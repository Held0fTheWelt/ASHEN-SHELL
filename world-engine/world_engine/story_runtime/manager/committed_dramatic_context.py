"""Committed dramatic-context projection.

Extracts dramatic context from committed turn state for subsequent planner, validator, and visible-projection consumers.
"""
from __future__ import annotations

from ._deps import *
from .committed_dramatic_context_parts import (
    beat_context,
    dramatic_outcome_context,
    narrative_thread_context,
    pacing_context,
    responder_context,
    retrieval_context,
    scene_assessment_context,
    scene_energy_context,
    social_state_context,
    state_target_context,
)

def _build_committed_dramatic_context_summary(
    *,
    graph_state: dict[str, Any],
    narrative_commit_payload: dict[str, Any],
    thread_metrics: dict[str, Any],
) -> dict[str, Any]:
    """Merge packaged runtime context with committed planner truth."""
    base = (
        graph_state.get("dramatic_context_summary")
        if isinstance(graph_state.get("dramatic_context_summary"), dict)
        else {}
    )
    planner = (
        narrative_commit_payload.get("planner_truth")
        if isinstance(narrative_commit_payload.get("planner_truth"), dict)
        else {}
    )
    scene_assessment = (
        planner.get("scene_assessment_core")
        if isinstance(planner.get("scene_assessment_core"), dict)
        else {}
    )
    social_summary = (
        planner.get("social_state_summary")
        if isinstance(planner.get("social_state_summary"), dict)
        else {}
    )
    beat = (
        narrative_commit_payload.get("beat_progression")
        if isinstance(narrative_commit_payload.get("beat_progression"), dict)
        else {}
    )
    retrieval = graph_state.get("retrieval") if isinstance(graph_state.get("retrieval"), dict) else {}
    continuity_query = (
        retrieval.get("continuity_query_signal")
        if isinstance(retrieval.get("continuity_query_signal"), dict)
        else {}
    )
    base_responder = base.get("responder") if isinstance(base.get("responder"), dict) else {}
    base_pacing = base.get("pacing") if isinstance(base.get("pacing"), dict) else {}
    base_scene_energy = (
        base.get("scene_energy")
        if isinstance(base.get("scene_energy"), dict)
        else {}
    )
    base_pacing_rhythm = (
        base.get("pacing_rhythm")
        if isinstance(base.get("pacing_rhythm"), dict)
        else {}
    )
    base_temporal_control = (
        base.get("temporal_control")
        if isinstance(base.get("temporal_control"), dict)
        else {}
    )
    base_genre_awareness = (
        base.get("genre_awareness")
        if isinstance(base.get("genre_awareness"), dict)
        else {}
    )
    base_scene = (
        base.get("scene_assessment")
        if isinstance(base.get("scene_assessment"), dict)
        else {}
    )
    committed_context = dict(base)
    committed_context.update(
        {
            "contract": "bounded_dramatic_context.v1",
            "source": "narrative_commit.planner_truth+runtime_turn_state",
            "committed_scene_id": narrative_commit_payload.get("committed_scene_id"),
            "commit_reason_code": narrative_commit_payload.get("commit_reason_code"),
            "selected_scene_function": planner.get("selected_scene_function")
            or base.get("selected_scene_function"),
            "function_type": planner.get("function_type") or base.get("function_type"),
            "responder": responder_context(planner, base_responder),
            "pacing": pacing_context(planner, base_pacing),
            "scene_energy": scene_energy_context(planner, base_scene_energy),
            "pacing_rhythm": state_target_context(planner, "pacing_rhythm", base_pacing_rhythm),
            "temporal_control": state_target_context(planner, "temporal_control", base_temporal_control),
            "genre_awareness": state_target_context(planner, "genre_awareness", base_genre_awareness),
            "social_pressure": state_target_context(planner, "social_pressure"),
            "expectation_variation": state_target_context(planner, "expectation_variation"),
            "narrative_momentum": state_target_context(planner, "narrative_momentum"),
            "scene_assessment": scene_assessment_context(scene_assessment, base_scene),
            "social_state": social_state_context(social_summary),
            "dramatic_outcome": dramatic_outcome_context(planner),
            "beat": beat_context(beat),
            "narrative_threads": narrative_thread_context(thread_metrics),
            "retrieval_context": retrieval_context(retrieval, continuity_query),
        }
    )
    return committed_context

__all__ = [
    name
    for name in globals()
    if not name.startswith("__") and name != "annotations"
]
