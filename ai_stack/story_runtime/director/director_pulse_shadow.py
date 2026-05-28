"""Director Pulse shadow path.

Evaluates one Director tick and returns a diagnostic bundle of four Pulse-MVP
events without touching the existing block-bundle path or session state.

Shadow mode (ADR-0058 §8):
* Runs in parallel to the existing visible_scene_output.blocks.v1 bundle path.
* Does not replace the bundle path — bundle path is still primary.
* Does not mutate caller state.
* Does not consume mandatory beats.
* Does not advance the canonical path.
* Always labeled ``shadow_only: True``.
* Silence is a first-class, recorded Director choice — not a fallback.

Governance:
* ADR-0058 — Director-Driven Pulse and Block-Stream-Bus
* ADR-0059 — Semantic NPC Motivation Score
* ADR-0060 — Souffleuse Inner Voice Composition
* ADR-0039 — No Pi/Π runtime keys; semantic names only
"""

from __future__ import annotations

import uuid
from typing import Any

from ai_stack.contracts.director_pulse_contracts import (
    ACTION_SILENCE,
    ACTION_SPEAK,
    CAPABILITY_NAME_ACTOR_PRESSURE_PROFILES,
    CAPABILITY_NAME_INTERACTION_PATTERNS,
    CAPABILITY_NAME_NARRATIVE_MOMENTUM,
    CAPABILITY_NAME_PACING_RHYTHM,
    CAPABILITY_NAME_RELATIONSHIP_DYNAMICS,
    CAPABILITY_NAME_SCENE_ENERGY,
    CAPABILITY_NAME_SOCIAL_PRESSURE,
    CUT_IN_CUT_EM_DASH,
    CUT_IN_CUT_SKIP_TO_END,
    CUT_IN_UNINTERRUPTED,
    LANE_PLAYER_HINT,
    LANE_VISIBLE_SCENE_OUTPUT,
    TRIGGER_MOTIVATION_THRESHOLD_CROSSED,
    TRIGGER_PLAYER_INPUT,
    BLOCK_TYPE_SOUFFLEUSE,
    build_block_stream_event,
    build_director_tick_decision,
    build_player_cut_in_event,
    resolve_cut_kind_for_block_type,
    CUT_KIND_EM_DASH,
)
from ai_stack.story_runtime.npc_agency.npc_motivation_score_engine import (
    compute_npc_motivation_scores,
    select_initiative_actor,
)


def _new_id() -> str:
    return str(uuid.uuid4())


def _std_composition_inputs() -> list[str]:
    return [
        CAPABILITY_NAME_SCENE_ENERGY,
        CAPABILITY_NAME_SOCIAL_PRESSURE,
        CAPABILITY_NAME_RELATIONSHIP_DYNAMICS,
        CAPABILITY_NAME_NARRATIVE_MOMENTUM,
        CAPABILITY_NAME_ACTOR_PRESSURE_PROFILES,
        CAPABILITY_NAME_INTERACTION_PATTERNS,
        CAPABILITY_NAME_PACING_RHYTHM,
    ]


