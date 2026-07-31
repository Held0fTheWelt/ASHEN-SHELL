"""Trace ID propagation for World Engine HTTP requests (aligned with backend X-WoS-Trace-Id)."""

from __future__ import annotations

import contextvars
import hashlib
import uuid
from contextvars import Token

TRACE_ID: contextvars.ContextVar[str | None] = contextvars.ContextVar("wos_we_trace_id", default=None)
LANGFUSE_TRACE_ID: contextvars.ContextVar[str | None] = contextvars.ContextVar("wos_we_langfuse_trace_id", default=None)


def set_trace_id(trace_id: str) -> Token:
    return TRACE_ID.set(trace_id)


def get_trace_id() -> str | None:
    return TRACE_ID.get()


def set_langfuse_trace_id(trace_id: str) -> Token:
    return LANGFUSE_TRACE_ID.set(trace_id)


def get_langfuse_trace_id() -> str | None:
    return LANGFUSE_TRACE_ID.get()


def reset_trace_id(token: Token) -> None:
    TRACE_ID.reset(token)


def ensure_trace_id(incoming: str | None) -> str:
    if incoming:
        set_trace_id(incoming)
        return incoming
    existing = get_trace_id()
    if existing:
        return existing
    new_id = str(uuid.uuid4())
    set_trace_id(new_id)
    return new_id


def _is_langfuse_trace_id(value: str) -> bool:
    return len(value) == 32 and all(ch in "0123456789abcdef" for ch in value)


def ensure_langfuse_trace_id(incoming: str | None, *, seed: str | None = None) -> str:
    if incoming:
        normalized = incoming.strip().lower()
        if _is_langfuse_trace_id(normalized):
            set_langfuse_trace_id(normalized)
            return normalized
    existing = get_langfuse_trace_id()
    if existing:
        return existing
    if seed:
        new_id = hashlib.sha256(seed.encode("utf-8")).hexdigest()[:32]
    else:
        new_id = uuid.uuid4().hex
    set_langfuse_trace_id(new_id)
    return new_id
