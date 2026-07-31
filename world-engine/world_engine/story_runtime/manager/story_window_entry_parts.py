"""Small builders used by authoritative story-window projection."""
from __future__ import annotations

from ._deps import *
from .content_language import _goc_content_modules_root
from .degradation_and_turn_blocks import _scene_blocks_from_turn_event
from .dramatic_context_authority import _story_window_dramatic_context
from .player_input_scene_blocks import _player_input_scene_blocks_for_story_window
from .visible_projection_opening import _coerce_visible_text_lines


def event_surfaces_for_story_window(event: dict[str, Any]) -> dict[str, Any]:
    commit = event.get("narrative_commit") if isinstance(event.get("narrative_commit"), dict) else {}
    consequences = commit.get("committed_consequences")
    bundle = event.get("visible_output_bundle") if isinstance(event.get("visible_output_bundle"), dict) else {}
    planner = commit.get("planner_truth") if isinstance(commit.get("planner_truth"), dict) else {}
    social_summary = (
        planner.get("social_state_summary")
        if isinstance(planner.get("social_state_summary"), dict)
        else {}
    )
    dramatic_context = (
        event.get("dramatic_context_summary")
        if isinstance(event.get("dramatic_context_summary"), dict)
        else {}
    )
    return {
        "turn_number": event.get("turn_number"),
        "turn_kind": str(event.get("turn_kind") or "player").strip() or "player",
        "commit": commit,
        "consequence_lines": [str(item) for item in consequences]
        if isinstance(consequences, list)
        else [],
        "spoken_lines": _coerce_visible_text_lines(bundle.get("spoken_lines")),
        "action_lines": _coerce_visible_text_lines(bundle.get("action_lines")),
        "render_support": bundle.get("render_support")
        if isinstance(bundle.get("render_support"), dict)
        else None,
        "authority": event.get("committed_turn_authority")
        if isinstance(event.get("committed_turn_authority"), dict)
        else {},
        "validation": event.get("validation_outcome")
        if isinstance(event.get("validation_outcome"), dict)
        else {},
        "runtime_governance_surface": event.get("runtime_governance_surface")
        if isinstance(event.get("runtime_governance_surface"), dict)
        else {},
        "social_summary": social_summary,
        "story_dramatic_context": _story_window_dramatic_context(dramatic_context),
    }


def actor_summary_for_story_window(
    *,
    event: dict[str, Any],
    story_dramatic_context: dict[str, Any],
    spoken_lines: list[str],
    action_lines: list[str],
) -> dict[str, Any]:
    actor_turn_summary = (
        event.get("actor_turn_summary")
        if isinstance(event.get("actor_turn_summary"), dict)
        else {}
    )
    if actor_turn_summary or not story_dramatic_context:
        return actor_turn_summary
    return {
        "contract": "actor_turn_summary.v1",
        "primary_responder_id": story_dramatic_context.get("responder_id"),
        "secondary_responder_ids": story_dramatic_context.get("secondary_responder_ids") or [],
        "spoken_line_count": story_dramatic_context.get("spoken_line_count") or len(spoken_lines),
        "action_line_count": story_dramatic_context.get("action_line_count") or len(action_lines),
        "initiative_summary": story_dramatic_context.get("initiative_summary") or {},
        "last_actor_outcome_summary": story_dramatic_context.get("last_actor_outcome_summary"),
    }


def authority_summary_for_story_window(
    *,
    event: dict[str, Any],
    commit: dict[str, Any],
    validation: dict[str, Any],
    authority: dict[str, Any],
    social_summary: dict[str, Any],
    story_dramatic_context: dict[str, Any],
) -> dict[str, Any]:
    return {
        "authority_record_version": authority.get("authority_record_version"),
        "committed_scene_id": authority.get("committed_scene_id") or commit.get("committed_scene_id"),
        "validation_status": authority.get("validation_status") or validation.get("status"),
        "commit_applied": authority.get("commit_applied"),
        "quality_class": authority.get("quality_class"),
        "degradation_signals": authority.get("degradation_signals") or [],
        "degradation_summary": authority.get("degradation_summary"),
        "selected_scene_function": event.get("selected_scene_function"),
        "experiment_preview": event.get("experiment_preview"),
        "visibility_class_markers": event.get("visibility_class_markers") or [],
        "failure_markers": event.get("failure_markers") or [],
        "social_state_fingerprint": social_summary.get("fingerprint"),
        "social_risk_band": social_summary.get("social_risk_band"),
        "social_continuity_status": social_summary.get("social_continuity_status"),
        "dramatic_context": story_dramatic_context,
    }


