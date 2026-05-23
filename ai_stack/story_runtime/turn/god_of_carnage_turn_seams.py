"""
Proposal, validation, commit, visible seams helpers
(CANONICAL_TURN_CONTRACT_GOC.md §2).
"""

from __future__ import annotations

from typing import Any

from ai_stack.story_runtime.god_of_carnage.god_of_carnage_dramatic_alignment import extract_proposed_narrative_text
from ai_stack.story_runtime.god_of_carnage.god_of_carnage_field_initialization_envelope import (
    SETTER_SURFACE_RUNTIME_HOST_SESSION,
    goc_uninitialized_field_envelope,
)
from ai_stack.story_runtime.god_of_carnage.god_of_carnage_frozen_vocabulary import (
    DIRECTOR_IMMUTABLE_FIELDS,
    GOC_MODULE_ID,
    assert_transition_pattern,
)
from ai_stack.story_runtime.opening_shape_normalizer import narration_summary_to_plain_str
from ai_stack.story_runtime.turn.god_of_carnage_visible_render_support import (
    build_visible_render_bundle,
)
from ai_stack.story_runtime.turn.god_of_carnage_turn_seams_validation import (
    GOC_NPC_LANE_TEXT_CHAR_CAP_DEFAULT,
    _apply_w5_validation_to_outcome,
    _check_human_actor_violations,
    _check_npc_spoken_action_lane_blob_cap,
    _detect_npc_narrated_player_action_violation,
    _resolved_npc_lane_char_cap,
    run_validation_seam,
)

def strip_director_overwrites_from_structured_output(
    structured: dict[str, Any] | None,
) -> tuple[dict[str, Any] | None, list[dict[str, Any]]]:
    """Remove immutable director fields from model structured output
    (§3.6).
    
    Behaviour, edge cases, and invariants should be inferred from the implementation and public contract of this symbol.
    
    Args:
        structured: ``structured`` (dict[str, Any] |
            None); meaning follows the type and call sites.
    
    Returns:
        tuple[dict[str, Any] | None, list[dict[str, Any]]]:
            Returns a value of type ``tuple[dict[str, Any] | None,
            list[dict[str, Any]]]``; see the function body for structure, error paths, and sentinels.
    """
    if not structured or not isinstance(structured, dict):
        return structured, []
    markers: list[dict[str, Any]] = []
    cleaned = dict(structured)
    for key in DIRECTOR_IMMUTABLE_FIELDS:
        if key in cleaned:
            del cleaned[key]
            markers.append(
                {
                    "marker": "stripped_model_overwrite_attempt",
                    "field": key,
                    "note": "CANONICAL_TURN_CONTRACT_GOC.md §3.6 — model cannot replace director fields.",
                }
            )
    return cleaned, markers


