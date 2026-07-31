"""Canonical record builder for player-visible recoverable turns."""
from __future__ import annotations

from ._deps import *

_CANONICAL_RUNTIME_ASPECT_FIELDS = (
    "scene_energy_target",
    "scene_energy_transition",
    "scene_energy_validation",
    "pacing_rhythm_state",
    "pacing_rhythm_target",
    "pacing_rhythm_validation",
    "temporal_control_state",
    "temporal_control_target",
    "temporal_control_validation",
    "sensory_context_state",
    "sensory_context_target",
    "sensory_context_validation",
    "social_pressure_state",
    "social_pressure_target",
    "social_pressure_validation",
    "tonal_consistency_target",
    "tonal_consistency_validation",
    "expectation_variation_state",
    "expectation_variation_target",
    "expectation_variation_validation",
    "narrative_momentum_state",
    "narrative_momentum_target",
    "narrative_momentum_validation",
)


def build_player_visible_canonical_record(
    *,
    session: StorySession,
    graph_state: dict[str, Any],
    event: dict[str, Any],
    trace_id: str | None,
    commit_turn_number: int,
    turn_outcome: str,
    human_att: dict[str, Any],
) -> dict[str, Any]:
    committed_result = (
        event.get("committed_result")
        if isinstance(event.get("committed_result"), dict)
        else graph_state.get("committed_result")
    )
    record: dict[str, Any] = {
        "canonical_turn_id": event["canonical_turn_id"],
        "turn_number": commit_turn_number,
        "turn_kind": event.get("turn_kind") or "player_rejected_recoverable",
        "trace_id": trace_id or "",
        "turn_outcome": turn_outcome,
        "narrative_commit": event.get("narrative_commit"),
        "validation_outcome": event.get("validation_outcome"),
        "committed_result": committed_result,
        "no_dead_end_recovery": event.get("no_dead_end_recovery"),
        "turn_aspect_ledger": event.get("turn_aspect_ledger"),
        "visible_output_bundle": event.get("visible_output_bundle"),
        "human_input_attribution": human_att,
        "hierarchical_memory_update": event.get("hierarchical_memory"),
        "recoverable_outcome": True,
        "committed_state_after": {
            "current_scene_id": session.current_scene_id,
            "turn_counter": session.turn_counter,
            "environment_state": session.environment_state
            if isinstance(session.environment_state, dict)
            else {},
        },
    }
    for field in _CANONICAL_RUNTIME_ASPECT_FIELDS:
        record[field] = event.get(field)
    return record


__all__ = ["build_player_visible_canonical_record"]
