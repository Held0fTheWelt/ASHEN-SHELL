"""Playability helpers: quality vs hard-boundary failures, degraded commit, rewrite hints.

Used by the LangGraph runtime turn executor for bounded self-correction. Lives in ``ai_stack``
so the executor does not depend on world-engine application packages.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ai_stack.contracts.expectation_variation_contracts import EXPECTATION_VARIATION_FAILURE_CODES
from ai_stack.contracts.narrative_momentum_contracts import NARRATIVE_MOMENTUM_FAILURE_CODES
from ai_stack.contracts.pacing_rhythm_contracts import PACING_RHYTHM_FAILURE_CODES
from ai_stack.contracts.scene_energy_contracts import SCENE_ENERGY_FAILURE_CODES
from ai_stack.contracts.tonal_consistency_contracts import TONAL_CONSISTENCY_FAILURE_CODES

REWRITEABLE_VALIDATION_REASONS = frozenset(
    {
        "dramatic_alignment_narrative_too_short",
        "dramatic_alignment_insufficient_mass",
        "dramatic_alignment_insufficient_mass_thin_or_silence",
        "dramatic_alignment_withhold_requires_min_beat",
        "opening_leniency_approved",
        "empty_visible_output",
        "meta_output_detected",
        "insufficient_scene_grounding",
        "insufficient_character_reaction",
        "parser_error",
        "model_generation_failed",
        "actor_lane_illegal_actor",
        "actor_lane_invalid_initiative_type",
        "actor_lane_scene_function_mismatch",
        "actor_lane_text_exceeds_transcript_beat",
        "narrator_required_missing",
        "npc_executed_player_action",
        "npc_narrated_player_perception",
        "npc_action_controls_human_actor",
        "npc_force_player_speech",
        "capability_missing_required",
        "forbidden_capability_realized",
        "voice_consistency_drift",
        "npc_initiative_missing_required",
        "npc_initiative_missing_required_secondary",
        "npc_initiative_forbidden_actor_planned",
        "npc_initiative_forbidden_actor_realized",
        *EXPECTATION_VARIATION_FAILURE_CODES,
        *NARRATIVE_MOMENTUM_FAILURE_CODES,
        *SCENE_ENERGY_FAILURE_CODES,
        *PACING_RHYTHM_FAILURE_CODES,
        *TONAL_CONSISTENCY_FAILURE_CODES,
    }
)

HARD_BOUNDARY_REASON_PREFIXES = (
    "scene_",
    "character_",
    "trigger_",
    "boundary_",
    "illegal_",
    "canonical_",
    "hard_forbidden",
)

# Explicit degraded-commit policy table:
# - Allowed: legal-but-weak prose outcomes after retries (tagged degraded_commit).
# - Blocked: structural / legality / parser / empty-structure failures.
DEGRADED_COMMIT_ALLOWED_REASONS = frozenset(
    {
        "dramatic_alignment_narrative_too_short",
        "dramatic_alignment_insufficient_mass",
        "dramatic_alignment_insufficient_mass_thin_or_silence",
        "dramatic_alignment_withhold_requires_min_beat",
        "dramatic_effect_reject_empty_fluency",
        "empty_visible_output",
        "opening_leniency_approved",
        "insufficient_character_reaction",
    }
)

DEGRADED_COMMIT_BLOCK_REASONS = frozenset(
    {
        "actor_lane_illegal_actor",
        "actor_lane_invalid_initiative_type",
        "actor_lane_scene_function_mismatch",
        "malformed_proposed_effect",
        "incomplete_proposed_effect",
        "model_generation_failed",
        "narrator_required_missing",
        "npc_executed_player_action",
        "npc_narrated_player_perception",
        "npc_action_controls_human_actor",
        "npc_force_player_speech",
        "capability_missing_required",
        "forbidden_capability_realized",
        "npc_initiative_missing_required",
        "npc_initiative_missing_required_secondary",
        "npc_initiative_forbidden_actor_planned",
        "npc_initiative_forbidden_actor_realized",
    }
)

DEGRADED_COMMIT_BLOCK_FEEDBACK_CODES = frozenset(
    {
        "parser_error",
        "model_call_failed",
    }
)


@dataclass(slots=True)
class PlayabilityDecision:
    should_retry: bool
    allow_degraded_commit: bool
    feedback_codes: list[str]
    hard_boundary_failure: bool
    preserve_actor_lanes: bool = False


def _reason(outcome: dict[str, Any] | None) -> str:
    if not isinstance(outcome, dict):
        return ""
    return str(outcome.get("reason") or "").strip()


def _append_runtime_aspect_feedback(
    feedback: list[str],
    outcome: dict[str, Any] | None,
) -> None:
    aspect_failure = outcome.get("runtime_aspect_failure") if isinstance(outcome, dict) else None
    if not isinstance(aspect_failure, dict):
        return
    reason = str(aspect_failure.get("failure_reason") or "").strip()
    if reason:
        feedback.append(reason)
    expected_owner = str(aspect_failure.get("expected_owner") or "").strip()
    if expected_owner:
        feedback.append(f"expected_owner:{expected_owner}")


def _append_capability_feedback(
    feedback: list[str],
    outcome: dict[str, Any] | None,
) -> None:
    capability_failure = outcome.get("capability_failure") if isinstance(outcome, dict) else None
    if not isinstance(capability_failure, dict):
        return
    reason = str(capability_failure.get("failure_reason") or "").strip()
    if reason:
        feedback.append(reason)
    missing = capability_failure.get("missing_required_capabilities")
    if isinstance(missing, list):
        for cap in missing[:3]:
            cap_text = str(cap or "").strip()
            if cap_text:
                feedback.append(f"missing_required_capability:{cap_text}")
    violated = capability_failure.get("violated_capabilities")
    if isinstance(violated, list):
        for cap in violated[:3]:
            cap_text = str(cap or "").strip()
            if cap_text:
                feedback.append(f"violated_capability:{cap_text}")


def _append_voice_feedback(
    feedback: list[str],
    outcome: dict[str, Any] | None,
) -> None:
    voice_validation = outcome.get("voice_consistency_validation") if isinstance(outcome, dict) else None
    if not isinstance(voice_validation, dict):
        return
    findings = voice_validation.get("blocking_findings") or voice_validation.get("findings") or []
    if not isinstance(findings, list):
        return
    for finding in findings[:3]:
        if not isinstance(finding, dict):
            continue
        drift_class = str(finding.get("drift_class") or "").strip()
        speaker = str(finding.get("speaker_id") or "").strip()
        if drift_class:
            feedback.append(f"voice_drift:{drift_class}")
        if speaker:
            feedback.append(f"voice_speaker:{speaker}")
        actual_source = str(finding.get("actual_source_actor_id") or "").strip()
        if actual_source:
            feedback.append(f"voice_best_match:{actual_source}")
        evidence = finding.get("evidence") if isinstance(finding.get("evidence"), dict) else {}
        low_dimensions = evidence.get("low_dimensions") if isinstance(evidence, dict) else []
        if not isinstance(low_dimensions, list):
            continue
        for dimension in low_dimensions[:3]:
            dimension_text = str(dimension or "").strip()
            if dimension_text:
                feedback.append(f"voice_dimension:{dimension_text}")


def _append_npc_feedback(
    feedback: list[str],
    outcome: dict[str, Any] | None,
) -> None:
    npc_validation = outcome.get("npc_initiative_validation") if isinstance(outcome, dict) else None
    if not isinstance(npc_validation, dict):
        return
    for code in npc_validation.get("error_codes") or []:
        code_text = str(code or "").strip()
        if code_text:
            feedback.append(code_text)
    for actor_id in npc_validation.get("missing_required_actor_ids") or []:
        actor_text = str(actor_id or "").strip()
        if actor_text:
            feedback.append(f"missing_required_npc_initiative:{actor_text}")


def _append_validation_code_feedback(
    feedback: list[str],
    outcome: dict[str, Any] | None,
    *,
    validation_key: str,
    code_key: str,
) -> None:
    validation = outcome.get(validation_key) if isinstance(outcome, dict) else None
    if not isinstance(validation, dict):
        return
    for code in validation.get(code_key) or []:
        code_text = str(code or "").strip()
        if code_text:
            feedback.append(code_text)


def _append_generation_feedback(
    feedback: list[str],
    *,
    generation: dict[str, Any],
    proposed_state_effects: list[dict[str, Any]] | None,
) -> None:
    raw = str(generation.get("model_raw_text") or generation.get("content") or "")
    if raw.strip().startswith("[mock]"):
        feedback.append("mock_fallback_output")
    if len(raw.strip()) < 80:
        feedback.append("narration_too_short")
    proposed = proposed_state_effects if isinstance(proposed_state_effects, list) else []
    if not proposed:
        feedback.append("no_structured_effects")


def _dedupe_feedback_codes(feedback: list[str]) -> list[str]:
    deduped: list[str] = []
    for code in feedback:
        c = str(code or "").strip()
        if c and c not in deduped:
            deduped.append(c)
    return deduped


def is_hard_boundary_failure(outcome: dict[str, Any] | None) -> bool:
    if isinstance(outcome, dict) and bool(outcome.get("hard_boundary_failure")):
        return True
    reason = _reason(outcome)
    if not reason:
        return False
    if reason.startswith("scene_energy_"):
        return False
    if reason.startswith("pacing_rhythm_"):
        return False
    if reason.startswith("tonal_consistency_"):
        return False
    if reason.startswith("sensory_context_"):
        return False
    if reason.startswith("expectation_variation_"):
        return False
    if reason.startswith("narrative_momentum_"):
        return False
    if reason.startswith(HARD_BOUNDARY_REASON_PREFIXES):
        return True
    geo = outcome.get("dramatic_effect_gate_outcome") if isinstance(outcome, dict) else None
    if isinstance(geo, dict):
        codes = [str(x) for x in geo.get("effect_rationale_codes") or []]
        return any(
            not code.startswith("scene_energy_")
            and not code.startswith("pacing_rhythm_")
            and not code.startswith("tonal_consistency_")
            and not code.startswith("sensory_context_")
            and not code.startswith("expectation_variation_")
            and not code.startswith("narrative_momentum_")
            and code.startswith(HARD_BOUNDARY_REASON_PREFIXES)
            for code in codes
        )
    return False


def collect_playability_feedback_codes(
    *,
    outcome: dict[str, Any] | None,
    generation: dict[str, Any] | None,
    proposed_state_effects: list[dict[str, Any]] | None = None,
) -> list[str]:
    feedback: list[str] = []
    reason = _reason(outcome)
    if reason:
        feedback.append(reason)
    gen = generation if isinstance(generation, dict) else {}
    meta = gen.get("metadata") if isinstance(gen.get("metadata"), dict) else {}
    if gen.get("success") is False:
        feedback.append("model_call_failed")
    if meta.get("langchain_parser_error"):
        feedback.append("parser_error")
    _append_runtime_aspect_feedback(feedback, outcome)
    _append_capability_feedback(feedback, outcome)
    _append_voice_feedback(feedback, outcome)
    _append_npc_feedback(feedback, outcome)
    for validation_key in (
        "scene_energy_validation",
        "pacing_rhythm_validation",
        "tonal_consistency_validation",
        "temporal_control_validation",
        "sensory_context_validation",
    ):
        _append_validation_code_feedback(
            feedback,
            outcome,
            validation_key=validation_key,
            code_key="failure_codes",
        )
    _append_validation_code_feedback(
        feedback,
        outcome,
        validation_key="dramatic_irony_validation",
        code_key="violation_codes",
    )
    for validation_key in ("expectation_variation_validation", "narrative_momentum_validation"):
        _append_validation_code_feedback(
            feedback,
            outcome,
            validation_key=validation_key,
            code_key="failure_codes",
        )
    _append_generation_feedback(
        feedback,
        generation=gen,
        proposed_state_effects=proposed_state_effects,
    )
    return _dedupe_feedback_codes(feedback)


def _degraded_commit_allowed(
    *,
    reason: str,
    feedback: list[str],
    actor_lane_validation: dict[str, Any] | None,
    generation: dict[str, Any] | None = None,
) -> bool:
    """Determine whether degraded commit is legal under explicit policy."""
    if reason in DEGRADED_COMMIT_BLOCK_REASONS:
        return False
    gen = generation if isinstance(generation, dict) else {}
    for code in feedback:
        if code not in DEGRADED_COMMIT_BLOCK_FEEDBACK_CODES:
            continue
        if code == "parser_error" and bool(gen.get("fallback_used")):
            # Graph-managed fallback prose often carries parser errors by
            # construction; allow bounded degraded commit for prose-only
            # outcomes when fallback already succeeded.
            continue
        return False
    if isinstance(actor_lane_validation, dict) and actor_lane_validation.get("status") == "rejected":
        return False
    if reason in DEGRADED_COMMIT_ALLOWED_REASONS:
        return True
    return False


def decide_playability_recovery(
    *,
    turn_number: int,
    attempt_index: int,
    max_attempts: int,
    outcome: dict[str, Any] | None,
    generation: dict[str, Any] | None,
    proposed_state_effects: list[dict[str, Any]] | None = None,
    allow_degraded_commit_after_retries: bool = True,
    actor_lane_validation: dict[str, Any] | None = None,
) -> PlayabilityDecision:
    hard_boundary = is_hard_boundary_failure(outcome)
    feedback = collect_playability_feedback_codes(
        outcome=outcome,
        generation=generation,
        proposed_state_effects=proposed_state_effects,
    )
    status = str((outcome or {}).get("status") or "")
    reason = _reason(outcome)
    rewriteable = False
    if status == "rejected" and not hard_boundary:
        failure_class = str((outcome or {}).get("failure_class") or "").strip()
        rewriteable = (
            bool((outcome or {}).get("recoverable_rejection"))
            or failure_class in {"opening_event_coverage", "recoverable_opening_contract"}
            or reason in REWRITEABLE_VALIDATION_REASONS
            or "parser_error" in feedback
            or "mock_fallback_output" in feedback
            or "narration_too_short" in feedback
            or "no_structured_effects" in feedback
        )
    should_retry = rewriteable and attempt_index <= max_attempts
    allow_degraded = (
        allow_degraded_commit_after_retries
        and rewriteable
        and not should_retry
        and not hard_boundary
        and turn_number <= 12
        and _degraded_commit_allowed(
            reason=reason,
            feedback=feedback,
            actor_lane_validation=actor_lane_validation,
            generation=generation,
        )
    )
    actor_lane_healthy = (
        isinstance(actor_lane_validation, dict)
        and actor_lane_validation.get("status") == "approved"
        and actor_lane_validation.get("reason") == "actor_lane_legal"
    )
    prose_only_reject = reason in {
        "dramatic_alignment_narrative_too_short",
        "dramatic_alignment_insufficient_mass",
        "dramatic_alignment_insufficient_mass_thin_or_silence",
        "dramatic_alignment_withhold_requires_min_beat",
        "dramatic_effect_reject_empty_fluency",
        "empty_visible_output",
    }
    preserve_actor_lanes = actor_lane_healthy and prose_only_reject
    return PlayabilityDecision(
        should_retry=should_retry,
        allow_degraded_commit=allow_degraded,
        feedback_codes=feedback,
        hard_boundary_failure=hard_boundary,
        preserve_actor_lanes=preserve_actor_lanes,
    )

def _rewrite_preserve_prefix(preserve_actor_lanes: bool) -> str:
    if not preserve_actor_lanes:
        return ""
    return (
        "Your actor lanes (primary_responder_id, spoken_lines, action_lines, initiative_events) are structurally valid — "
        "do NOT change them. Only improve narration_summary. Do not invent new actors, new dialogue, or new actions. "
    )


def _rewrite_base_instruction(feedback_codes: list[str]) -> str:
    issues = ", ".join(str(x) for x in feedback_codes[:8]) or "quality_improvement_needed"
    return (
        "Rewrite the previous runtime turn so it is commit-worthy. "
        "Stay strictly inside canonical module boundaries, remain in-scene, avoid meta commentary, "
        "produce concrete narrative progression with visible character reaction, and fix these issues: "
        f"{issues}."
    )


def _actor_lane_rewrite_feedback(
    feedback_codes: list[str],
    allowed_actor_ids: list[str] | None,
) -> str | None:
    actor_lane_issues = [
        code
        for code in feedback_codes
        if code.startswith("actor_lane_")
        or code in {"human_actor_selected_as_responder", "ai_controlled_human_actor"}
    ]
    if actor_lane_issues:
        allowed_str = ", ".join(sorted(allowed_actor_ids or [])) or "the approved responder set"
        actor_feedback = (
            " When populating actor lanes: "
            f"use only these approved actor IDs: {allowed_str}. "
            "Populate spoken_lines with speaker_id, action_lines with actor_id, and initiative_events with valid types. "
            "Do not invent new actor IDs. Do not include the human/player actor in primary_responder_id, "
            "secondary_responder_ids, responder_actor_ids, spoken_lines, action_lines, initiative_events, or narration-as-action."
        )
        return actor_feedback
    return None


def _runtime_authority_rewrite_feedback(feedback_codes: list[str]) -> str | None:
    runtime_aspect_issues = [
        code
        for code in feedback_codes
        if code
        in {
            "narrator_required_missing",
            "npc_executed_player_action",
            "npc_narrated_player_perception",
            "npc_action_controls_human_actor",
            "npc_force_player_speech",
            "capability_missing_required",
            "forbidden_capability_realized",
        }
        or code.startswith("missing_required_capability:")
        or code.startswith("violated_capability:")
        or code.startswith("expected_owner:")
    ]
    if runtime_aspect_issues:
        authority_feedback = (
            " Runtime authority repair: keep the player action owned by the player, "
            "use narrator prose for movement, perception, physical consequences, and scene framing, "
            "and keep NPCs to allowed dialogue or social reaction only. "
            "Do not let an NPC execute the player's action, narrate the player's perception, "
            "or speak for the player. If a required narrator capability is missing, add concise narrator prose "
            "that makes the consequence visible without inventing new facts."
        )
        return authority_feedback
    return None


def _voice_rewrite_feedback(feedback_codes: list[str]) -> str | None:
    voice_issues = [
        code
        for code in feedback_codes
        if code == "voice_consistency_drift"
        or code.startswith("voice_drift:")
        or code.startswith("voice_speaker:")
        or code.startswith("voice_best_match:")
        or code.startswith("voice_dimension:")
    ]
    if voice_issues:
        voice_feedback = (
            " Voice consistency repair: keep every spoken_lines row assigned to the same approved speaker, "
            "but rewrite that speaker's wording so it follows the provided Character Voice Profiles. "
            "Repair flagged semantic voice dimensions such as worldview, register, syntax/rhythm, "
            "rhetorical strategy, and phase alignment. Remove policy-forbidden language markers without adding new actors, new facts, "
            "or narrator explanations to hide the issue."
        )
        return voice_feedback
    return None


def _npc_agency_rewrite_feedback(
    feedback_codes: list[str],
    allowed_actor_ids: list[str] | None,
) -> str | None:
    npc_agency_issues = [
        code
        for code in feedback_codes
        if code.startswith("npc_initiative_")
        or code.startswith("missing_required_npc_initiative:")
    ]
    if npc_agency_issues:
        allowed_str = ", ".join(sorted(allowed_actor_ids or [])) or "the approved NPC responder set"
        npc_agency_feedback = (
            " NPC agency repair: realize every missing required NPC initiative in spoken_lines or action_lines, "
            f"using only these approved actor IDs: {allowed_str}. "
            "At least one nominated secondary NPC must visibly react when the plan requires secondary initiative. "
            "Do not treat initiative_events alone as realization, do not add unapproved actors, "
            "and never move dialogue or action onto the human/player actor."
        )
        return npc_agency_feedback
    return None


def _dramatic_irony_rewrite_feedback(feedback_codes: list[str]) -> str | None:
    dramatic_irony_issues = [
        code
        for code in feedback_codes
        if code.startswith("dramatic_irony_")
        or code == "forbidden_omniscient_hidden_intent_reveal"
    ]
    if dramatic_irony_issues:
        dramatic_irony_feedback = (
            " Dramatic irony repair: remove direct statements of private motive, hidden intent, or planner-only facts. "
            "Keep the same approved actors and scene pressure, but realize the opportunity only through visible behavior, "
            "subtext, misread reaction, or withheld context. Do not explain what an actor secretly plans or wants."
        )
        return dramatic_irony_feedback
    return None


def _prefixed_rewrite_feedback(
    feedback_codes: list[str],
    prefix: str,
    feedback: str,
) -> str | None:
    return feedback if any(code.startswith(prefix) for code in feedback_codes) else None


def _category_rewrite_feedback(feedback_codes: list[str]) -> str | None:
    category_feedback = (
        (
            "scene_energy_",
            " Scene energy repair: preserve the selected scene function and actor boundaries, "
            "but make the structured output satisfy the scene_energy target. Add visible spoken_lines "
            "or action_lines for the required actor response count, keep the turn concise enough for "
            "the target density, and avoid any forbidden transition.",
        ),
        (
            "pacing_rhythm_",
            " Pacing rhythm repair: preserve the selected scene function and actor boundaries, "
            "but shape structured spoken_lines/action_lines to satisfy the pacing_rhythm target. "
            "Respect min/max visible block counts, required actor-turn changes, pause obligations, "
            "and any forced-speech block from the silence decision.",
        ),
        (
            "sensory_context_",
            " Sensory context repair: preserve actor lanes and committed facts, "
            "but realize the selected sensory_context target through structured sensory_context_events. "
            "Use only selected layer_id/source_ref pairs from the dramatic packet, respect layer budget, "
            "and keep sensory texture tied to authored locations, objects, and mood layers.",
        ),
        (
            "genre_awareness_",
            " Genre awareness repair: preserve actor lanes and committed facts, "
            "but realize only the selected genre_awareness profile from the dramatic packet. "
            "Emit genre_awareness_events with selected genre_profile_id/register values, include required conventions, "
            "respect max_genre_signals_per_turn, and remove forbidden or unselected marker_ids.",
        ),
        (
            "tonal_consistency_",
            " Tonal consistency repair: preserve actor lanes and committed facts, "
            "but rewrite visible narration/dialogue so it realizes the selected tonal_consistency target "
            "from the dramatic packet. Keep the required tone dimensions visible through concrete scene pressure, "
            "stay in the allowed register, and remove forbidden marker classes, debug wording, quest framing, "
            "or therapy framing. Do not satisfy this with self-attested labels.",
        ),
        (
            "expectation_variation_",
            " Expectation variation repair: preserve actor lanes and committed facts, "
            "but realize only selected expectation_variation_events from the dramatic packet. "
            "Use selected variation_id/variation_type pairs, include source_refs from required_setup_refs, "
            "respect max_variation_units_per_turn and cooldown, and remove unselected or unearned variation events.",
        ),
        (
            "narrative_momentum_",
            " Narrative momentum repair: preserve actor lanes and committed facts, "
            "but satisfy the selected narrative_momentum target from the dramatic packet. "
            "Emit narrative_momentum_events with event_type, momentum_state, and source_refs; "
            "use allowed_next_states only and add a forward-motion event when required.",
        ),
    )
    for prefix, feedback in category_feedback:
        matched = _prefixed_rewrite_feedback(feedback_codes, prefix, feedback)
        if matched:
            return matched
    return None


def build_rewrite_instruction(feedback_codes: list[str], allowed_actor_ids: list[str] | None = None, preserve_actor_lanes: bool = False) -> str:
    preserve_prefix = _rewrite_preserve_prefix(preserve_actor_lanes)
    base_instruction = _rewrite_base_instruction(feedback_codes)
    for feedback in (
        _actor_lane_rewrite_feedback(feedback_codes, allowed_actor_ids),
        _runtime_authority_rewrite_feedback(feedback_codes),
        _voice_rewrite_feedback(feedback_codes),
        _npc_agency_rewrite_feedback(feedback_codes, allowed_actor_ids),
        _dramatic_irony_rewrite_feedback(feedback_codes),
        _category_rewrite_feedback(feedback_codes),
    ):
        if feedback:
            return preserve_prefix + base_instruction + feedback
    return preserve_prefix + base_instruction


def degrade_validation_outcome(
    outcome: dict[str, Any] | None,
    *,
    reason: str = "degraded_commit_after_retries",
) -> dict[str, Any]:
    base = dict(outcome or {})
    base["status"] = "approved"
    base["reason"] = reason
    geo = base.get("dramatic_effect_gate_outcome") if isinstance(base.get("dramatic_effect_gate_outcome"), dict) else {}
    geo = dict(geo)
    geo["gate_result"] = reason
    geo["rejection_reasons"] = []
    geo["structural_fallback_used"] = bool(geo.get("structural_fallback_used"))
    geo["empty_fluency_risk"] = "managed"
    base["dramatic_effect_gate_outcome"] = geo
    return base