def structured_output_to_proposed_effects(structured: dict[str, Any] | None) -> list[dict[str, Any]]:
    """Map structured output into proposed_state_effects list.

    Behaviour, edge cases, and invariants should be inferred from the implementation and public contract of this symbol.

    Args:
        structured: ``structured`` (dict[str, Any] |
            None); meaning follows the type and call sites.

    Returns:
        list[dict[str, Any]]:
            Returns a value of type ``list[dict[str, Any]]``; see the function body for structure, error paths, and sentinels.
    """
    if not structured or not isinstance(structured, dict):
        return []
    effects = []
    raw = structured.get("proposed_state_effects")
    if not isinstance(raw, list) or not raw:
        raw = structured.get("state_effects")
    if isinstance(raw, list) and raw:
        effects = []
        for item in raw:
            if not isinstance(item, dict):
                continue
            effect = dict(item)
            desc = str(effect.get("description") or "").strip()
            if not desc:
                value = str(effect.get("value") or effect.get("text") or effect.get("summary") or "").strip()
                effect_type = str(effect.get("effect_type") or "").strip()
                target = str(effect.get("target") or "").strip()
                parts = [part for part in (effect_type, target, value) if part]
                if parts:
                    effect["description"] = ": ".join(parts)
            effects.append(effect)
        narr = narration_summary_to_plain_str(structured.get("narration_summary"))
        if not narr.strip():
            narr = narration_summary_to_plain_str(structured.get("narrative_response"))
        if narr.strip():
            effects.append(
                {
                    "effect_type": "narrative_projection",
                    "description": narr.strip()[:4096],
                }
            )
    elif structured.get("effect_type") or structured.get("description"):
        effects = [
            {
                "effect_type": structured.get("effect_type", "narrative_beat"),
                "description": str(structured.get("description", "")),
            }
        ]
    else:
        narr = narration_summary_to_plain_str(structured.get("narration_summary"))
        if not narr.strip():
            narr = narration_summary_to_plain_str(structured.get("narrative_response"))
        if narr.strip():
            effects = [
                {
                    "effect_type": "narrative_proposal",
                    "description": narr.strip()[:4096],
                }
            ]

    if effects:
        semantic_meta = {}
        for key in ("responder_id", "function_type", "social_outcome", "dramatic_direction"):
            if structured.get(key):
                semantic_meta[key] = structured[key]
        if structured.get("emotional_shift") and isinstance(structured["emotional_shift"], dict):
            semantic_meta["emotional_shift"] = structured["emotional_shift"]
        spoken_count = len([x for x in structured.get("spoken_lines") or [] if isinstance(x, dict)])
        action_count = len([x for x in structured.get("action_lines") or [] if isinstance(x, dict)])
        if spoken_count or action_count:
            semantic_meta["actor_lane_count"] = spoken_count + action_count
        if semantic_meta:
            effects[-1].update(semantic_meta)

    return effects