def detect_thin_path_narrator_fold(event: dict[str, Any]) -> tuple[str | None, bool]:
    scene_blocks = _scene_blocks_from_turn_event(event)
    realization_plan = event.get("realization_plan") if isinstance(event.get("realization_plan"), dict) else None
    path_summary = (
        event.get("observability_path_summary")
        if isinstance(event.get("observability_path_summary"), dict)
        else event.get("path_summary")
        if isinstance(event.get("path_summary"), dict)
        else None
    )
    realize_capability = path_summary.get("realize_via_capabilities_used_capability") if path_summary else None
    if not realize_capability and realization_plan:
        capabilities = realization_plan.get("capabilities_selected") or []
        realize_capability = capabilities[0] if capabilities else None
    is_narrator_capability = isinstance(realize_capability, str) and realize_capability.startswith("narrator.")
    if not scene_blocks or not is_narrator_capability:
        return None, False
    narrator_blocks = [
        b
        for b in scene_blocks
        if str(b.get("block_type") or "").strip().lower() == "narrator"
    ]
    actor_blocks = [
        b
        for b in scene_blocks
        if str(b.get("block_type") or "").strip().lower() in ("actor_line", "actor_action")
    ]
    if len(narrator_blocks) != 1 or actor_blocks:
        return None, False
    candidate_text = str(narrator_blocks[0].get("text") or "").strip()
    return (candidate_text, True) if candidate_text else (None, False)


def build_story_window_player_entry(
    *,
    session: StorySession,
    event: dict[str, Any],
    turn_number: Any,
    raw_input: str,
    thin_path_narrator_text: str | None,
    thin_path_fold: bool,
) -> dict[str, Any] | None:
    if not raw_input:
        return None
    projection = session.runtime_projection if isinstance(session.runtime_projection, dict) else {}
    human_actor_id = str(projection.get("human_actor_id") or "").strip()
    interpreted = event.get("interpreted_input") if isinstance(event.get("interpreted_input"), dict) else {}
    role = str(projection.get("selected_player_role") or "").strip()
    player_display_name = goc_player_role_display_name(role) if role else None
    player_blocks = _player_input_scene_blocks_for_story_window(
        session_id=session.session_id,
        turn_number=turn_number,
        raw_input=raw_input,
        session_output_language=session.session_output_language,
        human_actor_id=human_actor_id or None,
        interpreted_input=interpreted,
        module_id=session.module_id,
    )
    if thin_path_fold and thin_path_narrator_text and player_blocks:
        for player_block in player_blocks:
            if str(player_block.get("block_type") or "") == "player_input_outcome":
                player_block["text"] = thin_path_narrator_text
                player_block["source"] = "narrator_realization_fold"
                break
    module_id = str(session.module_id or GOD_OF_CARNAGE_MODULE_ID).strip() or GOD_OF_CARNAGE_MODULE_ID
    lang = str(session.session_output_language or DEFAULT_SESSION_LANGUAGE).strip().lower()[:2] or DEFAULT_SESSION_LANGUAGE
    second_person = resolve_string(
        module_id,
        "player_shell.second_person",
        lang,
        content_modules_root=_goc_content_modules_root(),
    )
    player_entry: dict[str, Any] = {
        "entry_id": f"{session.session_id}:{turn_number}:player",
        "kind": "player_turn",
        "role": "player",
        "speaker": player_display_name if player_display_name else second_person,
        "turn_number": turn_number,
        "text": raw_input,
        "source": "player_input",
    }
    if player_blocks:
        player_entry["scene_blocks"] = player_blocks
        player_entry["text"] = str(player_blocks[0].get("text") or raw_input).strip() or raw_input
    return player_entry


