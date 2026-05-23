"""Deterministic authoritative action-resolution surfaces (no LLM invoke).

This module builds the runtime short path for affordance-resolved mundane
actions. It is **not** a mock of live generation: there is no adapter.generate
call, no LDSS fallback, and no model fallback — see ``metadata`` flags.
"""

from __future__ import annotations

from typing import Any

from ai_stack.language_io.language_adapter import resolve_string

from ai_stack.contracts.runtime_turn_contracts import ADAPTER_INVOCATION_AUTHORITATIVE_ACTION_RESOLUTION
from ai_stack.contracts.narrator_consequence_contracts import (
    build_local_context_transition,
    build_narrator_consequence_plan,
    build_updated_player_local_context,
    normalize_scene_affordance_model_for_contracts,
)
from ai_stack.contracts.environment_state_contracts import apply_action_to_environment_state


def _action_resolution_surface_inputs(
    *,
    player_action_frame: dict[str, Any],
    affordance_resolution: dict[str, Any],
) -> dict[str, str]:
    resolved_target = (
        player_action_frame.get("resolved_target")
        if isinstance(player_action_frame.get("resolved_target"), dict)
        else {}
    )
    return {
        "status": str(affordance_resolution.get("affordance_status") or "").strip().lower(),
        "policy": str(affordance_resolution.get("action_commit_policy") or "").strip().lower(),
        "verb": str(player_action_frame.get("verb") or "").strip().lower(),
        "target_label": str(
            resolved_target.get("matched_alias")
            or resolved_target.get("canonical_name")
            or resolved_target.get("target_id")
            or ""
        ).strip(),
        "action_kind": str(player_action_frame.get("action_kind") or "").strip().lower(),
    }


def _action_resolution_contract_surfaces(
    *,
    lang: str,
    player_action_frame: dict[str, Any],
    affordance_resolution: dict[str, Any],
    scene_affordance_model: dict[str, Any] | None,
    current_player_local_context: dict[str, Any] | None,
    environment_state: dict[str, Any] | None,
    environment_model: dict[str, Any] | None,
    actor_lane_context: dict[str, Any] | None,
    turn_number: int | None,
) -> dict[str, dict[str, Any]]:
    sam = normalize_scene_affordance_model_for_contracts(
        scene_affordance_model if isinstance(scene_affordance_model, dict) else {},
    )
    if not sam:
        return {
            "local_context_transition": {},
            "narrator_consequence_plan": {},
            "updated_player_local_context": {},
            "candidate_environment_state": {},
        }
    local_context_transition = build_local_context_transition(
        player_action_frame=player_action_frame,
        affordance_resolution=affordance_resolution,
        scene_affordance_model=sam,
        current_player_local_context=current_player_local_context,
    )
    narrator_consequence_plan = build_narrator_consequence_plan(
        lang=lang,
        player_action_frame=player_action_frame,
        affordance_resolution=affordance_resolution,
        scene_affordance_model=sam,
        local_context_transition=local_context_transition,
    )
    updated_player_local_context = build_updated_player_local_context(
        current_player_local_context=current_player_local_context,
        local_context_transition=local_context_transition,
        narrator_consequence_plan=narrator_consequence_plan,
        scene_affordance_model=sam,
    )
    candidate_environment_state = apply_action_to_environment_state(
        environment_state=environment_state,
        environment_model=environment_model,
        player_action_frame=player_action_frame,
        affordance_resolution=affordance_resolution,
        local_context_transition=local_context_transition,
        narrator_consequence_plan=narrator_consequence_plan,
        actor_lane_context=actor_lane_context,
        turn_number=turn_number,
    )
    return {
        "local_context_transition": local_context_transition,
        "narrator_consequence_plan": narrator_consequence_plan,
        "updated_player_local_context": updated_player_local_context,
        "candidate_environment_state": candidate_environment_state,
    }


