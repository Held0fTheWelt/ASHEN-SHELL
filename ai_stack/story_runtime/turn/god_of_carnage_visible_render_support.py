"""Visible-render helpers for the God of Carnage turn seam."""

from __future__ import annotations

import json
from typing import Any

from ai_stack.story_runtime.god_of_carnage.god_of_carnage_frozen_vocabulary import (
    GOC_MODULE_ID as GOD_OF_CARNAGE_MODULE_ID,
    canonicalize_goc_actor_id as canonicalize_god_of_carnage_actor_id,
)
from ai_stack.story_runtime.god_of_carnage.god_of_carnage_yaml_authority import (
    goc_actor_display_name,
    goc_actor_identity,
    select_goc_director_surface_hints_for_turn,
    thin_edge_staging_line_from_guidance,
)
from ai_stack.story_runtime.npc_agency.god_of_carnage_npc_transcript_projection import (
    goc_spoken_lines_multi_speaker_row_markers,
)
from ai_stack.story_runtime.opening_shape_normalizer import narration_summary_to_plain_str


def _structured_rows_filtered_for_human_lane(
    rows: Any,
    *,
    human_actor_id: str | None,
    selected_player_role: str | None,
    actor_key: str,
) -> tuple[list[Any], int]:
    """Drop dict rows whose actor matches the live human lane."""
    if not isinstance(rows, list):
        return [], 0
    out: list[Any] = []
    dropped = 0
    for item in rows:
        if not isinstance(item, dict):
            out.append(item)
            continue
        actor_raw = str(item.get(actor_key) or "").strip()
        if not actor_raw:
            out.append(item)
            continue
        canon = canonicalize_god_of_carnage_actor_id(actor_raw) or actor_raw
        if _matches_human_lane(canon, human_actor_id, selected_player_role):
            dropped += 1
            continue
        out.append(item)
    return out, dropped


def _matches_human_lane(
    actor_id: str,
    human_actor_id: str | None,
    selected_player_role: str | None,
) -> bool:
    for candidate in (human_actor_id, selected_player_role):
        normalized = canonicalize_god_of_carnage_actor_id(str(candidate or "").strip())
        if normalized and actor_id == normalized:
            return True
    return False


def _display_text_from_generation_content(raw: str) -> str:
    s = raw.strip()
    if not s.startswith("{"):
        return raw
    try:
        parsed = json.loads(s)
    except json.JSONDecodeError:
        parsed = None
    if not isinstance(parsed, dict):
        return raw
    actor_lines = []
    actor_lines.extend(_coerce_actor_lines(parsed.get("spoken_lines"), actor_key="speaker_id"))
    actor_lines.extend(_coerce_actor_lines(parsed.get("action_lines"), actor_key="actor_id"))
    if str(parsed.get("schema_version") or "").strip() == "runtime_actor_turn_v1" and actor_lines:
        return "\n".join(actor_lines[:4])
    narr = narration_summary_to_plain_str(parsed.get("narration_summary"))
    if not narr.strip():
        narr = narration_summary_to_plain_str(parsed.get("narrative_response"))
    if narr.strip():
        return narr.strip()
    return "\n".join(actor_lines[:4]) if actor_lines else raw


def _coerce_actor_lines(value: Any, *, actor_key: str) -> list[str]:
    if isinstance(value, str):
        line = value.strip()
        return [line] if line else []
    if not isinstance(value, list):
        return []
    lines: list[str] = []
    for item in value:
        if isinstance(item, dict):
            text = str(item.get("text") or "").strip()
            if not text:
                continue
            actor = str(item.get(actor_key) or "").strip()
            actor = goc_actor_display_name(actor, first_name=True) if actor else actor
            tone = str(item.get("tone") or "").strip()
            prefix = f"{actor}: " if actor else ""
            suffix = f" ({tone})" if tone else ""
            lines.append(f"{prefix}{text}{suffix}".strip())
            continue
        line = str(item).strip()
        if line:
            lines.append(line)
    return lines


