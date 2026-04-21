"""FastAPI application for the runnable MVP scaffold."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Annotated, Any

from fastapi import Depends, FastAPI, Header, HTTPException, Query, status
from pydantic import BaseModel, Field

from .config import get_settings
from .logging_utils import configure_logging
from .service import WorldEngineService
from .storage import SessionStore

settings = get_settings()
store = SessionStore(settings.database_path)
service = WorldEngineService(store=store)


@asynccontextmanager
async def lifespan(_: FastAPI):
    configure_logging()
    yield


app = FastAPI(title="World of Shadows MVP v21", version="0.21.1", lifespan=lifespan)


class CreateSessionRequest(BaseModel):
    module_id: str = Field(default="god_of_carnage")


class ExecuteTurnRequest(BaseModel):
    player_input: str


class HealthResponse(BaseModel):
    status: str
    service: str
    storage_path: str


def require_internal_key(x_internal_api_key: Annotated[str | None, Header()] = None) -> None:
    if x_internal_api_key != settings.internal_api_key:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="internal auth required")


@app.get("/api/v1/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(
        status="ok",
        service="world-of-shadows-mvp-v21",
        storage_path=str(settings.database_path),
    )


@app.post("/api/v1/sessions")
def create_session(request: CreateSessionRequest) -> dict[str, Any]:
    try:
        return service.create_session(request.module_id)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@app.get("/api/v1/sessions/{session_id}")
def get_session(session_id: str) -> dict[str, Any]:
    result = service.get_session_player_view(session_id)
    if result is None:
        service.record_missing_session_incident(session_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="session not found")
    return result


@app.post("/api/v1/sessions/{session_id}/turns")
def execute_turn(session_id: str, request: ExecuteTurnRequest) -> dict[str, Any]:
    player_input = request.player_input.strip()
    if not player_input:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="player_input must not be empty")
    result = service.execute_turn(session_id, player_input)
    if result is None:
        service.record_missing_session_incident(session_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="session not found")
    return result


@app.get("/api/v1/sessions/{session_id}/state", dependencies=[Depends(require_internal_key)])
def get_state(session_id: str) -> dict[str, Any]:
    result = service.get_runtime_state(session_id)
    if result is None:
        service.record_missing_session_incident(session_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="session not found")
    return result


@app.get("/api/v1/sessions/{session_id}/logs", dependencies=[Depends(require_internal_key)])
def get_logs(session_id: str, limit: int = Query(default=100, ge=1, le=500)) -> dict[str, Any]:
    result = service.get_logs(session_id, limit=limit)
    if result is None:
        service.record_missing_session_incident(session_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="session not found")
    return result


@app.get("/api/v1/sessions/{session_id}/diagnostics", dependencies=[Depends(require_internal_key)])
def get_diagnostics(session_id: str) -> dict[str, Any]:
    result = service.get_diagnostics(session_id)
    if result is None:
        service.record_missing_session_incident(session_id)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="session not found")
    return result