def _director_motivation_scores(
    *,
    npc_ids: list[str],
    tick_id: str,
    scene_energy_output: dict[str, Any] | None,
    social_pressure_output: dict[str, Any] | None,
    relationship_state_output: dict[str, Any] | None,
    narrative_momentum_output: dict[str, Any] | None,
    actor_pressure_profiles: dict[str, Any] | None,
    npc_motivation_score_policy: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    return compute_npc_motivation_scores(
        npc_ids=npc_ids,
        tick_id=tick_id,
        scene_energy_output=scene_energy_output,
        social_pressure_output=social_pressure_output,
        relationship_state_output=relationship_state_output,
        narrative_momentum_output=narrative_momentum_output,
        actor_pressure_profiles=actor_pressure_profiles,
        npc_motivation_score_policy=npc_motivation_score_policy,
    )


def _director_action_choice(
    *,
    player_input_payload: dict[str, Any] | None,
    initiative_actor_id: str | None,
    trigger_kind: str,
    triggering_actor_id: str | None,
) -> tuple[str, str, str | None]:
    if player_input_payload:
        return TRIGGER_PLAYER_INPUT, ACTION_SPEAK, triggering_actor_id or "player"
    if initiative_actor_id:
        return trigger_kind, ACTION_SPEAK, initiative_actor_id
    return trigger_kind, ACTION_SILENCE, None


def _director_block_stream_event(
    *,
    block_payload: dict[str, Any] | None,
    current_block_type: str | None,
    current_block_id: str | None,
    player_input_payload: dict[str, Any] | None,
    tick_id: str,
    chosen_actor: str | None,
) -> dict[str, Any] | None:
    if not block_payload or not current_block_type:
        return None
    cut_in_state = CUT_IN_UNINTERRUPTED
    if player_input_payload and current_block_id:
        cut_kind = resolve_cut_kind_for_block_type(current_block_type)
        cut_in_state = (
            CUT_IN_CUT_EM_DASH
            if cut_kind == CUT_KIND_EM_DASH
            else CUT_IN_CUT_SKIP_TO_END
        )
    lane = (
        LANE_PLAYER_HINT
        if current_block_type == BLOCK_TYPE_SOUFFLEUSE
        else LANE_VISIBLE_SCENE_OUTPUT
    )
    return build_block_stream_event(
        tick_id=tick_id,
        block_type=current_block_type,
        block_payload=block_payload,
        cut_in_state=cut_in_state,
        lane=lane,
        source=chosen_actor or "director",
    )


def _director_player_cut_in_event(
    *,
    player_input_payload: dict[str, Any] | None,
    tick_id: str,
    current_block_id: str | None,
    current_block_type: str | None,
) -> dict[str, Any] | None:
    if not player_input_payload:
        return None
    return build_player_cut_in_event(
        tick_id=tick_id,
        interrupted_block_id=current_block_id,
        interrupted_block_type=current_block_type,
        cut_kind=resolve_cut_kind_for_block_type(current_block_type),
        player_input_payload=player_input_payload,
    )


def evaluate_director_tick(
    *,
    trigger_kind: str = TRIGGER_MOTIVATION_THRESHOLD_CROSSED,
    triggering_actor_id: str | None = None,
    npc_ids: list[str],
    scene_energy_output: dict[str, Any] | None = None,
    social_pressure_output: dict[str, Any] | None = None,
    relationship_state_output: dict[str, Any] | None = None,
    narrative_momentum_output: dict[str, Any] | None = None,
    actor_pressure_profiles: dict[str, Any] | None = None,
    npc_motivation_score_policy: dict[str, Any] | None = None,
    gathering_paused: bool = False,
    since_last_tick_ms: float | None = None,
    current_block_id: str | None = None,
    current_block_type: str | None = None,
    block_payload: dict[str, Any] | None = None,
    player_input_payload: dict[str, Any] | None = None,
    tick_id: str | None = None,
) -> dict[str, Any]:
    """Evaluate one shadow Director tick and return the Pulse diagnostics."""
    resolved_tick_id = tick_id or _new_id()

    motivation_scores = _director_motivation_scores(
        npc_ids=npc_ids,
        tick_id=resolved_tick_id,
        scene_energy_output=scene_energy_output,
        social_pressure_output=social_pressure_output,
        relationship_state_output=relationship_state_output,
        narrative_momentum_output=narrative_momentum_output,
        actor_pressure_profiles=actor_pressure_profiles,
        npc_motivation_score_policy=npc_motivation_score_policy,
    )
    initiative_actor_id = select_initiative_actor(motivation_scores)
    resolved_trigger, chosen_action, chosen_actor = _director_action_choice(
        player_input_payload=player_input_payload,
        initiative_actor_id=initiative_actor_id,
        trigger_kind=trigger_kind,
        triggering_actor_id=triggering_actor_id,
    )
    tick_decision = build_director_tick_decision(
        trigger_kind=resolved_trigger,
        triggering_actor_id=triggering_actor_id,
        chosen_action_kind=chosen_action,
        chosen_actor_id=chosen_actor,
        composition_inputs=_std_composition_inputs(),
        since_last_tick_ms=since_last_tick_ms,
        silence_reason="no_npc_above_motivation_threshold" if chosen_action == ACTION_SILENCE else None,
        tick_id=resolved_tick_id,
    )

    return {
        "director_tick_decision": tick_decision,
        "npc_motivation_scores": motivation_scores,
        "block_stream_event": _director_block_stream_event(
            block_payload=block_payload,
            current_block_type=current_block_type,
            current_block_id=current_block_id,
            player_input_payload=player_input_payload,
            tick_id=resolved_tick_id,
            chosen_actor=chosen_actor,
        ),
        "player_cut_in_event": _director_player_cut_in_event(
            player_input_payload=player_input_payload,
            tick_id=resolved_tick_id,
            current_block_id=current_block_id,
            current_block_type=current_block_type,
        ),
        "gathering_paused": gathering_paused,
        "shadow_only": True,
    }


__all__ = [
    "evaluate_director_tick",
]
