"""Player-visible runtime surface projection helpers."""
from __future__ import annotations

from ._deps import *

_RUNTIME_ASPECT_FIELDS = (
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
    "symbolic_object_resonance_state",
    "symbolic_object_resonance_target",
    "symbolic_object_resonance_validation",
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


def copy_player_visible_runtime_surfaces(
    *,
    event: dict[str, Any],
    graph_state: dict[str, Any],
    selected_responder_set: list[Any],
) -> None:
    retrieval = graph_state.get("retrieval") if isinstance(graph_state.get("retrieval"), dict) else {}
    routing = graph_state.get("routing") if isinstance(graph_state.get("routing"), dict) else {}
    generation = graph_state.get("generation") if isinstance(graph_state.get("generation"), dict) else {}
    graph_diag = graph_state.get("graph_diagnostics") if isinstance(graph_state.get("graph_diagnostics"), dict) else {}
    if retrieval:
        event.setdefault("retrieval", retrieval)
    if routing or generation:
        event.setdefault("model_route", {**routing, "generation": generation})
    if graph_diag:
        event.setdefault("graph", graph_diag)
    if graph_state.get("selected_scene_function") is not None:
        event.setdefault("selected_scene_function", graph_state.get("selected_scene_function"))
    for field in _RUNTIME_ASPECT_FIELDS:
        value = graph_state.get(field)
        if isinstance(value, dict):
            event.setdefault(field, value)
    if selected_responder_set:
        event.setdefault("selected_responder_set", selected_responder_set)
    actor_survival_telemetry = (
        graph_state.get("actor_survival_telemetry")
        if isinstance(graph_state.get("actor_survival_telemetry"), dict)
        else {}
    )
    if actor_survival_telemetry:
        event.setdefault("actor_survival_telemetry", actor_survival_telemetry)


__all__ = ["copy_player_visible_runtime_surfaces"]