def vitality_readout_for_story_window(event: dict[str, Any]) -> dict[str, Any]:
    telemetry = event.get("actor_survival_telemetry") if isinstance(event.get("actor_survival_telemetry"), dict) else {}
    vitality = telemetry.get("vitality_telemetry_v1") if isinstance(telemetry.get("vitality_telemetry_v1"), dict) else {}
    operator_hints = (
        telemetry.get("operator_diagnostic_hints")
        if isinstance(telemetry.get("operator_diagnostic_hints"), dict)
        else {}
    )
    passivity = (
        telemetry.get("passivity_diagnosis_v1")
        if isinstance(telemetry.get("passivity_diagnosis_v1"), dict)
        else operator_hints
    )
    return {
        "actor_survival_telemetry": telemetry,
        "passivity_diagnosis": passivity,
        "vitality_summary": {
            "response_present": bool(vitality.get("response_present")),
            "initiative_present": bool(vitality.get("initiative_present")),
            "multi_actor_realized": bool(vitality.get("multi_actor_realized")),
            "sparse_input_recovery_applied": bool(vitality.get("sparse_input_recovery_applied")),
            "realized_actor_ids": list(vitality.get("realized_actor_ids") or []),
            "rendered_actor_ids": list(vitality.get("rendered_actor_ids") or []),
        },
    }


def build_story_window_runtime_entry(
    *,
    session: StorySession,
    turn_number: Any,
    turn_kind: str,
    visible_lines: list[str],
    spoken_lines: list[str],
    action_lines: list[str],
    consequence_lines: list[str],
    story_dramatic_context: dict[str, Any],
    authority_summary: dict[str, Any],
    quality_class: str,
    degradation_signals: list[str],
    degradation_summary: Any,
    actor_turn_summary: dict[str, Any],
    actor_survival_telemetry: dict[str, Any],
    vitality_summary: dict[str, Any],
    passivity_diagnosis: dict[str, Any],
    runtime_governance_surface: dict[str, Any],
    scene_blocks: list[dict[str, Any]],
    render_support: dict[str, Any] | None,
) -> dict[str, Any]:
    runtime_entry = {
        "entry_id": f"{session.session_id}:{turn_number}:{turn_kind}",
        "kind": "opening" if turn_kind == "opening" else "runtime_response",
        "role": "runtime",
        "speaker": "World of Shadows",
        "turn_number": turn_number,
        "text": "\n\n".join(visible_lines),
        "spoken_lines": spoken_lines,
        "action_lines": action_lines,
        "committed_consequences": consequence_lines,
        "responder_id": story_dramatic_context.get("responder_id"),
        "validation_status": authority_summary.get("validation_status"),
        "quality_class": quality_class,
        "degradation_signals": degradation_signals,
        "degradation_summary": degradation_summary,
        "degraded": quality_class in {QUALITY_CLASS_DEGRADED, QUALITY_CLASS_FAILED},
        "degraded_reasons": list(degradation_signals),
        "actor_turn_summary": actor_turn_summary,
        "actor_survival_telemetry": actor_survival_telemetry,
        "vitality_summary": vitality_summary,
        "why_turn_felt_passive": list(passivity_diagnosis.get("why_turn_felt_passive") or []),
        "primary_passivity_factors": list(passivity_diagnosis.get("primary_passivity_factors") or []),
        "source": "authoritative_story_runtime",
        "runtime_governance_surface": runtime_governance_surface,
        "authority_summary": authority_summary,
    }
    if scene_blocks:
        runtime_entry["scene_blocks"] = scene_blocks
    if render_support:
        runtime_entry["render_support"] = render_support
    if story_dramatic_context:
        runtime_entry["dramatic_context_summary"] = story_dramatic_context
    return runtime_entry


__all__ = [
    "actor_summary_for_story_window",
    "authority_summary_for_story_window",
    "build_story_window_runtime_entry",
    "build_story_window_player_entry",
    "detect_thin_path_narrator_fold",
    "event_surfaces_for_story_window",
    "vitality_readout_for_story_window",
]
