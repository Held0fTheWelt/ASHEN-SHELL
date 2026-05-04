"""Trace ID system using contextvars for request and non-request contexts."""

import contextvars
import hashlib
import uuid

# Context variable stores trace_id across request and non-request code paths
TRACE_ID: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "trace_id", default=None
)
LANGFUSE_TRACE_ID: contextvars.ContextVar[str | None] = contextvars.ContextVar(
    "langfuse_trace_id", default=None
)


def set_trace_id(trace_id: str) -> contextvars.Token:
    """Set trace_id in the current context and return the token for reset."""
    return TRACE_ID.set(trace_id)


def get_trace_id() -> str | None:
    """Get trace_id from the current context, or None if not set."""
    return TRACE_ID.get()


def set_langfuse_trace_id(trace_id: str) -> contextvars.Token:
    """Set the Langfuse trace ID in the current context."""
    return LANGFUSE_TRACE_ID.set(trace_id)


def get_langfuse_trace_id() -> str | None:
    """Get the Langfuse trace ID from the current context."""
    return LANGFUSE_TRACE_ID.get()


def reset_trace_id(token: contextvars.Token) -> None:
    """Reset trace_id using the token returned by set_trace_id."""
    TRACE_ID.reset(token)


def ensure_trace_id(incoming: str | None) -> str:
    """Idempotent trace_id getter/setter.

    If incoming is provided, set it and return it.
    If incoming is None and contextvar is already set, return existing value.
    If incoming is None and contextvar not set, generate UUIDv4, set it, return it.

    Args:
        incoming: Incoming trace_id from request header (or None)

    Returns:
        trace_id: The trace_id to use for this request/execution
    """
    if incoming:
        # Incoming value takes precedence
        set_trace_id(incoming)
        return incoming

    # Check if already set in contextvar
    existing = get_trace_id()
    if existing:
        return existing

    # Generate new UUID
    new_trace_id = str(uuid.uuid4())
    set_trace_id(new_trace_id)
    return new_trace_id


def _is_langfuse_trace_id(value: str) -> bool:
    return len(value) == 32 and all(ch in "0123456789abcdef" for ch in value)


def create_langfuse_trace_id(seed: str | None = None) -> str:
    """Create a Langfuse v4-compatible 32 lowercase hex trace ID."""
    if seed:
        return hashlib.sha256(seed.encode("utf-8")).hexdigest()[:32]
    return uuid.uuid4().hex


def ensure_langfuse_trace_id(incoming: str | None, *, seed: str | None = None) -> str:
    """Idempotently propagate or create a Langfuse-compatible trace ID."""
    if incoming:
        normalized = incoming.strip().lower()
        if _is_langfuse_trace_id(normalized):
            set_langfuse_trace_id(normalized)
            return normalized

    existing = get_langfuse_trace_id()
    if existing:
        return existing

    new_trace_id = create_langfuse_trace_id(seed)
    set_langfuse_trace_id(new_trace_id)
    return new_trace_id