def run_commit_seam(
    *,
    module_id: str,
    validation_outcome: dict[str, Any],
    proposed_state_effects: list[dict[str, Any]],
    candidate_deltas: list[dict[str, Any]] | None = None,
    state_delta_boundary: dict[str, Any] | None = None,
    player_action_frame: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Commit approved effects after all validation passes.

    MVP2: When candidate_deltas and state_delta_boundary are provided,
    protected-path enforcement runs here before any commit is applied.
    This is the commit-seam gate for StateDeltaBoundary.

    Error codes: protected_state_mutation_rejected, state_delta_boundary_violation.
    """
    # MVP2: Protected state mutation check runs at commit seam (before any write).
    if candidate_deltas and isinstance(candidate_deltas, list):
        protected = set(
            (state_delta_boundary or {}).get("protected_paths") or [
                "canonical_scene_order", "canonical_characters", "canonical_relationships",
                "canonical_content_truth", "canonical_props", "canonical_endings",
                "content_module_id", "selected_player_role", "human_actor_id", "actor_lanes",
            ]
        )
        for delta in candidate_deltas:
            if not isinstance(delta, dict):
                continue
            path = str(delta.get("path") or "").strip()
            for root in protected:
                if path == root or path.startswith(root + ".") or path.startswith(root + "["):
                    return {
                        "committed_effects": [],
                        "commit_applied": False,
                        "commit_lane": "goc_commit_seam_v1",
                        "state_delta_rejection": {
                            "error_code": "protected_state_mutation_rejected",
                            "path": path,
                            "protected_root": root,
                        },
                    }

    if validation_outcome.get("status") != "approved":
        return {
            "committed_effects": [],
            "commit_applied": False,
            "commit_lane": "goc_commit_seam_v1",
        }
    if module_id != GOC_MODULE_ID:
        return {
            "committed_effects": [],
            "commit_applied": False,
            "commit_lane": "goc_commit_seam_v1",
        }
    base_out: dict[str, Any] = {
        "committed_effects": list(proposed_state_effects),
        "commit_applied": bool(proposed_state_effects),
        "commit_lane": "goc_commit_seam_v1",
    }
    paf = player_action_frame if isinstance(player_action_frame, dict) else {}
    if paf and validation_outcome.get("status") == "approved":
        nested = paf.get("affordance_resolution") if isinstance(paf.get("affordance_resolution"), dict) else {}
        pol = str(nested.get("action_commit_policy") or "").strip().lower()
        aff_st = str(nested.get("affordance_status") or paf.get("affordance_status") or "").strip().lower()
        verb = str(paf.get("verb") or "").strip().lower()
        applied = bool(base_out["commit_applied"])
        base_out["player_action_authority"] = {
            "player_action_committed": applied and pol == "commit_action",
            "player_speech_committed": (applied and pol == "commit_speech")
            or bool(str(paf.get("speech_text") or "").strip()),
            "action_commit_status": "committed" if applied else "skipped",
            "affordance_status": aff_st,
            "verb": verb,
            "resolved_target_id": paf.get("resolved_target_id"),
            "validation_surface": paf.get("validation_surface"),
        }
    return base_out


def run_visible_render(
    *,
    module_id: str,
    committed_result: dict[str, Any],
    validation_outcome: dict[str, Any],
    generation: dict[str, Any],
    transition_pattern: str,
    live_player_truth_surface: bool = False,
    render_context: dict[str, Any] | None = None,
) -> tuple[dict[str, Any], list[str]]:
    """Build visible_output_bundle aligned with committed truth (§2.2–§2.3)."""
    _ = transition_pattern  # reserved for future bundle tone selection
    return build_visible_render_bundle(
        module_id=module_id,
        committed_result=committed_result,
        validation_outcome=validation_outcome,
        generation=generation,
        live_player_truth_surface=live_player_truth_surface,
        render_context=render_context,
    )


def build_diagnostics_refs(
    *,
    graph_diagnostics: dict[str, Any],
    experiment_preview: bool,
    transition_pattern: str,
    gate_hints: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Project operational diagnostics into canonical refs
    (CANONICAL_TURN_CONTRACT_GOC.md §5).
    
    Behaviour, edge cases, and invariants should be inferred from the implementation and public contract of this symbol.
    
    Args:
        graph_diagnostics: ``graph_diagnostics`` (dict[str, Any]); meaning follows the type and call sites.
        experiment_preview: ``experiment_preview`` (bool); meaning follows the type and call sites.
        transition_pattern: ``transition_pattern`` (str); meaning follows the type and call sites.
        gate_hints: ``gate_hints`` (dict[str, Any] |
            None); meaning follows the type and call sites.
    
    Returns:
        list[dict[str, Any]]:
            Returns a value of type ``list[dict[str, Any]]``; see the function body for structure, error paths, and sentinels.
    """
    tp = assert_transition_pattern(transition_pattern)
    refs: list[dict[str, Any]] = [
        {
            "ref_type": "graph_diagnostics_projection",
            "graph_name": graph_diagnostics.get("graph_name"),
            "graph_version": graph_diagnostics.get("graph_version"),
            "nodes_executed": graph_diagnostics.get("nodes_executed"),
            "node_outcomes": graph_diagnostics.get("node_outcomes"),
            "fallback_path_taken": graph_diagnostics.get("fallback_path_taken"),
            "execution_health": graph_diagnostics.get("execution_health"),
        },
        {
            "ref_type": "experiment_preview",
            "experiment_preview": experiment_preview,
        },
        {
            "ref_type": "transition_pattern",
            "transition_pattern": tp,
        },
    ]
    if gate_hints:
        refs.append({"ref_type": "gate_review_hints", **gate_hints})
    return refs


def repro_metadata_complete(repro: dict[str, Any]) -> bool:
    """GATE_SCORING_POLICY_GOC.md §5.2 — required fields for operator
    questions.
    
    Behaviour, edge cases, and invariants should be inferred from the implementation and public contract of this symbol.
    
    Args:
        repro: ``repro`` (dict[str, Any]); meaning follows the type and call sites.
    
    Returns:
        bool:
            Returns a value of type ``bool``; see the function body for structure, error paths, and sentinels.
    """
    required = (
        "graph_name",
        "trace_id",
        "selected_model",
        "selected_provider",
        "retrieval_domain",
        "retrieval_profile",
        "model_attempted",
        "model_success",
        "adapter_invocation_mode",
        "graph_path_summary",
    )
    return all(repro.get(k) not in (None, "") for k in required)


def _project_turn_basis_field_str(
    state: dict[str, Any],
    key: str,
    *,
    expected_source: str,
) -> str | dict[str, Any]:
    """Describe what ``_project_turn_basis_field_str`` does in one line
    (verb-led summary for this function).
    
    Behaviour, edge cases, and invariants should be inferred from the implementation and public contract of this symbol.
    
    Args:
        state: ``state`` (dict[str, Any]); meaning follows the type and call sites.
        key: ``key`` (str); meaning follows the type and call sites.
        expected_source: ``expected_source`` (str); meaning follows the type and call sites.
    
    Returns:
        str | dict[str, Any]:
            Returns a value of type ``str | dict[str, Any]``; see the function body for structure, error paths, and sentinels.
    """
    raw = state.get(key)
    if isinstance(raw, str) and raw.strip():
        return raw.strip()
    return goc_uninitialized_field_envelope(
        setter_surface=SETTER_SURFACE_RUNTIME_HOST_SESSION,
        expected_source=expected_source,
    )


def _project_turn_number(state: dict[str, Any]) -> int | dict[str, Any]:
    """``_project_turn_number`` — see implementation for behaviour and contracts.
    
    Behaviour, edge cases, and invariants should be inferred from the implementation and public contract of this symbol.
    
    Args:
        state: ``state`` (dict[str, Any]); meaning follows the type and call sites.
    
    Returns:
        int | dict[str, Any]:
            Returns a value of type ``int | dict[str, Any]``; see the function body for structure, error paths, and sentinels.
    """
    tn = state.get("turn_number")
    if isinstance(tn, int) and tn >= 0:
        return tn
    return goc_uninitialized_field_envelope(
        setter_surface=SETTER_SURFACE_RUNTIME_HOST_SESSION,
        expected_source="RuntimeTurnGraphExecutor.run(..., turn_number=<int>) or session store turn counter",
    )


def _roadmap_turn_basis(state: dict[str, Any]) -> dict[str, Any]:
    return {
        "turn_id": _project_turn_basis_field_str(
            state,
            "turn_id",
            expected_source="RuntimeTurnGraphExecutor.run(..., turn_id=<str>) or host-supplied stable turn id",
        ),
        "session_id": _project_turn_basis_field_str(
            state,
            "session_id",
            expected_source="RuntimeTurnGraphExecutor.run(..., session_id=<str>)",
        ),
        "turn_number": _project_turn_number(state),
        "timestamp": _project_turn_basis_field_str(
            state,
            "turn_timestamp_iso",
            expected_source="RuntimeTurnGraphExecutor.run(..., turn_timestamp_iso=<iso8601>)",
        ),
        "initiator_type": _project_turn_basis_field_str(
            state,
            "turn_initiator_type",
            expected_source="RuntimeTurnGraphExecutor.run(..., turn_initiator_type=<str>)",
        ),
        "input_class": _project_turn_basis_field_str(
            state,
            "turn_input_class",
            expected_source="Derived from interpreted_input.kind unless overridden via run(..., turn_input_class=)",
        ),
        "execution_mode": _project_turn_basis_field_str(
            state,
            "turn_execution_mode",
            expected_source="RuntimeTurnGraphExecutor.run(..., turn_execution_mode=<str>)",
        ),
    }


def _roadmap_decision_boundary_records(
    *,
    state: dict[str, Any],
    nodes: list[Any],
) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for node_name in nodes:
        if not isinstance(node_name, str):
            continue
        records.append(
            {
                "decision_name": node_name,
                "decision_class": "runtime_graph_node",
                "owner_layer": "ai_stack.langgraph.langgraph_runtime",
                "input_seam_ref": f"state_before:{node_name}",
                "chosen_path": node_name,
                "validation_result": str((state.get("node_outcomes") or {}).get(node_name) or "ok"),
                "failure_seam_used": "",
                "notes_code": "graph_trace_only",
            }
        )
    return records


def _roadmap_routing_record(routing: dict[str, Any]) -> dict[str, Any]:
    return {
        "route_mode": routing.get("route_mode"),
        "route_reason": routing.get("route_reason_code") or routing.get("reason"),
        "fallback_chain": routing.get("fallback_chain"),
        "fallback_stage_reached": routing.get("fallback_stage_reached"),
        "policy_id_used": routing.get("policy_id_used"),
        "policy_version_used": routing.get("policy_version_used"),
        "selected_model": routing.get("selected_model"),
        "selected_provider": routing.get("selected_provider"),
    }


def _roadmap_retrieval_record(retrieval: dict[str, Any]) -> dict[str, Any]:
    gov = retrieval.get("retrieval_governance_summary")
    gov = gov if isinstance(gov, dict) else {}
    record: dict[str, Any] = {
        "retrieval_used": bool(retrieval.get("hit_count")) or retrieval.get("status") not in (None, "", "empty"),
        "retrieval_domain": retrieval.get("domain"),
        "retrieval_lane": retrieval.get("profile") or retrieval.get("retrieval_route"),
        "retrieval_visibility_class": gov.get("dominant_visibility_class"),
        "authored_truth_refs": list(gov.get("authored_truth_refs") or []),
        "derived_artifact_refs": list(gov.get("derived_artifact_refs") or []),
        "retrieval_governance_result": gov,
    }
    continuity_query_signal = retrieval.get("continuity_query_signal")
    if isinstance(continuity_query_signal, dict):
        record["continuity_query_signal"] = continuity_query_signal
    return record


def _roadmap_realization_record(
    *,
    state: dict[str, Any],
    generation: dict[str, Any],
    gen_meta: dict[str, Any],
    visibility_markers: list[Any],
) -> dict[str, Any]:
    responders = state.get("selected_responder_set") if isinstance(state.get("selected_responder_set"), list) else []
    primary = responders[0] if responders and isinstance(responders[0], dict) else {}
    return {
        "selected_responder": primary.get("actor_id"),
        "selected_scene_function": state.get("selected_scene_function"),
        "selected_pacing_label": state.get("pacing_mode"),
        "visibility_class": visibility_markers[0] if visibility_markers else None,
        "realization_mode": gen_meta.get("adapter_invocation_mode"),
        "degraded_wording_used": bool(generation.get("fallback_used")),
        "safe_wording_fallback_used": bool(generation.get("fallback_used")),
    }


def _roadmap_outcome_record(
    *,
    state: dict[str, Any],
    validation: dict[str, Any],
    committed: dict[str, Any],
    visibility_markers: list[Any],
) -> dict[str, Any]:
    failure_list = state.get("failure_markers") if isinstance(state.get("failure_markers"), list) else []
    return {
        "commit_outcome": "applied" if committed.get("commit_applied") else "not_applied",
        "guard_outcomes": [m for m in failure_list if isinstance(m, dict)],
        "rejected_reasons": [validation.get("reason")] if validation.get("status") == "rejected" else [],
        "continuity_aftereffects": state.get("continuity_impacts"),
        "player_visible_response_class": visibility_markers,
    }


def build_roadmap_dramatic_turn_record(state: dict[str, Any]) -> dict[str, Any]:
    """Roadmap §6.3 six-block projection — read-only aggregate from
    ``RuntimeTurnState`` (single truth surface).
    
    Behaviour, edge cases, and invariants should be inferred from the implementation and public contract of this symbol.
    
    Args:
        state: ``state`` (dict[str, Any]); meaning follows the type and call sites.
    
    Returns:
        dict[str, Any]:
            Returns a value of type ``dict[str, Any]``; see the function body for structure, error paths, and sentinels.
    """
    gd = state.get("graph_diagnostics") if isinstance(state.get("graph_diagnostics"), dict) else {}
    nodes = gd.get("nodes_executed") if isinstance(gd.get("nodes_executed"), list) else []
    routing = state.get("routing") if isinstance(state.get("routing"), dict) else {}
    retrieval = state.get("retrieval") if isinstance(state.get("retrieval"), dict) else {}
    validation = state.get("validation_outcome") if isinstance(state.get("validation_outcome"), dict) else {}
    committed = state.get("committed_result") if isinstance(state.get("committed_result"), dict) else {}
    generation = state.get("generation") if isinstance(state.get("generation"), dict) else {}
    gen_meta = generation.get("metadata") if isinstance(generation.get("metadata"), dict) else {}
    vis = state.get("visibility_class_markers") if isinstance(state.get("visibility_class_markers"), list) else []
    return {
        "turn_basis": _roadmap_turn_basis(state),
        "decision_boundary_records": _roadmap_decision_boundary_records(state=state, nodes=nodes),
        "routing_record": _roadmap_routing_record(routing),
        "retrieval_record": _roadmap_retrieval_record(retrieval),
        "realization_record": _roadmap_realization_record(
            state=state,
            generation=generation,
            gen_meta=gen_meta,
            visibility_markers=vis,
        ),
        "outcome_record": _roadmap_outcome_record(
            state=state,
            validation=validation,
            committed=committed,
            visibility_markers=vis,
        ),
    }


def _operator_turn_metadata(state: dict[str, Any]) -> dict[str, Any]:
    return {
        "session_id": state.get("session_id"),
        "trace_id": state.get("trace_id"),
        "module_id": state.get("module_id"),
        "current_scene_id": state.get("current_scene_id"),
        "turn_id": state.get("turn_id"),
        "turn_number": state.get("turn_number"),
        "turn_timestamp_iso": state.get("turn_timestamp_iso"),
        "turn_initiator_type": state.get("turn_initiator_type"),
        "turn_input_class": state.get("turn_input_class"),
        "turn_execution_mode": state.get("turn_execution_mode"),
    }


def _operator_story_state_fields(
    state: dict[str, Any],
    interpreted_input: dict[str, Any],
) -> dict[str, Any]:
    return {
        "semantic_move_record": state.get("semantic_move_record"),
        "semantic_move_kind": (
            (state.get("semantic_move_record") or {}).get("move_type")
            if isinstance(state.get("semantic_move_record"), dict)
            else None
        ),
        "social_state_record": state.get("social_state_record"),
        "character_mind_records": state.get("character_mind_records"),
        "dramatic_irony_record": state.get("dramatic_irony_record"),
        "scene_plan_record": state.get("scene_plan_record"),
        "interpreted_move": state.get("interpreted_move"),
        "interpreted_input": interpreted_input or None,
    }


def _operator_action_resolution_fields(state: dict[str, Any]) -> dict[str, Any]:
    return {
        "player_action_frame": state.get("player_action_frame")
        if isinstance(state.get("player_action_frame"), dict)
        else None,
        "affordance_resolution": state.get("affordance_resolution")
        if isinstance(state.get("affordance_resolution"), dict)
        else None,
        "scene_affordance_model": state.get("scene_affordance_model")
        if isinstance(state.get("scene_affordance_model"), dict)
        else None,
        "player_local_context": state.get("player_local_context")
        if isinstance(state.get("player_local_context"), dict)
        else None,
        "local_context_transition": state.get("local_context_transition")
        if isinstance(state.get("local_context_transition"), dict)
        else None,
        "narrator_consequence_plan": state.get("narrator_consequence_plan")
        if isinstance(state.get("narrator_consequence_plan"), dict)
        else None,
    }


def _operator_interpreted_flags(interpreted_input: dict[str, Any]) -> dict[str, Any]:
    return {
        "player_input_kind": interpreted_input.get("player_input_kind") if interpreted_input else None,
        "player_action_committed": bool(interpreted_input.get("player_action_committed")) if interpreted_input else False,
        "player_speech_committed": bool(interpreted_input.get("player_speech_committed")) if interpreted_input else False,
        "narrator_response_expected": bool(interpreted_input.get("narrator_response_expected")) if interpreted_input else False,
        "npc_response_expected": bool(interpreted_input.get("npc_response_expected")) if interpreted_input else False,
    }


def _operator_scene_selection_fields(
    state: dict[str, Any],
    intent_surface_diag: dict[str, Any],
) -> dict[str, Any]:
    scene_assessment = state.get("scene_assessment") if isinstance(state.get("scene_assessment"), dict) else {}
    scene_plan = state.get("scene_plan_record") if isinstance(state.get("scene_plan_record"), dict) else {}
    multi_pressure = (scene_assessment.get("multi_pressure_resolution") or {})
    return {
        "scene_director_selection_source": multi_pressure.get("selection_source"),
        "planner_rationale_codes": scene_plan.get("planner_rationale_codes") if scene_plan else None,
        "keyword_scene_candidates_used": bool(multi_pressure.get("keyword_scene_candidates_used")),
        "intent_surface_diagnostics": intent_surface_diag or None,
        "npc_narrated_player_action_violation": bool(intent_surface_diag.get("npc_narrated_player_action_violation")),
    }


def _operator_runtime_surface_fields(state: dict[str, Any]) -> dict[str, Any]:
    return {
        "scene_assessment": state.get("scene_assessment"),
        "selected_responder_set": state.get("selected_responder_set"),
        "selected_scene_function": state.get("selected_scene_function"),
        "pacing_mode": state.get("pacing_mode"),
        "silence_brevity_decision": state.get("silence_brevity_decision"),
        "proposed_state_effects": state.get("proposed_state_effects"),
        "validation_outcome": state.get("validation_outcome"),
        "dramatic_effect_outcome": state.get("dramatic_effect_outcome"),
        "committed_result": state.get("committed_result"),
        "visible_output_bundle": state.get("visible_output_bundle"),
        "continuity_impacts": state.get("continuity_impacts"),
        "visibility_class_markers": state.get("visibility_class_markers"),
        "failure_markers": state.get("failure_markers"),
        "fallback_markers": state.get("fallback_markers"),
        "quality_class": state.get("quality_class"),
        "degradation_signals": state.get("degradation_signals"),
        "degradation_summary": state.get("degradation_summary"),
        "diagnostics_refs": state.get("diagnostics_refs"),
        "experiment_preview": state.get("experiment_preview"),
        "transition_pattern": state.get("transition_pattern"),
        "routing": state.get("routing"),
        "dramatic_turn_record": build_roadmap_dramatic_turn_record(state),
    }


def _operator_telemetry_fields(state: dict[str, Any]) -> dict[str, Any]:
    return {
        "actor_survival_telemetry": state.get("actor_survival_telemetry"),
        "vitality_telemetry_v1": (
            ((state.get("actor_survival_telemetry") or {}).get("vitality_telemetry_v1"))
            if isinstance(state.get("actor_survival_telemetry"), dict)
            else None
        ),
    }


def _operator_graph_diagnostics_summary(
    graph_diagnostics: dict[str, Any],
    repro_metadata: dict[str, Any],
) -> dict[str, Any]:
    return {
        "graph_diagnostics_summary": {
            "graph_name": graph_diagnostics.get("graph_name"),
            "graph_version": graph_diagnostics.get("graph_version"),
            "nodes_executed": graph_diagnostics.get("nodes_executed"),
            "node_outcomes": graph_diagnostics.get("node_outcomes"),
            "execution_health": graph_diagnostics.get("execution_health"),
            "fallback_path_taken": graph_diagnostics.get("fallback_path_taken"),
            "repro_complete": repro_metadata.get("repro_complete"),
        }
    }


def build_operator_canonical_turn_record(state: dict[str, Any]) -> dict[str, Any]:
    """Single JSON-serializable operator view over post-`package_output`
    state (CANONICAL_TURN_CONTRACT_GOC.md §8).
    
    Behaviour, edge cases, and invariants should be inferred from the implementation and public contract of this symbol.
    
    Args:
        state: ``state`` (dict[str, Any]); meaning follows the type and call sites.
    
    Returns:
        dict[str, Any]:
            Returns a value of type ``dict[str, Any]``; see the function body for structure, error paths, and sentinels.
    """
    gd = state.get("graph_diagnostics") if isinstance(state.get("graph_diagnostics"), dict) else {}
    repro = gd.get("repro_metadata") if isinstance(gd.get("repro_metadata"), dict) else {}
    interpreted_input = state.get("interpreted_input") if isinstance(state.get("interpreted_input"), dict) else {}
    validation_outcome = state.get("validation_outcome") if isinstance(state.get("validation_outcome"), dict) else {}
    intent_surface_diag = (
        validation_outcome.get("intent_surface_diagnostics")
        if isinstance(validation_outcome.get("intent_surface_diagnostics"), dict)
        else {}
    )
    out = {"turn_metadata": _operator_turn_metadata(state)}
    out.update(_operator_story_state_fields(state, interpreted_input))
    out.update(_operator_action_resolution_fields(state))
    out.update(_operator_interpreted_flags(interpreted_input))
    out.update(_operator_scene_selection_fields(state, intent_surface_diag))
    out.update(_operator_runtime_surface_fields(state))
    out.update(_operator_telemetry_fields(state))
    out.update(_operator_graph_diagnostics_summary(gd, repro))
    return out


_SCENE_FN_TO_CONTINUITY_PRIMARY: dict[str, str] = {
    "reveal_surface": "revealed_fact",
    "redirect_blame": "blame_pressure",
    "escalate_conflict": "situational_pressure",
    "repair_or_stabilize": "repair_attempt",
    "probe_motive": "situational_pressure",
    "establish_pressure": "situational_pressure",
    "withhold_or_evade": "silent_carry",
    "scene_pivot": "refused_cooperation",
}


def build_goc_continuity_impacts_on_commit(
    *,
    module_id: str,
    selected_scene_function: str,
    proposed_state_effects: list[dict[str, Any]],
    social_outcome: str | None = None,
    emotional_shift: dict[str, Any] | None = None,
    dramatic_direction: str | None = None,
) -> list[dict[str, Any]]:
    """Emit one or more frozen continuity classes after a successful commit
    (bounded, YAML-vocabulary aligned).
    
    Behaviour, edge cases, and invariants should be inferred from the implementation and public contract of this symbol.
    
    Args:
        module_id: ``module_id`` (str); meaning follows the type and call sites.
        selected_scene_function: ``selected_scene_function`` (str); meaning follows the type and call sites.
        proposed_state_effects: ``proposed_state_effects`` (list[dict[str, Any]]); meaning follows the type and call sites.
    
    Returns:
        list[dict[str, Any]]:
            Returns a value of type ``list[dict[str, Any]]``; see the function body for structure, error paths, and sentinels.
    """
    if module_id != GOC_MODULE_ID:
        return []
    primary = _SCENE_FN_TO_CONTINUITY_PRIMARY.get(selected_scene_function)
    if not primary:
        primary = "situational_pressure"
    impacts: list[dict[str, Any]] = [
        {"class": primary, "note": f"committed_scene_function:{selected_scene_function}"},
    ]

    # Model-driven continuity classification (higher precision than keyword scanning)
    _SOCIAL_OUTCOME_TO_CLASS = {
        "alliance_possible": "alliance_shift",
        "alliance_shift": "alliance_shift",
        "conflict_escalation": "tension_escalation",
        "conflict_resolution": "repair_attempt",
        "tension_escalates": "tension_escalation",
        "tension_escalation": "tension_escalation",
        "dignity_injury": "dignity_injury",
        "blame_shift": "blame_pressure",
        "repair_attempt": "repair_attempt",
    }
    if social_outcome:
        mapped = _SOCIAL_OUTCOME_TO_CLASS.get(social_outcome.lower().strip())
        if mapped and mapped != primary and len(impacts) < 2:
            impacts.append({"class": mapped, "note": f"model_social_outcome:{social_outcome}"})
    if dramatic_direction in ("escalate",) and len(impacts) < 2:
        impacts.append({"class": "tension_escalation", "note": "model_dramatic_direction:escalate"})
    elif dramatic_direction in ("defuse", "calm") and len(impacts) < 2:
        impacts.append({"class": "repair_attempt", "note": f"model_dramatic_direction:{dramatic_direction}"})

    _ = proposed_state_effects
    return impacts[:2]