def _generation_content_and_meta(generation: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    content = str(generation.get("content") or generation.get("text") or "").strip()
    meta = generation.get("metadata") if isinstance(generation.get("metadata"), dict) else {}
    if not content and isinstance(meta.get("raw_content"), str):
        content = meta["raw_content"].strip()
    if content:
        content = _display_text_from_generation_content(content)
    return content, meta


def _prepare_visible_render_context(
    *,
    module_id: str,
    validation_outcome: dict[str, Any],
    generation: dict[str, Any],
    render_context: dict[str, Any] | None,
) -> dict[str, Any]:
    content, generation_meta = _generation_content_and_meta(generation)
    structured_source = generation_meta.get("structured_output")
    structured = dict(structured_source) if isinstance(structured_source, dict) else {}
    rc = render_context if isinstance(render_context, dict) else {}
    human_actor_id = str(rc.get("human_actor_id") or "").strip() or None
    selected_role = str(rc.get("selected_player_role") or "").strip() or None
    spoken_human_drops, action_human_drops = _filter_human_lane_rows(
        module_id=module_id,
        structured=structured,
        human_actor_id=human_actor_id,
        selected_player_role=selected_role,
    )
    actor_lane_validation = (
        validation_outcome.get("actor_lane_validation")
        if isinstance(validation_outcome.get("actor_lane_validation"), dict)
        else None
    )
    actor_lanes_rejected = bool(
        isinstance(actor_lane_validation, dict)
        and actor_lane_validation.get("status") == "rejected"
    )
    markers = _initial_visible_render_markers(
        module_id=module_id,
        structured=structured,
        render_context=rc,
        actor_lane_validation=actor_lane_validation,
        actor_lanes_rejected=actor_lanes_rejected,
    )
    return {
        "content": content,
        "structured": structured,
        "render_context": rc,
        "spoken_human_drops": spoken_human_drops,
        "action_human_drops": action_human_drops,
        "structured_spoken_lines": _coerce_actor_lines(structured.get("spoken_lines"), actor_key="speaker_id"),
        "structured_action_lines": _coerce_actor_lines(structured.get("action_lines"), actor_key="actor_id"),
        "actor_lane_validation": actor_lane_validation,
        "actor_lanes_rejected": actor_lanes_rejected,
        "markers": markers,
    }


def _filter_human_lane_rows(
    *,
    module_id: str,
    structured: dict[str, Any],
    human_actor_id: str | None,
    selected_player_role: str | None,
) -> tuple[int, int]:
    if module_id != GOD_OF_CARNAGE_MODULE_ID or not structured:
        return 0, 0
    if not human_actor_id and not selected_player_role:
        return 0, 0
    filtered_spoken, spoken_drops = _structured_rows_filtered_for_human_lane(
        structured.get("spoken_lines"),
        human_actor_id=human_actor_id,
        selected_player_role=selected_player_role,
        actor_key="speaker_id",
    )
    structured["spoken_lines"] = filtered_spoken
    filtered_action, action_drops = _structured_rows_filtered_for_human_lane(
        structured.get("action_lines"),
        human_actor_id=human_actor_id,
        selected_player_role=selected_player_role,
        actor_key="actor_id",
    )
    structured["action_lines"] = filtered_action
    return spoken_drops, action_drops


def _initial_visible_render_markers(
    *,
    module_id: str,
    structured: dict[str, Any],
    render_context: dict[str, Any],
    actor_lane_validation: dict[str, Any] | None,
    actor_lanes_rejected: bool,
) -> list[str]:
    markers: list[str] = []
    if module_id == GOD_OF_CARNAGE_MODULE_ID:
        markers.extend(
            goc_spoken_lines_multi_speaker_row_markers(
                structured,
                runtime_projection=render_context.get("runtime_projection")
                if isinstance(render_context.get("runtime_projection"), dict)
                else None,
            )
        )
    if actor_lanes_rejected:
        markers.append("actor_lanes_validation_gated")
    if (actor_lane_validation or {}).get("reason") == "no_structured_actor_output_with_selected_responders":
        markers.append("no_actor_lane_output_with_selected_responders")
    return markers


def _render_support(bundle: dict[str, Any]) -> dict[str, Any]:
    support = bundle.setdefault("render_support", {})
    if not isinstance(support, dict):
        support = {}
        bundle["render_support"] = support
    support.setdefault("projection_version", "render_support.v1")
    support.setdefault("player_visible", False)
    return support


def _apply_render_downgrade(bundle: dict[str, Any], context: dict[str, Any]) -> None:
    if not context.get("actor_lanes_rejected"):
        return
    actor_lane_validation = context.get("actor_lane_validation")
    bundle["render_downgrade"] = {
        "actor_lanes": "validation_rejected",
        "reason": actor_lane_validation.get("reason")
        if isinstance(actor_lane_validation, dict)
        else None,
    }


def _basic_bundle(context: dict[str, Any], gm_lines: list[str]) -> dict[str, Any]:
    return {
        "gm_narration": gm_lines,
        "spoken_lines": context["structured_spoken_lines"],
        "action_lines": context["structured_action_lines"],
    }


def _attach_environment_render_support(
    *,
    module_id: str,
    bundle: dict[str, Any],
    context: dict[str, Any],
) -> None:
    rc = context["render_context"]
    environment = rc.get("environment_render_context")
    environment = environment if isinstance(environment, dict) else {}
    if module_id != GOD_OF_CARNAGE_MODULE_ID or not environment:
        return
    _render_support(bundle)["environment"] = environment
    if "environment_state_bound" not in context["markers"]:
        context["markers"].append("environment_state_bound")


def _committed_gm_lines(context: dict[str, Any]) -> list[str]:
    rc = context["render_context"]
    content = context["content"]
    gm_lines = [content] if content else []
    responder_actor_id = str(rc.get("responder_actor_id") or "").strip()
    responder_name = (
        goc_actor_display_name(responder_actor_id, first_name=True)
        if responder_actor_id and goc_actor_identity(responder_actor_id)
        else ""
    )
    player_rc = str(rc.get("player_input") or "").strip()
    live_human_lane = bool(rc.get("human_actor_id") or rc.get("selected_player_role"))
    is_opening_turn = str(rc.get("turn_input_class") or "").strip().lower() == "opening"
    if responder_name and content and not (player_rc and live_human_lane) and not is_opening_turn:
        gm_lines.insert(0, f"{responder_name} reacts immediately.")
    return gm_lines or ["The exchange shifts, and the room adjusts around it."]


def _append_director_hint(
    hints: list[dict[str, str | bool]],
    hint_type: str,
    text: str,
    source: str,
) -> None:
    clean = str(text or "").strip()
    if clean:
        hints.append(
            {
                "hint_type": hint_type,
                "text": clean[:280],
                "source": source,
                "player_visible": False,
            }
        )


def _director_surface_hints_for_commit(context: dict[str, Any]) -> tuple[list[dict[str, str | bool]], bool]:
    rc = context["render_context"]
    hints: list[dict[str, str | bool]] = []
    scene_id = str(rc.get("current_scene_id") or "")
    scene_guidance = rc.get("scene_guidance") if isinstance(rc.get("scene_guidance"), dict) else {}
    pacing_mode = str(rc.get("pacing_mode") or "")
    silence_dec = rc.get("silence_brevity_decision") if isinstance(rc.get("silence_brevity_decision"), dict) else {}
    supplement = ""
    if scene_guidance and scene_id and (pacing_mode == "thin_edge" or silence_dec.get("mode") == "withheld"):
        supplement = thin_edge_staging_line_from_guidance(scene_guidance=scene_guidance, scene_id=scene_id)
    narr_len = len(str(rc.get("proposed_narrative_excerpt") or "").strip() or context["content"])
    used_supplement = bool(supplement and (narr_len < 50 or silence_dec.get("mode") == "withheld"))
    _append_profile_director_hints(hints, context, supplement=supplement, used_supplement=used_supplement)
    for authored in select_goc_director_surface_hints_for_turn(scene_id=scene_id, pacing_mode=pacing_mode):
        _append_director_hint(
            hints,
            str(authored.get("hint_type") or "phase_context"),
            str(authored.get("text") or ""),
            str(authored.get("source") or "hints/"),
        )
    return hints, used_supplement


def _append_profile_director_hints(
    hints: list[dict[str, str | bool]],
    context: dict[str, Any],
    *,
    supplement: str,
    used_supplement: bool,
) -> None:
    rc = context["render_context"]
    profile = rc.get("character_profile_snippet") if isinstance(rc.get("character_profile_snippet"), dict) else {}
    guidance = rc.get("scene_guidance_snippets") if isinstance(rc.get("scene_guidance_snippets"), dict) else {}
    pacing_mode = str(rc.get("pacing_mode") or "")
    silence = rc.get("silence_brevity_decision") if isinstance(rc.get("silence_brevity_decision"), dict) else {}
    narr_len = len(str(rc.get("proposed_narrative_excerpt") or "").strip() or context["content"])
    if used_supplement:
        _append_director_hint(hints, "phase_context", supplement, "scene_guidance.narrative_context")
    role = str(profile.get("formal_role") or profile.get("role") or "").strip()
    if role and (silence.get("mode") == "withheld" or pacing_mode in ("compressed", "multi_pressure")):
        _append_director_hint(hints, "responder_role", role, "character_profile.formal_role")
    tone = str(profile.get("baseline_tone") or "").strip()
    if tone and pacing_mode in ("thin_edge", "multi_pressure"):
        _append_director_hint(hints, "tonal_pressure", tone, "character_profile.baseline_tone")
    phase_arc = str(profile.get("phase_arc_hint") or "").strip()
    if phase_arc and narr_len < 90:
        _append_director_hint(hints, "character_pressure_arc", phase_arc, "character_profile.phase_arc_hint")
    ai_hint = str(guidance.get("ai_guidance_hint") or "").strip()
    if ai_hint and (narr_len < 80 or pacing_mode == "multi_pressure"):
        _append_director_hint(hints, "phase_pressure_cue", ai_hint, "scene_guidance.ai_guidance")


def _actor_ids_in_structured_render(structured: dict[str, Any]) -> set[str]:
    actor_ids: set[str] = set()
    for items_key, actor_key in (("spoken_lines", "speaker_id"), ("action_lines", "actor_id")):
        items = structured.get(items_key)
        if not isinstance(items, list):
            continue
        for item in items:
            if isinstance(item, dict):
                actor_id = str(item.get(actor_key) or "").strip()
                if actor_id:
                    actor_ids.add(actor_id)
    return actor_ids


def _append_human_lane_filter_support(bundle: dict[str, Any], context: dict[str, Any]) -> None:
    spoken_drops = int(context.get("spoken_human_drops") or 0)
    action_drops = int(context.get("action_human_drops") or 0)
    if not (spoken_drops or action_drops):
        return
    _render_support(bundle)["human_lane_structured_filters"] = {
        "spoken_lines_dropped": spoken_drops,
        "action_lines_dropped": action_drops,
    }
    context["markers"].append("generated_human_actor_output_filtered")


def _append_committed_render_support(
    *,
    bundle: dict[str, Any],
    context: dict[str, Any],
    director_surface_hints: list[dict[str, str | bool]],
) -> None:
    _append_human_lane_filter_support(bundle, context)
    _append_multi_actor_support(bundle, context)
    _append_vitality_floor_warning(bundle, context)
    _append_reaction_order_divergence(bundle, context)
    if director_surface_hints:
        _render_support(bundle)["director_surface_hints"] = director_surface_hints


def _append_multi_actor_support(bundle: dict[str, Any], context: dict[str, Any]) -> None:
    actor_ids = _actor_ids_in_structured_render(context["structured"])
    if len(actor_ids) < 2:
        return
    context["markers"].append("multi_actor_realized")
    bundle["multi_actor_render"] = {
        "realized_actor_ids": sorted(actor_ids),
        "actor_count": len(actor_ids),
    }


def _append_vitality_floor_warning(bundle: dict[str, Any], context: dict[str, Any]) -> None:
    rc = context["render_context"]
    if str(rc.get("pacing_mode") or "") != "thin_edge":
        return
    if context["structured_spoken_lines"] or context["structured_action_lines"]:
        return
    notes = rc.get("carry_forward_tension_notes")
    if isinstance(notes, str) and notes.strip():
        _render_support(bundle)["vitality_floor_warning"] = "thin_edge_output_empty_with_prior_tension"


def _append_reaction_order_divergence(bundle: dict[str, Any], context: dict[str, Any]) -> None:
    rc = context["render_context"]
    divergence_reason = rc.get("reaction_order_divergence")
    if not divergence_reason:
        return
    _render_support(bundle)["reaction_order_divergence"] = {
        "divergence": rc.get("divergence", True),
        "reason": divergence_reason,
        "preferred": rc.get("preferred_reaction_order_ids") or [],
        "realized": rc.get("realized_actor_order") or [],
        "not_realized": rc.get("not_realized_actor_ids") or [],
        "non_fatal": rc.get("non_fatal", True),
        "justified": rc.get("justified", False),
        "justification": rc.get("justification"),
    }
    context["markers"].append("reaction_order_divergence")


def _build_non_god_of_carnage_bundle(context: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    content = context["content"]
    bundle = _basic_bundle(context, [content] if content else [])
    _apply_render_downgrade(bundle, context)
    context["markers"].append("non_factual_staging")
    return bundle, context["markers"]


def _build_committed_god_of_carnage_bundle(
    *,
    module_id: str,
    context: dict[str, Any],
) -> tuple[dict[str, Any], list[str]]:
    hints, used_supplement = _director_surface_hints_for_commit(context)
    bundle = _basic_bundle(context, _committed_gm_lines(context))
    _attach_environment_render_support(module_id=module_id, bundle=bundle, context=context)
    _append_committed_render_support(bundle=bundle, context=context, director_surface_hints=hints)
    _apply_render_downgrade(bundle, context)
    context["markers"].append("truth_aligned")
    if used_supplement:
        context["markers"].append("bounded_ambiguity")
    return bundle, context["markers"]


def _build_uncommitted_god_of_carnage_bundle(
    *,
    module_id: str,
    context: dict[str, Any],
    live_player_truth_surface: bool,
) -> tuple[dict[str, Any], list[str]]:
    content = context["content"]
    if live_player_truth_surface:
        bundle = _basic_bundle(context, [content] if content else [])
        marker = "live_truth_surface_no_preview_placeholder"
    else:
        safe = content if content else "(Preview staging — no committed world-state change.)"
        bundle = _basic_bundle(context, [safe])
        marker = "non_factual_staging"
    _attach_environment_render_support(module_id=module_id, bundle=bundle, context=context)
    _apply_render_downgrade(bundle, context)
    context["markers"].append(marker)
    return bundle, context["markers"]


def build_visible_render_bundle(
    *,
    module_id: str,
    committed_result: dict[str, Any],
    validation_outcome: dict[str, Any],
    generation: dict[str, Any],
    live_player_truth_surface: bool,
    render_context: dict[str, Any] | None,
) -> tuple[dict[str, Any], list[str]]:
    context = _prepare_visible_render_context(
        module_id=module_id,
        validation_outcome=validation_outcome,
        generation=generation,
        render_context=render_context,
    )
    approved = validation_outcome.get("status") == "approved"
    committed = committed_result.get("committed_effects") or []
    has_commit = bool(committed) and committed_result.get("commit_applied")
    if module_id != GOD_OF_CARNAGE_MODULE_ID:
        return _build_non_god_of_carnage_bundle(context)
    if has_commit and approved:
        return _build_committed_god_of_carnage_bundle(module_id=module_id, context=context)
    return _build_uncommitted_god_of_carnage_bundle(
        module_id=module_id,
        context=context,
        live_player_truth_surface=live_player_truth_surface,
    )
