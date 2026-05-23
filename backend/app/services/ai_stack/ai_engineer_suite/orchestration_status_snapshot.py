"""Status snapshot assembly for AI orchestration diagnostics."""

from __future__ import annotations

from collections import Counter
from typing import Any

from .common import (
    LANGGRAPH_RUNTIME_EXPORT_AVAILABLE,
    STATUS_SEMANTICS,
    GameServiceError,
    _RUNTIME_PROFILE_ALLOWED,
    _VERBOSITY_ALLOWED,
    get_runtime_modes,
    get_story_diagnostics,
    list_story_sessions,
    read_scope_settings,
)
from .settings_validation import _extract_parser_errors, _extract_values


def _langgraph_dependency_status() -> tuple[bool, str | None]:
    dependency_available = bool(LANGGRAPH_RUNTIME_EXPORT_AVAILABLE)
    if dependency_available:
        return True, None
    try:
        from ai_stack.langgraph.langgraph_runtime import ensure_langgraph_available

        ensure_langgraph_available()
        return True, None
    except Exception as exc:  # pragma: no cover - environment dependent
        return False, str(exc)


def _langchain_bridge_status() -> tuple[bool, str | None, dict[str, bool]]:
    parser_schema_health = {"runtime_structured_output": True, "writers_room_structured_output": True}
    try:
        from ai_stack.langchain import RuntimeTurnStructuredOutput, WritersRoomStructuredOutput

        RuntimeTurnStructuredOutput.model_validate_json('{"narrative_response":"ok"}')
        WritersRoomStructuredOutput.model_validate_json('{"review_notes":"ok","recommendations":[]}')
        return True, None, parser_schema_health
    except Exception as exc:  # pragma: no cover - dependency/runtime dependent
        return False, str(exc), {"runtime_structured_output": False, "writers_room_structured_output": False}


def _recent_diagnostics_summary(trace_id: str | None) -> dict[str, Any]:
    session_items: list[dict[str, Any]] = []
    diagnostics_errors: list[dict[str, Any]] = []
    node_counter: Counter[str] = Counter()
    graph_error_count = 0
    fallback_marker_count = 0
    parser_error_count = 0

    try:
        sessions_payload = list_story_sessions(trace_id=trace_id)
        for row in list(sessions_payload.get("items") or [])[:3]:
            if not isinstance(row, dict):
                continue
            session_id = str(row.get("session_id") or "").strip()
            if not session_id:
                continue
            try:
                diag = get_story_diagnostics(session_id, trace_id=trace_id)
                session_items.append({"session_id": session_id, "diagnostics": diag})
                node_counter.update(_node_names(diag))
                graph_error_count += _list_value_count(diag, "graph_errors")
                fallback_marker_count += _list_value_count(diag, "fallback_markers")
                parser_error_count += len(_extract_parser_errors(diag))
            except GameServiceError as exc:
                diagnostics_errors.append({"session_id": session_id, "message": str(exc), "status_code": exc.status_code})
    except GameServiceError as exc:
        diagnostics_errors.append({"session_id": None, "message": str(exc), "status_code": exc.status_code})

    return {
        "session_items": session_items,
        "diagnostics_errors": diagnostics_errors,
        "graph_error_count": graph_error_count,
        "fallback_marker_count": fallback_marker_count,
        "parser_error_count": parser_error_count,
        "top_nodes_executed": node_counter.most_common(8),
    }


def _node_names(payload: Any) -> list[str]:
    names: list[str] = []
    for nodes in _extract_values(payload, "nodes_executed"):
        if isinstance(nodes, list):
            names.extend(node_name for node_name in nodes if isinstance(node_name, str) and node_name)
    return names


def _list_value_count(payload: Any, key: str) -> int:
    total = 0
    for values in _extract_values(payload, key):
        if isinstance(values, list):
            total += len(values)
    return total


def _state_from_signals(*, blocked: bool, degraded: bool) -> str:
    if blocked:
        return "blocked"
    if degraded:
        return "degraded"
    return "healthy"


def _guidance_rows(
    *,
    dependency_available: bool,
    parser_error_count: int,
    diagnostics_verbosity: str,
) -> list[dict[str, str]]:
    guidance: list[dict[str, str]] = []
    if not dependency_available:
        guidance.append(
            {
                "severity": "blocked",
                "message": "LangGraph dependency/runtime export is unavailable.",
                "consequence": "Primary graph execution cannot run as expected.",
                "next_step": "Review orchestration diagnostics and fallback posture before enabling strict runtime paths.",
                "fix_path": "/manage/ai-orchestration",
            }
        )
    if parser_error_count > 0:
        guidance.append(
            {
                "severity": "degraded",
                "message": "Recent parser/schema failures were observed.",
                "consequence": "Structured orchestration output reliability is reduced.",
                "next_step": "Keep corrective feedback enabled and inspect recent diagnostics errors.",
                "fix_path": "/manage/ai-orchestration",
            }
        )
    if diagnostics_verbosity == "debug":
        guidance.append(
            {
                "severity": "info",
                "message": "Diagnostics verbosity is set to debug (bounded debug-only posture).",
                "consequence": "Operator output can become noisy during normal operation.",
                "next_step": "Return to operator or detailed verbosity when troubleshooting is complete.",
                "fix_path": "/manage/runtime-settings",
            }
        )
    return guidance