def _action_resolution_template_key(surface: dict[str, str]) -> str:
    status = surface["status"]
    policy = surface["policy"]
    verb = surface["verb"]
    target_label = surface["target_label"]
    action_kind = surface["action_kind"]
    if policy == "needs_clarification" or status in {"unknown_target", "ambiguous"}:
        return (
            "action_resolution.clarification.ambiguous"
            if status == "ambiguous"
            else "action_resolution.clarification.unknown_target"
        )
    if status in {"blocked", "unsafe"}:
        return "action_resolution.blocked.generic"
    if verb in {"move_to", "stand_up"} or action_kind == "movement":
        return (
            "action_resolution.narrator.move_offscreen"
            if status == "allowed_offscreen"
            else "action_resolution.narrator.move_local"
        )
    if verb in {"look_at", "listen_to"} or action_kind == "perception":
        return (
            "action_resolution.narrator.perception_object"
            if target_label
            else "action_resolution.narrator.perception_generic"
        )
    if action_kind == "object_interaction" or verb in {
        "activate",
        "deactivate",
        "open",
        "place",
        "take",
    }:
        return (
            "action_resolution.narrator.object_interaction"
            if target_label
            else "action_resolution.narrator.generic"
        )
    if status == "partial":
        return "action_resolution.narrator.partial"
    return "action_resolution.narrator.generic"


def _action_resolution_narration(
    *,
    module_id: str,
    lang: str,
    content_modules_root: Any,
    key: str,
    target_label: str,
    narrator_consequence_plan: dict[str, Any],
) -> str:
    authored_text = narrator_consequence_plan.get("consequence_text") if narrator_consequence_plan else None
    if authored_text:
        return authored_text
    try:
        return resolve_string(
            module_id,
            key,
            lang,
            content_modules_root=content_modules_root,
            target_label=target_label or "…",
        )
    except KeyError:
        return resolve_string(
            module_id,
            "action_resolution.narrator.generic",
            lang,
            content_modules_root=content_modules_root,
            target_label=target_label or "…",
        )


def _synthetic_action_resolution_structured_output(narration: str) -> dict[str, Any]:
    return {
        "schema_version": "runtime_actor_turn_v1",
        "narration_summary": narration,
        "narrative_response": narration,
        "spoken_lines": [],
        "action_lines": [],
        "function_type": "action_resolution_surface",
    }


def _synthetic_action_resolution_metadata(
    *,
    structured: dict[str, Any],
    contract_surfaces: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    return {
        "adapter": "action_resolution_authoritative",
        "adapter_invocation_mode": ADAPTER_INVOCATION_AUTHORITATIVE_ACTION_RESOLUTION,
        "structured_output": structured,
        "authoritative_action_resolution": True,
        "generation_required": False,
        "mock_used": False,
        "ldss_fallback": False,
        "local_context_transition": contract_surfaces["local_context_transition"] or None,
        "narrator_consequence_plan": contract_surfaces["narrator_consequence_plan"] or None,
        "updated_player_local_context": contract_surfaces["updated_player_local_context"] or None,
        "candidate_environment_state": contract_surfaces["candidate_environment_state"] or None,
    }


def build_synthetic_generation_for_action_resolution(
    *,
    module_id: str,
    lang: str,
    player_action_frame: dict[str, Any],
    affordance_resolution: dict[str, Any],
    content_modules_root: Any = None,
    scene_affordance_model: dict[str, Any] | None = None,
    current_player_local_context: dict[str, Any] | None = None,
    environment_state: dict[str, Any] | None = None,
    environment_model: dict[str, Any] | None = None,
    actor_lane_context: dict[str, Any] | None = None,
    turn_number: int | None = None,
) -> dict[str, Any]:
    """Return a minimal successful generation dict with structured_output for proposal_normalize."""
    surface = _action_resolution_surface_inputs(
        player_action_frame=player_action_frame,
        affordance_resolution=affordance_resolution,
    )
    contract_surfaces = _action_resolution_contract_surfaces(
        lang=lang,
        player_action_frame=player_action_frame,
        affordance_resolution=affordance_resolution,
        scene_affordance_model=scene_affordance_model,
        current_player_local_context=current_player_local_context,
        environment_state=environment_state,
        environment_model=environment_model,
        actor_lane_context=actor_lane_context,
        turn_number=turn_number,
    )
    narr = _action_resolution_narration(
        module_id=module_id,
        lang=lang,
        content_modules_root=content_modules_root,
        key=_action_resolution_template_key(surface),
        target_label=surface["target_label"],
        narrator_consequence_plan=contract_surfaces["narrator_consequence_plan"],
    )
    structured = _synthetic_action_resolution_structured_output(narr)
    return {
        "success": True,
        "attempted": False,
        "fallback_used": False,
        "content": narr,
        "text": narr,
        "metadata": _synthetic_action_resolution_metadata(
            structured=structured,
            contract_surfaces=contract_surfaces,
        ),
    }
