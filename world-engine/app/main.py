from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path
import sys

import app.config  # noqa: F401 — load_dotenv so WOS_REPO_ROOT from .env is visible

from app.repo_root import resolve_wos_repo_root

REPO_ROOT = resolve_wos_repo_root(start=Path(__file__).resolve().parent)
if str(REPO_ROOT) not in sys.path:
    sys.path.append(str(REPO_ROOT))

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.http import router as http_router
from app.api.ws import router as ws_router
from app.auth.tickets import TicketManager
from app.config import (
    APP_TITLE,
    APP_VERSION,
    BACKEND_RUNTIME_CONFIG_URL,
    INTERNAL_RUNTIME_CONFIG_TOKEN,
    RUN_STORE_DIR,
    RUNTIME_CONFIG_FETCH_TIMEOUT_SECONDS,
    STORY_SESSION_STORE_DIR,
)
from app.middleware.trace_middleware import install_trace_middleware
from app.narrative.package_loader import NarrativePackageLoader
from app.narrative.preview_isolation import PreviewIsolationRegistry
from app.narrative.runtime_health import RuntimeHealthCounters
from app.narrative.validator_strategies import OutputValidatorConfig, ValidationStrategy
from app.runtime.manager import RuntimeManager
from app.runtime.runtime_config_client import fetch_resolved_runtime_config
from app.story_runtime import StoryRuntimeManager
from app.story_runtime.story_session_store import JsonStorySessionStore

WEB_ROOT = Path(__file__).resolve().parent / "web"


@asynccontextmanager
async def lifespan(app: FastAPI):
    resolved_runtime_config = fetch_resolved_runtime_config(
        base_url=BACKEND_RUNTIME_CONFIG_URL,
        token=INTERNAL_RUNTIME_CONFIG_TOKEN,
        timeout_seconds=RUNTIME_CONFIG_FETCH_TIMEOUT_SECONDS,
    )
    app.state.resolved_runtime_config = resolved_runtime_config
    app.state.manager = RuntimeManager(store_root=RUN_STORE_DIR, governed_runtime_config=resolved_runtime_config)
    app.state.story_manager = StoryRuntimeManager(
        session_store=JsonStorySessionStore(STORY_SESSION_STORE_DIR),
        governed_runtime_config=resolved_runtime_config,
    )
    app.state.ticket_manager = TicketManager()
    app.state.narrative_package_loader = NarrativePackageLoader(repo_root=REPO_ROOT)
    app.state.preview_isolation_registry = PreviewIsolationRegistry()
    app.state.narrative_runtime_health = RuntimeHealthCounters()
    world_engine_settings = (resolved_runtime_config or {}).get("world_engine_settings") or {}
    validation_mode = ((resolved_runtime_config or {}).get("validation_execution_mode") or "schema_plus_semantic").strip()
    strategy = ValidationStrategy.SCHEMA_PLUS_SEMANTIC
    if validation_mode == "schema_only":
        strategy = ValidationStrategy.SCHEMA_ONLY
    elif validation_mode == "strict_rule_engine":
        strategy = ValidationStrategy.SCHEMA_PLUS_SEMANTIC
    app.state.narrative_validator_config = OutputValidatorConfig(
        strategy=strategy,
        semantic_policy_check=validation_mode != "schema_only",
        enable_corrective_feedback=bool(world_engine_settings.get("enable_corrective_feedback", True)),
        max_retry_attempts=int(world_engine_settings.get("max_retry_attempts", 1)),
        fast_feedback_mode=True,
    )
    yield


app = FastAPI(title=APP_TITLE, version=APP_VERSION, lifespan=lifespan)
install_trace_middleware(app)
app.include_router(http_router)
app.include_router(ws_router)
app.mount("/static", StaticFiles(directory=WEB_ROOT / "static"), name="static")


@app.get("/")
def index() -> FileResponse:
    return FileResponse(WEB_ROOT / "templates" / "index.html")


@app.get("/ops")
def ops_console() -> FileResponse:
    """Minimal unauthenticated readiness view for operators (see UX plan: engine-near diagnosis)."""
    return FileResponse(WEB_ROOT / "templates" / "ops.html")
