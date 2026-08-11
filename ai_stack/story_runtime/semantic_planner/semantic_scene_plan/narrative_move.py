"""Narrative-move proposal assembly for configurable story governance."""

from __future__ import annotations

from typing import Any

from .utils import _as_dict, _as_list, _clean, _unique_clean


def _reference_rejoin_policy(governance: dict[str, Any]) -> dict[str, Any]:
    mode_policy = _as_dict(governance.get("mode_policy"))
    return _as_dict(mode_policy.get("reference_rejoin"))


def _arc_relation(
    *,
    governance: dict[str, Any],
    canonical_step_id: str,
    selected_scene_function: str,
) -> str:
    path_role = _clean(governance.get("canonical_path_role"))
    if path_role == "mandatory_spine":
        return "mandatory_path"
    if path_role == "optional_reference":
        return "optional_reference_available" if canonical_step_id else "unbounded_by_reference"
    if path_role != "reference_arc":
        return "not_governed"
    if not canonical_step_id:
        return "off_path_no_reference"

    rejoin = _reference_rejoin_policy(governance)
    strategy = _clean(rejoin.get("strategy"))
    scene_functions = {
        _clean(value)
        for value in _as_list(rejoin.get("scene_functions"))
        if _clean(value)
    }
    if strategy == "scene_function_allowlist" and selected_scene_function in scene_functions:
        return "rejoined_reference_opportunity"
    return "off_path_with_reference_available"


def build_narrative_move_proposal(
    *,
    content_frame: dict[str, Any],
    selected_scene_function: str,
    narrative_scene_function: str,
    pressure_function: str,
    scene_target: dict[str, Any],
    continuity_obligation: dict[str, Any],
    selected_responder_set: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    """Build an advisory move without granting the planner state-write authority."""

    governance = _as_dict(content_frame.get("narrative_governance"))
    canonical_step_id = _clean(content_frame.get("canonical_path_step_id"))
    relation = _arc_relation(
        governance=governance,
        canonical_step_id=canonical_step_id,
        selected_scene_function=_clean(selected_scene_function),
    )
    responder_ids = _unique_clean(
        [
            row.get("actor_id") or row.get("responder_id")
            for row in (selected_responder_set or [])
            if isinstance(row, dict)
        ]
    )
    reference_opportunities = _unique_clean(
        [
            *_as_list(content_frame.get("reference_action_opportunities")),
            *_as_list(content_frame.get("reference_narrator_opportunities")),
        ]
    )
    return {
        "schema_version": "narrative_move_proposal.v1",
        "authority_scope": "planner_advisory",
        "authoritative": False,
        "state_writer": "world_engine_story_runtime",
        "narrative_mode": _clean(governance.get("active_mode")) or "reenactment",
        "progression_authority": _clean(governance.get("progression_authority"))
        or "canonical_step",
        "arc_relation": relation,
        "selected_scene_function": _clean(selected_scene_function),
        "narrative_scene_function": _clean(narrative_scene_function),
        "pressure_function": _clean(pressure_function),
        "target": dict(scene_target),
        "responder_ids": responder_ids,
        "continuity_class": continuity_obligation.get("continuity_class"),
        "reference_step_id": canonical_step_id or None,
        "reference_opportunities": reference_opportunities[:12],
        "canonical_output_required": relation == "mandatory_path",
        "constraints": [
            "proposal_cannot_commit_state",
            "world_engine_remains_single_state_writer",
            "reference_material_is_not_automatically_visible_output",
        ],
    }


__all__ = ["build_narrative_move_proposal"]