def build_orchestration_status_snapshot(*, trace_id: str | None = None) -> dict[str, Any]:
    """Build the orchestration status payload returned by the admin service."""
    runtime_modes = get_runtime_modes()
    world_engine_settings = read_scope_settings("world_engine")
    dependency_available, langgraph_import_error = _langgraph_dependency_status()
    bridge_available, bridge_error, parser_schema_health = _langchain_bridge_status()
    diagnostics = _recent_diagnostics_summary(trace_id)

    langgraph_state = _state_from_signals(
        blocked=not dependency_available,
        degraded=(
            diagnostics["graph_error_count"] > 0
            or diagnostics["fallback_marker_count"] > 0
            or bool(diagnostics["diagnostics_errors"])
        ),
    )
    langchain_state = _state_from_signals(
        blocked=not bridge_available,
        degraded=diagnostics["parser_error_count"] > 0,
    )
    overall_state = _state_from_signals(
        blocked="blocked" in {langgraph_state, langchain_state},
        degraded="degraded" in {langgraph_state, langchain_state},
    )
    diagnostics_verbosity = world_engine_settings.get("runtime_diagnostics_verbosity", "operator")

    return {
        "overall_state": overall_state,
        "status_semantics": STATUS_SEMANTICS,
        "langgraph": _langgraph_payload(
            runtime_modes,
            world_engine_settings,
            dependency_available,
            langgraph_import_error,
            langgraph_state,
            diagnostics,
        ),
        "langchain": _langchain_payload(bridge_available, bridge_error, parser_schema_health, diagnostics),
        "controls": {
            "allowed_runtime_profiles": sorted(_RUNTIME_PROFILE_ALLOWED),
            "allowed_runtime_diagnostics_verbosity": sorted(_VERBOSITY_ALLOWED),
            "max_retry_attempts_range": {"min": 0, "max": 5},
        },
        "comparison": _comparison_payload(runtime_modes, world_engine_settings, diagnostics),
        "guidance": _guidance_rows(
            dependency_available=dependency_available,
            parser_error_count=diagnostics["parser_error_count"],
            diagnostics_verbosity=str(diagnostics_verbosity),
        ),
    }


def _langgraph_payload(
    runtime_modes: dict[str, Any],
    world_engine_settings: dict[str, Any],
    dependency_available: bool,
    import_error: str | None,
    state: str,
    diagnostics: dict[str, Any],
) -> dict[str, Any]:
    return {
        "state": state,
        "dependency_available": dependency_available,
        "import_error": import_error,
        "runtime_profile": runtime_modes.get("runtime_profile"),
        "validation_execution_mode": runtime_modes.get("validation_execution_mode"),
        "max_retry_attempts": world_engine_settings.get("max_retry_attempts", 1),
        "enable_corrective_feedback": bool(world_engine_settings.get("enable_corrective_feedback", True)),
        "runtime_diagnostics_verbosity": world_engine_settings.get("runtime_diagnostics_verbosity", "operator"),
        "fallback_posture": {
            "fallback_marker_count_recent": diagnostics["fallback_marker_count"],
            "graph_error_count_recent": diagnostics["graph_error_count"],
        },
        "recent_execution_summary": {
            "sessions_sampled": len(diagnostics["session_items"]),
            "top_nodes_executed": diagnostics["top_nodes_executed"],
            "diagnostics_errors": diagnostics["diagnostics_errors"],
        },
    }


def _langchain_payload(
    bridge_available: bool,
    bridge_error: str | None,
    parser_schema_health: dict[str, bool],
    diagnostics: dict[str, Any],
) -> dict[str, Any]:
    return {
        "state": _state_from_signals(blocked=not bridge_available, degraded=diagnostics["parser_error_count"] > 0),
        "bridge_available": bridge_available,
        "bridge_error": bridge_error,
        "runtime_adapter_bridge_available": bridge_available,
        "retriever_bridge_available": bridge_available,
        "writers_room_bridge_available": bridge_available,
        "tool_bridge_available": bridge_available,
        "parser_schema_health": parser_schema_health,
        "recent_parser_failure_count": diagnostics["parser_error_count"],
    }


def _comparison_payload(
    runtime_modes: dict[str, Any],
    world_engine_settings: dict[str, Any],
    diagnostics: dict[str, Any],
) -> dict[str, Any]:
    return {
        "expected_healthy": {
            "langgraph_dependency_available": True,
            "langchain_bridge_available": True,
            "recent_graph_errors": 0,
            "recent_parser_failures": 0,
        },
        "active": {
            "runtime_profile": runtime_modes.get("runtime_profile"),
            "runtime_diagnostics_verbosity": world_engine_settings.get("runtime_diagnostics_verbosity", "operator"),
            "max_retry_attempts": world_engine_settings.get("max_retry_attempts", 1),
            "recent_graph_errors": diagnostics["graph_error_count"],
            "recent_parser_failures": diagnostics["parser_error_count"],
        },
    }
