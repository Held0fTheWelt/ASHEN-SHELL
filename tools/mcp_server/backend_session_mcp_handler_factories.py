"""Factory functions for backend session MCP tool handlers (DS-008)."""

from __future__ import annotations

import uuid
from typing import Any, Callable

from tools.mcp_server.backend_client import BackendClient
from tools.mcp_server.errors import JsonRpcError


def make_handle_system_health(backend: BackendClient) -> Callable[..., dict[str, Any]]:
    def handle_system_health(arguments: dict[str, Any]) -> dict[str, Any]:
        try:
            trace_id = str(uuid.uuid4())
            result = backend.health(trace_id=trace_id)
            return {"status": "healthy", "backend": result}
        except JsonRpcError as e:
            return {"status": "error", "message": e.message}

    return handle_system_health


def make_handle_session_create(backend: BackendClient) -> Callable[..., dict[str, Any]]:
    def handle_session_create(arguments: dict[str, Any]) -> dict[str, Any]:
        module_id = arguments.get("module_id")
        module_version = arguments.get("module_version")
        try:
            trace_id = str(uuid.uuid4())
            result = backend.create_session(
                module_id=module_id, trace_id=trace_id, module_version=module_version
            )
            return result
        except JsonRpcError as e:
            return {"error": e.message}

    return handle_session_create


def make_handle_session_get(backend: BackendClient) -> Callable[..., dict[str, Any]]:
    def handle_session_get(arguments: dict[str, Any]) -> dict[str, Any]:
        """Runtime-safe session snapshot (read-only, authority-respecting)."""
        session_id = arguments.get("session_id")
        if not session_id:
            return {"error": "session_id required"}
        try:
            trace_id = str(uuid.uuid4())
            result = backend._get(
                f"{backend.base_url}/api/v1/sessions/{session_id}",
                trace_id,
            )
            return result
        except JsonRpcError as e:
            return {"error": e.message}
        except Exception as e:
            return {"error": f"session_get failed: {str(e)}"}

    return handle_session_get


def make_handle_session_diag(backend: BackendClient) -> Callable[..., dict[str, Any]]:
    def handle_session_diag(arguments: dict[str, Any]) -> dict[str, Any]:
        """Runtime-safe session diagnostics (read-only, authority-respecting)."""
        session_id = arguments.get("session_id")
        if not session_id:
            return {"error": "session_id required"}
        try:
            trace_id = str(uuid.uuid4())
            result = backend._get(
                f"{backend.base_url}/api/v1/sessions/{session_id}/diagnostics",
                trace_id,
            )
            return result
        except JsonRpcError as e:
            return {"error": e.message}
        except Exception as e:
            return {"error": f"session_diag failed: {str(e)}"}

    return handle_session_diag


def make_handle_session_logs(backend: BackendClient) -> Callable[..., dict[str, Any]]:
    def handle_session_logs(arguments: dict[str, Any]) -> dict[str, Any]:
        """Session event logs (read-only, authority-respecting, audit surfaces)."""
        session_id = arguments.get("session_id")
        limit = arguments.get("limit", 100)
        if not session_id:
            return {"error": "session_id required"}
        try:
            trace_id = str(uuid.uuid4())
            result = backend._get(
                f"{backend.base_url}/api/v1/sessions/{session_id}/logs?limit={limit}",
                trace_id,
            )
            return result
        except JsonRpcError as e:
            return {"error": e.message}
        except Exception as e:
            return {"error": f"session_logs failed: {str(e)}"}

    return handle_session_logs


def make_handle_session_state(backend: BackendClient) -> Callable[..., dict[str, Any]]:
    def handle_session_state(arguments: dict[str, Any]) -> dict[str, Any]:
        """Session state snapshot (read-only, authority-respecting, runtime state machine)."""
        session_id = arguments.get("session_id")
        if not session_id:
            return {"error": "session_id required"}
        try:
            trace_id = str(uuid.uuid4())
            result = backend._get(
                f"{backend.base_url}/api/v1/sessions/{session_id}/state",
                trace_id,
            )
            return result
        except JsonRpcError as e:
            return {"error": e.message}
        except Exception as e:
            return {"error": f"session_state failed: {str(e)}"}

    return handle_session_state


def make_handle_session_execute_turn(backend: BackendClient) -> Callable[..., dict[str, Any]]:
    def handle_session_execute_turn(arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute turn in session (review-bound, proxies POST /sessions/{id}/turns → world-engine)."""
        session_id = arguments.get("session_id")
        player_input = (
            (arguments.get("player_input") or arguments.get("prompt") or arguments.get("input") or "")
            .strip()
        )
        if not session_id:
            return {"error": "session_id required"}
        if not player_input:
            return {"error": "player_input or prompt is required"}
        try:
            trace_id = str(uuid.uuid4())
            result = backend._post(
                f"{backend.base_url}/api/v1/sessions/{session_id}/turns",
                trace_id,
                json={"player_input": player_input},
            )
            return result
        except JsonRpcError as e:
            return {"error": e.message}
        except Exception as e:
            return {"error": f"session_execute_turn failed: {str(e)}"}

    return handle_session_execute_turn
