from __future__ import annotations

import os
from contextlib import asynccontextmanager
from pathlib import Path
import sys
from typing import Any
from urllib.parse import parse_qs, quote, urlsplit

import app.config  # noqa: F401 — load_dotenv so WOS_REPO_ROOT from .env is visible

from app.repo_root import resolve_wos_repo_root

REPO_ROOT = resolve_wos_repo_root(start=Path(__file__).resolve().parent)
if str(REPO_ROOT) not in sys.path:
    sys.path.append(str(REPO_ROOT))

try:
    from ai_stack.langchain.langchain_reviver_compat import ensure_langchain_reviver_explicit_core

    ensure_langchain_reviver_explicit_core()
except ImportError:
    pass
from ai_stack.prompt_store import configure_prompt_bundle

from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette import status as http_status
from starlette.concurrency import run_in_threadpool
from starlette.middleware.sessions import SessionMiddleware
import httpx

from app.api.http import router as http_router
from app.api.story_ws import story_ws_router, story_ws_support_router
from app.api.ws import router as ws_router
from app.auth.tickets import TicketManager
from app.ui_backend_proxy import backend_proxy_response, user_capabilities
from app.config import (
    APP_TITLE,
    APP_VERSION,
    BACKEND_RUNTIME_CONFIG_URL,
    BRANCH_TIMELINE_STORE_DIR,
    BRANCHING_TREE_STORE_DIR,
    CALLBACK_WEB_STORE_DIR,
    CONSEQUENCE_CASCADE_STORE_DIR,
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
from app.runtime.json_at_rest import JsonAtRestCodec
from app.runtime.manager import RuntimeManager
from app.runtime.runtime_config_client import (
    fetch_hf_hub_token_from_backend,
    fetch_resolved_runtime_config,
)
from app.story_runtime import StoryRuntimeManager
from app.story_runtime.branch_timeline_store import JsonBranchTimelineStore
from app.story_runtime.branching_tree_store import JsonBranchingTreeStore
from app.story_runtime.callback_web_store import JsonCallbackWebStore
from app.story_runtime.consequence_cascade_store import JsonConsequenceCascadeStore
from app.story_runtime.story_session_store import JsonStorySessionStore

WEB_ROOT = Path(__file__).resolve().parent / "web"
TEMPLATES = Jinja2Templates(directory=str(WEB_ROOT / "templates"))
AUTH_LOGIN_PATH = "/api/v1/auth/login"
AUTH_ME_PATH = "/api/v1/auth/me"
SESSION_KEY_ACCESS_TOKEN = "world_engine_access_token"
SESSION_KEY_REFRESH_TOKEN = "world_engine_refresh_token"
SESSION_KEY_CURRENT_USER = "world_engine_current_user"
WORLD_ENGINE_UI_PAGES = (
    ("/dashboard", "ui/dashboard.html", "dashboard"),
    ("/runs-sessions", "ui/runs_sessions.html", "runs-sessions"),
    ("/live-runtime", "ui/live_runtime.html", "live-runtime"),
    ("/validation-authority", "ui/validation_authority.html", "validation-authority"),
    ("/runtime-ledger", "ui/runtime_ledger.html", "runtime-ledger"),
    ("/narrative-systems", "ui/narrative_systems.html", "narrative-systems"),
    ("/traces", "ui/traces_observability.html", "traces"),
    ("/history", "ui/history_events.html", "history"),
    ("/runtime-status", "ui/health.html", "runtime-status"),
    ("/health", "ui/health.html", "runtime-status"),
    ("/engine", "ui/engine.html", "engine"),
)


def _ui_session_secret() -> str:
    """Resolve a dedicated UI session secret without embedding credentials in templates/JS."""
    secret = (
        os.getenv("WORLD_ENGINE_UI_SESSION_SECRET")
        or os.getenv("PLAY_SERVICE_SECRET")
        or os.getenv("PLAY_SERVICE_SHARED_SECRET")
        or ""
    ).strip()
    if secret:
        return secret
    if os.getenv("FLASK_ENV") == "test":
        return "world-engine-ui-test-secret"
    raise RuntimeError(
        "WORLD_ENGINE_UI_SESSION_SECRET or PLAY_SERVICE_SECRET must be configured for the World-Engine UI."
    )


def _backend_base_url() -> str:
    return (BACKEND_RUNTIME_CONFIG_URL or "").strip().rstrip("/")


def _safe_next_path(raw_next: str | None, default: str = "/dashboard") -> str:
    candidate = (raw_next or "").strip()
    if not candidate:
        return default
    if not candidate.startswith("/") or candidate.startswith("//"):
        return default
    parsed = urlsplit(candidate)
    if parsed.scheme or parsed.netloc:
        return default
    if candidate.startswith("/login"):
        return default
    return candidate


def _clear_ui_session(request: Request) -> None:
    request.session.pop(SESSION_KEY_ACCESS_TOKEN, None)
    request.session.pop(SESSION_KEY_REFRESH_TOKEN, None)
    request.session.pop(SESSION_KEY_CURRENT_USER, None)


def _backend_login(username: str, password: str) -> tuple[bool, dict[str, Any], int]:
    base_url = _backend_base_url()
    if not base_url:
        return False, {"message": "Backend authentication service is not configured."}, http_status.HTTP_503_SERVICE_UNAVAILABLE
    try:
        with httpx.Client(timeout=6.0) as client:
            response = client.post(
                f"{base_url}{AUTH_LOGIN_PATH}",
                json={"username": username, "password": password},
                headers={"Accept": "application/json"},
            )
    except httpx.HTTPError:
        return False, {"message": "Authentication service is currently unavailable."}, http_status.HTTP_503_SERVICE_UNAVAILABLE

    try:
        payload = response.json()
    except ValueError:
        payload = {}

    if response.status_code >= http_status.HTTP_400_BAD_REQUEST:
        return False, payload if isinstance(payload, dict) else {}, response.status_code
    return True, payload if isinstance(payload, dict) else {}, response.status_code


def _backend_fetch_user(access_token: str) -> tuple[bool, dict[str, Any], int]:
    base_url = _backend_base_url()
    if not base_url:
        return False, {"message": "Backend authentication service is not configured."}, http_status.HTTP_503_SERVICE_UNAVAILABLE
    try:
        with httpx.Client(timeout=6.0) as client:
            response = client.get(
                f"{base_url}{AUTH_ME_PATH}",
                headers={"Authorization": f"Bearer {access_token}", "Accept": "application/json"},
            )
    except httpx.HTTPError:
        return False, {"message": "Authentication service is currently unavailable."}, http_status.HTTP_503_SERVICE_UNAVAILABLE

    try:
        payload = response.json()
    except ValueError:
        payload = {}

    if response.status_code >= http_status.HTTP_400_BAD_REQUEST:
        return False, payload if isinstance(payload, dict) else {}, response.status_code
    return True, payload if isinstance(payload, dict) else {}, response.status_code


def _login_redirect(request: Request) -> RedirectResponse:
    next_path = quote(request.url.path, safe="/")
    return RedirectResponse(url=f"/login?next={next_path}", status_code=http_status.HTTP_303_SEE_OTHER)


def _authenticated_user_or_redirect(request: Request) -> tuple[dict[str, Any] | None, RedirectResponse | None]:
    access_token = request.session.get(SESSION_KEY_ACCESS_TOKEN)
    if not access_token:
        return None, _login_redirect(request)
    ok, payload, status = _backend_fetch_user(str(access_token))
    if not ok:
        _clear_ui_session(request)
        redirect = _login_redirect(request)
        if status == http_status.HTTP_503_SERVICE_UNAVAILABLE:
            # Service unavailable is treated as unauthenticated in the UI boundary.
            return None, redirect
        return None, redirect
    request.session[SESSION_KEY_CURRENT_USER] = payload
    return payload, None


async def _extract_login_credentials(request: Request) -> tuple[str, str]:
    content_type = (request.headers.get("content-type") or "").lower()
    if "application/json" in content_type:
        payload = await request.json()
        if not isinstance(payload, dict):
            return "", ""
        return str(payload.get("username") or "").strip(), str(payload.get("password") or "")

    raw_body = (await request.body()).decode("utf-8", errors="ignore")
    parsed = parse_qs(raw_body, keep_blank_values=True)
    username = (parsed.get("username", [""])[0] or "").strip()
    password = parsed.get("password", [""])[0] or ""
    return username, password


def _render_login_page(
    request: Request,
    *,
    error: str | None = None,
    status_code: int = http_status.HTTP_200_OK,
):
    safe_next = _safe_next_path(request.query_params.get("next"))
    return TEMPLATES.TemplateResponse(
        request=request,
        name="ui/login.html",
        context={
            "error_message": error,
            "next_path": safe_next,
        },
        status_code=status_code,
    )


def _ui_page_context(request: Request, current_user: dict[str, Any], *, active_page: str) -> dict[str, Any]:
    caps = user_capabilities(current_user)
    return {
        "current_user": current_user,
        "active_page": active_page,
        "ui_capabilities": caps,
    }


def _render_ui_page(
    request: Request,
    *,
    template_name: str,
    active_page: str,
    extra_context: dict[str, Any] | None = None,
):
    current_user, redirect = _authenticated_user_or_redirect(request)
    if redirect is not None:
        return redirect
    context = _ui_page_context(request, current_user or {}, active_page=active_page)
    if extra_context:
        context.update(extra_context)
    return TEMPLATES.TemplateResponse(
        request=request,
        name=template_name,
        context=context,
    )


def _register_world_engine_entry_routes(app: FastAPI, *, ui_root: Path) -> None:
    @app.get("/favicon.ico", include_in_schema=False)
    def favicon():
        return FileResponse(ui_root / "static" / "favicon.ico", media_type="image/vnd.microsoft.icon")

    @app.get("/")
    def root_entry(request: Request):
        if request.session.get(SESSION_KEY_ACCESS_TOKEN):
            return RedirectResponse(url="/dashboard", status_code=http_status.HTTP_303_SEE_OTHER)
        return RedirectResponse(url="/login", status_code=http_status.HTTP_303_SEE_OTHER)


def _register_world_engine_auth_routes(app: FastAPI) -> None:

    @app.get("/login")
    def login_page(request: Request):
        if request.session.get(SESSION_KEY_ACCESS_TOKEN):
            return RedirectResponse(url="/dashboard", status_code=http_status.HTTP_303_SEE_OTHER)
        return _render_login_page(request)

    @app.post("/login")
    async def login_submit(request: Request):
        username, password = await _extract_login_credentials(request)
        next_path = _safe_next_path(request.query_params.get("next"))
        if not username or not password:
            return _render_login_page(
                request,
                error="Username and password are required.",
                status_code=http_status.HTTP_400_BAD_REQUEST,
            )

        ok, payload, status = await run_in_threadpool(_backend_login, username, password)
        if not ok:
            # Return a generic/safe message; never expose internals.
            if status == http_status.HTTP_401_UNAUTHORIZED:
                error = "Invalid username or password."
            elif status == http_status.HTTP_503_SERVICE_UNAVAILABLE:
                error = "Authentication service is temporarily unavailable."
            else:
                error = "Login failed."
            status_code = (
                http_status.HTTP_401_UNAUTHORIZED
                if status == http_status.HTTP_401_UNAUTHORIZED
                else http_status.HTTP_400_BAD_REQUEST
            )
            return _render_login_page(request, error=error, status_code=status_code)

        access_token = str(payload.get("access_token") or "").strip()
        refresh_token = str(payload.get("refresh_token") or "").strip()
        if not access_token:
            return _render_login_page(
                request,
                error="Login failed.",
                status_code=http_status.HTTP_400_BAD_REQUEST,
            )

        request.session[SESSION_KEY_ACCESS_TOKEN] = access_token
        request.session[SESSION_KEY_REFRESH_TOKEN] = refresh_token
        me_ok, me_payload, _me_status = await run_in_threadpool(_backend_fetch_user, access_token)
        request.session[SESSION_KEY_CURRENT_USER] = me_payload if me_ok else (payload.get("user") or {})
        return RedirectResponse(url=next_path, status_code=http_status.HTTP_303_SEE_OTHER)

    @app.post("/logout")
    def logout(request: Request):
        _clear_ui_session(request)
        return RedirectResponse(url="/login", status_code=http_status.HTTP_303_SEE_OTHER)


def _register_world_engine_backend_proxy(app: FastAPI) -> None:
    @app.api_route("/ui-api/{backend_path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
    async def ui_backend_api_proxy(request: Request, backend_path: str):
        """Same-origin proxy to backend ``/api/v1/*`` using the UI session JWT."""
        if not request.session.get(SESSION_KEY_ACCESS_TOKEN):
            return JSONResponse(
                {"error": "Authentication required."},
                status_code=http_status.HTTP_401_UNAUTHORIZED,
            )
        return await backend_proxy_response(request, backend_path)


def _register_rendered_ui_page(app: FastAPI, *, path: str, template_name: str, active_page: str) -> None:
    route_name = f"ui_{active_page.replace('-', '_')}_{path.strip('/').replace('/', '_')}"

    @app.get(path, name=route_name)
    def rendered_ui_page(request: Request):
        return _render_ui_page(request, template_name=template_name, active_page=active_page)


def _register_world_engine_page_routes(app: FastAPI, *, ui_root: Path) -> None:
    for path, template_name, active_page in WORLD_ENGINE_UI_PAGES:
        _register_rendered_ui_page(
            app,
            path=path,
            template_name=template_name,
            active_page=active_page,
        )

    @app.get("/diagnostics")
    def diagnostics(request: Request):
        return RedirectResponse(url="/health", status_code=http_status.HTTP_303_SEE_OTHER)

    @app.get("/engine/app")
    def legacy_engine_page(request: Request):
        _current_user, redirect = _authenticated_user_or_redirect(request)
        if redirect is not None:
            return redirect
        return FileResponse(ui_root / "templates" / "index.html")


def register_world_engine_ui_routes(app: FastAPI, *, web_root: Path | None = None) -> None:
    ui_root = web_root or WEB_ROOT
    _register_world_engine_entry_routes(app, ui_root=ui_root)
    _register_world_engine_auth_routes(app)
    _register_world_engine_backend_proxy(app)
    _register_world_engine_page_routes(app, ui_root=ui_root)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize Langfuse tracing adapter at startup
    try:
        from app.observability.langfuse_adapter import LangfuseAdapter
        adapter = LangfuseAdapter.get_instance()
        if adapter.is_ready:
            print(f"[INFO] Langfuse observability initialized: ready={adapter.is_ready}")
        else:
            print(f"[INFO] Langfuse observability adapter loaded (ready={adapter.is_ready})")
    except Exception as e:
        print(f"[WARN] Failed to initialize Langfuse adapter: {e}")

    resolved_runtime_config = fetch_resolved_runtime_config(
        base_url=BACKEND_RUNTIME_CONFIG_URL,
        token=INTERNAL_RUNTIME_CONFIG_TOKEN,
        timeout_seconds=RUNTIME_CONFIG_FETCH_TIMEOUT_SECONDS,
    )
    configure_prompt_bundle((resolved_runtime_config or {}).get("prompt_store"))
    try:
        hf_tok = fetch_hf_hub_token_from_backend(
            base_url=BACKEND_RUNTIME_CONFIG_URL,
            token=INTERNAL_RUNTIME_CONFIG_TOKEN,
            timeout_seconds=RUNTIME_CONFIG_FETCH_TIMEOUT_SECONDS,
        )
        if hf_tok:
            os.environ["HF_TOKEN"] = hf_tok
            print("[INFO] HF_TOKEN synced from backend Hugging Face Hub governance store")
    except Exception as exc:
        print(f"[WARN] Could not sync HF_TOKEN from backend: {exc}")

    app.state.resolved_runtime_config = resolved_runtime_config
    json_at_rest_codec = JsonAtRestCodec.from_env()
    runtime_manager = RuntimeManager(store_root=RUN_STORE_DIR, governed_runtime_config=resolved_runtime_config)
    story_manager = StoryRuntimeManager(
        session_store=JsonStorySessionStore(STORY_SESSION_STORE_DIR, codec=json_at_rest_codec),
        branching_tree_store=JsonBranchingTreeStore(BRANCHING_TREE_STORE_DIR, codec=json_at_rest_codec),
        branch_timeline_store=JsonBranchTimelineStore(BRANCH_TIMELINE_STORE_DIR, codec=json_at_rest_codec),
        callback_web_store=JsonCallbackWebStore(CALLBACK_WEB_STORE_DIR, codec=json_at_rest_codec),
        consequence_cascade_store=JsonConsequenceCascadeStore(CONSEQUENCE_CASCADE_STORE_DIR, codec=json_at_rest_codec),
        governed_runtime_config=resolved_runtime_config,
    )
    runtime_manager.attach_story_manager(story_manager)
    app.state.manager = runtime_manager
    app.state.story_manager = story_manager
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
app.add_middleware(
    SessionMiddleware,
    secret_key=_ui_session_secret(),
    same_site="lax",
    https_only=(os.getenv("FLASK_ENV") in {"production", "staging"} or os.getenv("ENV") in {"production", "staging"}),
)
app.include_router(http_router)
app.include_router(ws_router)
app.include_router(story_ws_router)
app.include_router(story_ws_support_router)
app.mount("/static", StaticFiles(directory=WEB_ROOT / "static"), name="static")
register_world_engine_ui_routes(app)


@app.get("/ops")
def ops_console(request: Request):
    """Legacy ops health view; requires authenticated UI session (no public diagnostics)."""
    _current_user, redirect = _authenticated_user_or_redirect(request)
    if redirect is not None:
        return redirect
    return FileResponse(WEB_ROOT / "templates" / "ops.html")
