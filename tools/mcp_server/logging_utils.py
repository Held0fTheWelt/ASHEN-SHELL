"""Structured logging helpers."""

import json
import sys
import time
from uuid import uuid4
from typing import Any


def generate_trace_id() -> str:
    """Generate UUID v4 trace ID."""
    return str(uuid4())


def log_request(trace_id: str, method: str, params: dict) -> None:
    """Log incoming JSON-RPC request."""
    entry = {
        "type": "request",
        "trace_id": trace_id,
        "timestamp": time.time(),
        "method": method,
        "params_keys": list(params.keys()) if params else [],
    }
    print(json.dumps(entry), file=sys.stderr)


def log_response(trace_id: str, method: str, status: str, duration_ms: float, error_code: str = None) -> None:
    """Log outgoing JSON-RPC response."""
    entry = {
        "type": "response",
        "trace_id": trace_id,
        "timestamp": time.time(),
        "method": method,
        "status": status,
        "duration_ms": round(duration_ms, 2),
    }
    if error_code:
        entry["error_code"] = error_code
    print(json.dumps(entry), file=sys.stderr)


def log_tool_call(trace_id: str, tool_name: str, duration_ms: float, status: str, error_code: str = None) -> None:
    """Log tool execution."""
    entry = {
        "type": "tool_call",
        "trace_id": trace_id,
        "timestamp": time.time(),
        "tool_name": tool_name,
        "duration_ms": round(duration_ms, 2),
        "status": status,
    }
    if error_code:
        entry["error_code"] = error_code
    print(json.dumps(entry), file=sys.stderr)
