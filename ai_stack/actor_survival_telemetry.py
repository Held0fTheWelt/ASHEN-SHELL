"""Actor-survival telemetry: track where agent behavior survives or degrades.

Operators need visibility into whether the responder set, spoken lines, action
beats, and degradation state made it through generation → validation →
commit → render → frontend.

This module instruments the turn pipeline to produce operator-visible telemetry
proving which actor-level outputs survived each seam.
"""

from __future__ import annotations

from typing import Any


def build_actor_survival_telemetry(
    state: dict[str, Any],
    *,
    generation_ok: bool,
    validation_ok: bool,
    commit_applied: bool,
    fallback_taken: bool,
) -> dict[str, Any]:
    """Build operator-facing actor-survival summary for a turn.

    Tracks whether responder set, scene function, spoken lines, and action
    beats survived each processing seam. Used to populate operator dashboards
    and diagnostics.

    Args:
        state: RuntimeTurnState snapshot
        generation_ok: True if model generation succeeded
        validation_ok: True if validation passed
        commit_applied: True if committed_result was applied
        fallback_taken: True if fallback path was used

    Returns:
        Telemetry dict with survival markers at each seam
    """
    responders = state.get("selected_responder_set") or []
    primary_responder = responders[0].get("actor_id") if responders and isinstance(responders[0], dict) else None
    scene_function = state.get("selected_scene_function") or ""

    # Generation-level: what was produced
    generation = state.get("generation") or {}
    gen_meta = generation.get("metadata") if isinstance(generation.get("metadata"), dict) else {}
    gen_structured = gen_meta.get("structured_output") if isinstance(gen_meta.get("structured_output"), dict) else {}
    gen_spoken_lines = gen_structured.get("spoken_lines") or []
    gen_action_lines = gen_structured.get("action_lines") or []

    # Validation-level: what passed
    validation = state.get("validation_outcome") or {}
    val_approved = validation.get("status") == "approved"
    val_reason = validation.get("reason") or ""

    # Commit-level: what was committed
    committed = state.get("committed_result") or {}
    committed_effects = committed.get("committed_effects") or []

    # Render-level: what made it to visible output
    visible_bundle = state.get("visible_output_bundle") or {}
    rendered_spoken = visible_bundle.get("spoken_lines") or []
    rendered_narration = visible_bundle.get("gm_narration") or []

    # Degradation markers
    failure_markers = state.get("failure_markers") or []
    fallback_marker = {
        m.get("marker"): m.get("note")
        for m in failure_markers
        if isinstance(m, dict) and "fallback" in m.get("marker", "").lower()
    }

    return {
        "turn_telemetry_version": "1.0",
        "actor_survival": {
            # Configured intent
            "configured_responder_set_count": len(responders),
            "configured_primary_responder": primary_responder,
            "configured_scene_function": scene_function,

            # Generation phase
            "generation_phase": {
                "generation_attempted": generation_ok,
                "generation_fallback_used": fallback_taken,
                "spoken_lines_generated": len(gen_spoken_lines),
                "action_lines_generated": len(gen_action_lines),
                "responder_attribution_present": any(
                    line.get("speaker_id") for line in gen_spoken_lines
                    if isinstance(line, dict)
                ),
            },

            # Validation phase
            "validation_phase": {
                "validation_attempted": True,
                "validation_approved": val_approved,
                "validation_reason": val_reason,
                "actor_legality_checked": "actor" in val_reason.lower() or val_approved,
            },

            # Commit phase
            "commit_phase": {
                "commit_applied": commit_applied,
                "committed_effects_count": len(committed_effects),
                "responder_outcome_summary": committed.get("responder_outcome_summary"),
                "initiative_summary": committed.get("initiative_summary"),
            },

            # Render phase
            "render_phase": {
                "spoken_lines_rendered": len(rendered_spoken),
                "narration_blocks_rendered": len(rendered_narration),
                "continuity_state_present": "continuation_state" in visible_bundle,
                "responder_trace_present": "responder_trace" in visible_bundle,
            },

            # Degradation tracking
            "degradation_markers": {
                "fallback_used": fallback_taken,
                "validation_failed": not val_approved,
                "commit_not_applied": not commit_applied,
                "fallback_reason": str(fallback_marker.get("fallback_path_taken", "unknown")),
            },
        },
        "operator_diagnostic_hints": _build_operator_hints(
            generation_ok=generation_ok,
            validation_ok=validation_ok,
            commit_applied=commit_applied,
            fallback_taken=fallback_taken,
            primary_responder=primary_responder,
            rendered_spoken=rendered_spoken,
        ),
    }


