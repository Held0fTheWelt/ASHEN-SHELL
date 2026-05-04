"""HTTP middleware: accept/propagate X-WoS-Trace-Id across World Engine requests."""

from __future__ import annotations

from typing import Callable

from fastapi import FastAPI
from starlette.requests import Request
from starlette.responses import Response

from app.observability.trace import (
    LANGFUSE_TRACE_ID,
    TRACE_ID,
    ensure_langfuse_trace_id,
    ensure_trace_id,
    get_langfuse_trace_id,
    get_trace_id,
)


def install_trace_middleware(app: FastAPI) -> None:
    @app.middleware("http")
    async def wos_trace_middleware(request: Request, call_next: Callable[[Request], Response]) -> Response:
        token = TRACE_ID.set(None)
        langfuse_token = LANGFUSE_TRACE_ID.set(None)
        try:
            raw = request.headers.get("X-WoS-Trace-Id")
            incoming = raw.strip() if isinstance(raw, str) and raw.strip() else None
            trace_id = ensure_trace_id(incoming)
            raw_langfuse = request.headers.get("X-Langfuse-Trace-Id")
            incoming_langfuse = raw_langfuse.strip() if isinstance(raw_langfuse, str) and raw_langfuse.strip() else None
            langfuse_trace_id = ensure_langfuse_trace_id(incoming_langfuse, seed=trace_id)
            request.state.trace_id = trace_id
            request.state.langfuse_trace_id = langfuse_trace_id
            response = await call_next(request)
            response.headers["X-WoS-Trace-Id"] = get_trace_id() or trace_id
            response.headers["X-Langfuse-Trace-Id"] = get_langfuse_trace_id() or langfuse_trace_id
            return response
        finally:
            TRACE_ID.reset(token)
            LANGFUSE_TRACE_ID.reset(langfuse_token)
