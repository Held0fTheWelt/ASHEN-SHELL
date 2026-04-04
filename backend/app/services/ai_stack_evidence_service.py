"""Aggregate AI-stack evidence for governance (World-Engine diagnostics + backend session truth)."""

from __future__ import annotations

from typing import Any

from app.runtime.session_store import get_session as get_runtime_session
from app.services.game_service import GameServiceError, get_story_diagnostics, get_story_state
from app.services.improvement_service import list_recommendation_packages


def build_session_evidence_bundle(*, session_id: str, trace_id: str) -> dict[str, Any]:
    """Return inspectable evidence for a backend runtime session (may include World-Engine story host data)."""
    runtime_session = get_runtime_session(session_id)
    if not runtime_session:
        return {
            "trace_id": trace_id,
            "error": "backend_session_not_found",
            "session_id": session_id,
        }

    state = runtime_session.current_runtime_state
    metadata = state.metadata if isinstance(state.metadata, dict) else {}
    engine_id = metadata.get("world_engine_story_session_id")

    bundle: dict[str, Any] = {
        "trace_id": trace_id,
        "canonical_flow": "governance_session_evidence_bundle",
        "backend_session_id": session_id,
        "module_id": state.module_id,
        "current_scene_id": state.current_scene_id,
        "turn_counter_backend": state.turn_counter,
        "world_engine_story_session_id": engine_id,
        "world_engine_state": None,
        "world_engine_diagnostics": None,
        "bridge_errors": [],
        "improvement_recommendation_count": len(list_recommendation_packages()),
    }

    if isinstance(engine_id, str) and engine_id.strip():
        try:
            bundle["world_engine_state"] = get_story_state(engine_id, trace_id=trace_id)
            bundle["world_engine_diagnostics"] = get_story_diagnostics(engine_id, trace_id=trace_id)
        except GameServiceError as exc:
            bundle["bridge_errors"].append(
                {
                    "failure_class": "world_engine_unreachable",
                    "message": str(exc),
                    "status_code": exc.status_code,
                }
            )

    last_diag = bundle.get("world_engine_diagnostics") or {}
    diag_list = last_diag.get("diagnostics") if isinstance(last_diag, dict) else None
    if isinstance(diag_list, list) and diag_list:
        last_turn = diag_list[-1]
        graph = last_turn.get("graph") if isinstance(last_turn, dict) else None
        if isinstance(graph, dict):
            bundle["last_turn_repro_metadata"] = graph.get("repro_metadata")
            bundle["last_turn_graph_errors"] = graph.get("errors", [])

    return bundle
