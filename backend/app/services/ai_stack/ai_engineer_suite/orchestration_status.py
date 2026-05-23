"""LangGraph and LangChain orchestration status and settings functions."""

from __future__ import annotations

from .common import *
from .orchestration_status_snapshot import build_orchestration_status_snapshot
from .settings_validation import *

def get_orchestration_status(*, trace_id: str | None = None) -> dict[str, Any]:
    return build_orchestration_status_snapshot(trace_id=trace_id)


def get_orchestration_settings() -> dict[str, Any]:
    runtime_modes = get_runtime_modes()
    world_engine_settings = read_scope_settings("world_engine")
    return {
        "runtime_profile": runtime_modes.get("runtime_profile"),
        "enable_corrective_feedback": bool(world_engine_settings.get("enable_corrective_feedback", True)),
        "runtime_diagnostics_verbosity": world_engine_settings.get("runtime_diagnostics_verbosity", "operator"),
        "max_retry_attempts": world_engine_settings.get("max_retry_attempts", 1),
    }


def update_orchestration_settings(payload: dict[str, Any], actor: str) -> dict[str, Any]:
    modes_patch, world_engine_patch = _validate_orchestration_settings_patch(payload)
    if modes_patch:
        update_runtime_modes(modes_patch, actor)
    if world_engine_patch:
        update_scope_settings("world_engine", world_engine_patch, actor)
    return get_orchestration_settings()


__all__ = (
    'get_orchestration_status',
    'get_orchestration_settings',
    'update_orchestration_settings',
)