def _build_operator_hints(
    generation_ok: bool,
    validation_ok: bool,
    commit_applied: bool,
    fallback_taken: bool,
    primary_responder: str | None,
    rendered_spoken: list,
) -> dict[str, Any]:
    """Suggest to operator where actor behavior may have degraded."""
    hints = []

    if fallback_taken:
        hints.append("Turn used model fallback; generation quality may be lower.")

    if not validation_ok:
        hints.append("Turn failed validation; actor behavior may be constrained or corrected.")

    if not commit_applied:
        hints.append("Turn commit was not applied; story state may not reflect responder actions.")

    if not rendered_spoken:
        hints.append("No spoken lines in final output; responder may have been silent or narration-only.")

    if not primary_responder:
        hints.append("No primary responder identified; turn may have defaulted to narrator.")

    if generation_ok and validation_ok and commit_applied and not fallback_taken and rendered_spoken:
        hints.append("Turn completed with full actor agency: generated, validated, committed, rendered.")

    return {
        "hints": hints,
        "actor_agency_level": _assess_agency_level(
            generation_ok, validation_ok, commit_applied, fallback_taken, bool(rendered_spoken)
        ),
    }


def _assess_agency_level(
    generation_ok: bool,
    validation_ok: bool,
    commit_applied: bool,
    fallback_taken: bool,
    has_spoken_output: bool,
) -> str:
    """Classify turn's actor agency level for operator dashboards."""
    if not generation_ok:
        return "generation_failed"
    if fallback_taken:
        return "fallback_active"
    if not validation_ok:
        return "validation_constrained"
    if not commit_applied:
        return "commit_blocked"
    if not has_spoken_output:
        return "narration_only"
    if commit_applied and validation_ok and has_spoken_output:
        return "full_actor_agency"
    return "partial_agency"


def build_operator_turn_history_row(
    turn_number: int,
    turn_kind: str,
    primary_responder: str | None,
    scene_function: str,
    telemetry: dict[str, Any],
    visible_output: dict[str, Any],
) -> dict[str, Any]:
    """Format a turn for operator turn-history surface (admin/diagnostics).

    Includes responder, validation result, render summary, fallback truth,
    and agency level so operators can trace where behavior survived/degraded.
    """
    actor_survival = telemetry.get("actor_survival") or {}
    hints = telemetry.get("operator_diagnostic_hints") or {}

    return {
        "turn_number": turn_number,
        "turn_kind": turn_kind,
        "responder": primary_responder or "(narrator)",
        "scene_function": scene_function or "(unknown)",
        "validation_passed": actor_survival.get("validation_phase", {}).get("validation_approved", False),
        "commit_applied": actor_survival.get("commit_phase", {}).get("commit_applied", False),
        "spoken_lines_count": actor_survival.get("render_phase", {}).get("spoken_lines_rendered", 0),
        "narration_blocks_count": actor_survival.get("render_phase", {}).get("narration_blocks_rendered", 0),
        "fallback_used": actor_survival.get("degradation_markers", {}).get("fallback_used", False),
        "agency_level": hints.get("actor_agency_level", "unknown"),
        "diagnostic_hints": hints.get("hints", []),
        "visible_output_type": "actor_agency" if (visible_output.get("spoken_lines") or visible_output.get("action_lines")) else "narration_only",
    }


__all__ = [
    "build_actor_survival_telemetry",
    "build_operator_turn_history_row",
]
