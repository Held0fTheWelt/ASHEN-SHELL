"""Unsharded manager helper `_build_langfuse_path_summary` (Wave 1)."""
from __future__ import annotations

from .._deps import *

def _build_langfuse_path_summary(
    *,
    session: "StorySession",
    graph_state: dict[str, Any],
    event: dict[str, Any],
) -> dict[str, Any]:
    nodes = _str_list(graph_state.get("nodes_executed"))
    routing = graph_state.get("routing") if isinstance(graph_state.get("routing"), dict) else {}
    generation = graph_state.get("generation") if isinstance(graph_state.get("generation"), dict) else {}
    interpreted_input = (
        graph_state.get("interpreted_input")
        if isinstance(graph_state.get("interpreted_input"), dict)
        else {}
    )
    semantic_move_record = (
        graph_state.get("semantic_move_record")
        if isinstance(graph_state.get("semantic_move_record"), dict)
        else {}
    )
    scene_plan_record = (
        graph_state.get("scene_plan_record")
        if isinstance(graph_state.get("scene_plan_record"), dict)
        else {}
    )
    scene_assessment = (
        graph_state.get("scene_assessment")
        if isinstance(graph_state.get("scene_assessment"), dict)
        else {}
    )
    multi_pressure_resolution = (
        scene_assessment.get("multi_pressure_resolution")
        if isinstance(scene_assessment.get("multi_pressure_resolution"), dict)
        else {}
    )
    gen_meta = generation.get("metadata") if isinstance(generation.get("metadata"), dict) else {}
    validation = (
        graph_state.get("validation_outcome")
        if isinstance(graph_state.get("validation_outcome"), dict)
        else {}
    )
    actor_lane_validation = (
        validation.get("actor_lane_validation")
        if isinstance(validation.get("actor_lane_validation"), dict)
        else {}
    )
    committed = (
        graph_state.get("committed_result")
        if isinstance(graph_state.get("committed_result"), dict)
        else {}
    )
    telemetry = (
        graph_state.get("actor_survival_telemetry")
        if isinstance(graph_state.get("actor_survival_telemetry"), dict)
        else {}
    )
    vitality = (
        telemetry.get("vitality_telemetry_v1")
        if isinstance(telemetry.get("vitality_telemetry_v1"), dict)
        else {}
    )
    passivity = (
        telemetry.get("passivity_diagnosis_v1")
        if isinstance(telemetry.get("passivity_diagnosis_v1"), dict)
        else {}
    )
    governance = (
        event.get("runtime_governance_surface")
        if isinstance(event.get("runtime_governance_surface"), dict)
        else {}
    )
    human_input_attribution = (
        event.get("human_input_attribution")
        if isinstance(event.get("human_input_attribution"), dict)
        else {}
    )
    retrieval = graph_state.get("retrieval") if isinstance(graph_state.get("retrieval"), dict) else {}
    structured = gen_meta.get("structured_output")
    if structured is None:
        structured = generation.get("structured_output")
    graph_errors = _str_list(graph_state.get("graph_errors"))
    _ledger_src = (
        graph_state.get("turn_aspect_ledger")
        if isinstance(graph_state.get("turn_aspect_ledger"), dict)
        else event.get("turn_aspect_ledger")
        if isinstance(event.get("turn_aspect_ledger"), dict)
        else None
    )
    turn_aspect_ledger = normalize_runtime_aspect_ledger(_ledger_src) if isinstance(_ledger_src, dict) else None
    usage_details = gen_meta.get("usage_details") if isinstance(gen_meta.get("usage_details"), dict) else {}
    _u_in = int(usage_details.get("input") or gen_meta.get("tokens_prompt") or 0)
    _u_out = int(usage_details.get("output") or gen_meta.get("tokens_completion") or 0)
    _u_tot = int(usage_details.get("total") or gen_meta.get("tokens_total") or 0)
    if _u_tot <= 0 and (_u_in > 0 or _u_out > 0):
        _u_tot = _u_in + _u_out
    usage_total = _u_tot
    _graph_pkg = event.get("graph") if isinstance(event.get("graph"), dict) else {}
    _graph_name = str(_graph_pkg.get("graph_name") or "").strip() or None
    _route_id = str(routing.get("route_id") or "").strip()
    _route_family = str(routing.get("route_family") or "").strip()
    _langfuse_prompt_parts = [p for p in (_route_id, _route_family, _graph_name) if p]
    _langfuse_prompt_name = "/".join(_langfuse_prompt_parts) if _langfuse_prompt_parts else None
    _lat_raw = gen_meta.get("generation_latency_ms")
    _lat_ms = float(_lat_raw) if isinstance(_lat_raw, (int, float)) else None
    _tps_out: float | None = None
    if _lat_ms is not None and _lat_ms > 0 and _u_out > 0:
        _tps_out = round(_u_out / (_lat_ms / 1000.0), 4)
    _streaming = gen_meta.get("llm_invocation_streaming")
    _ttft_ms: float | None = None
    if _lat_ms is not None and _lat_ms >= 0:
        # Non-streaming HTTP completions: no true first-token boundary; use full call latency.
        if _streaming is False:
            _ttft_ms = round(_lat_ms, 3)
    projection = session.runtime_projection if isinstance(session.runtime_projection, dict) else {}
    provenance = session.content_provenance if isinstance(session.content_provenance, dict) else {}
    trace_classification = (
        provenance.get("trace_classification")
        if isinstance(provenance.get("trace_classification"), dict)
        else {}
    )
    runtime_mode = str(
        trace_classification.get("runtime_mode")
        or projection.get("runtime_mode")
        or "solo_story"
    ).strip() or "solo_story"
    trace_origin = str(trace_classification.get("trace_origin") or "").strip() or "unknown"
    execution_tier = str(trace_classification.get("execution_tier") or "").strip()
    if not execution_tier:
        execution_tier = _infer_execution_tier_for_pytest() if trace_origin == "pytest" else "diagnostic"
    canonical_player_flow = bool(trace_classification.get("canonical_player_flow", False))
    test_case_id = trace_classification.get("test_case_id")
    environment = _observability_environment_for_session(session)
    local_evidence_meta = local_langfuse_evidence_metadata()
    if local_evidence_meta.get("environment"):
        environment = str(local_evidence_meta.get("environment") or "local")

    _spr = (
        str((session.runtime_projection or {}).get("selected_player_role") or "").strip()
        if isinstance(session.runtime_projection, dict)
        else ""
    )
    _player_input_kind = str(interpreted_input.get("player_input_kind") or "").strip().lower()
    _semantic_move_kind = str(semantic_move_record.get("move_type") or "").strip()
    _subtext_record = (
        semantic_move_record.get("subtext")
        if isinstance(semantic_move_record.get("subtext"), dict)
        else {}
    )
    _subtext_contract_pass = True
    if semantic_move_record:
        _subtext_contract_pass = (
            (not _semantic_move_kind or _semantic_move_kind in SEMANTIC_MOVE_TYPES)
            and bool(str(_subtext_record.get("surface_mode") or "").strip())
            and bool(str(_subtext_record.get("hidden_intent_hypothesis") or "").strip())
            and bool(str(_subtext_record.get("subtext_function") or "").strip())
            and bool(str(_subtext_record.get("sincerity_band") or "").strip())
        )
    _intent_surface_contract_pass = True
    if _player_input_kind:
        _intent_surface_contract_pass = (
            _player_input_kind in PLAYER_INPUT_KINDS
            and isinstance(interpreted_input.get("player_action_committed"), bool)
            and isinstance(interpreted_input.get("player_speech_committed"), bool)
            and isinstance(interpreted_input.get("narrator_response_expected"), bool)
            and isinstance(interpreted_input.get("npc_response_expected"), bool)
        )
    _player_input_attribution_pass = (
        bool(human_input_attribution.get("player_input_attribution_pass"))
        if "player_input_attribution_pass" in human_input_attribution
        else True
    )
    _semantic_move_alignment_pass = True
    if _semantic_move_kind:
        _semantic_move_alignment_pass = True
    if is_question_punctuation_probe_guarded(_player_input_kind) and _semantic_move_kind:
        _semantic_move_alignment_pass = (
            _semantic_move_alignment_pass
            and _semantic_move_kind not in FORBIDDEN_NON_SPEECH_ACTION_SEMANTIC_MOVES
        )
    _npc_action_narration_boundary_pass = not bool(
        (
            validation.get("intent_surface_diagnostics")
            if isinstance(validation.get("intent_surface_diagnostics"), dict)
            else {}
        ).get("npc_narrated_player_action_violation")
    )
    _runtime_profile_id = (
        _runtime_profile_id_from_projection(projection)
        or (
            turn_aspect_ledger.get("runtime_profile_id")
            if isinstance(turn_aspect_ledger, dict)
            else None
        )
    )
    if isinstance(turn_aspect_ledger, dict) and _runtime_profile_id and not turn_aspect_ledger.get("runtime_profile_id"):
        turn_aspect_ledger = dict(turn_aspect_ledger)
        turn_aspect_ledger["runtime_profile_id"] = _runtime_profile_id
        turn_aspect_ledger = normalize_runtime_aspect_ledger(turn_aspect_ledger)
    self_correction = (
        graph_state.get("self_correction")
        if isinstance(graph_state.get("self_correction"), dict)
        else {}
    )
    _sc_attempts_raw = (
        self_correction.get("attempts")
        if isinstance(self_correction.get("attempts"), list)
        else []
    )
    _sc_attempts = [item for item in _sc_attempts_raw if isinstance(item, dict)]
    _first_sc = _sc_attempts[0] if _sc_attempts else {}
    _last_sc = _sc_attempts[-1] if _sc_attempts else {}
    _sc_attempted = gen_meta.get("self_correction_attempted")
    if _sc_attempted is None and self_correction:
        _sc_attempted = bool(_sc_attempts)
    _sc_attempt_count = gen_meta.get("self_correction_attempt_count")
    if _sc_attempt_count is None and self_correction:
        _sc_attempt_count = self_correction.get("attempt_count")
        if _sc_attempt_count is None:
            _sc_attempt_count = len(_sc_attempts)
    _sc_success = gen_meta.get("self_correction_success")
    if _sc_success is None and self_correction:
        _sc_success = (
            bool(_last_sc.get("success")) and not _last_sc.get("parser_error")
            if _last_sc
            else False
        )
    _sc_model = gen_meta.get("self_correction_model")
    if _sc_model is None and _last_sc:
        _sc_model = _last_sc.get("candidate_model")
    _sc_trigger_source = gen_meta.get("self_correction_trigger_source")
    if _sc_trigger_source is None and _first_sc:
        _sc_trigger_source = _first_sc.get("trigger_source")
    _runtime_aspect_failure_before_retry = gen_meta.get("runtime_aspect_failure_before_retry")
    if _runtime_aspect_failure_before_retry is None and _first_sc:
        _runtime_aspect_failure_before_retry = _first_sc.get("runtime_aspect_failure_before_retry")
    _capability_failure_before_retry = gen_meta.get("capability_failure_before_retry")
    if _capability_failure_before_retry is None and _first_sc:
        _capability_failure_before_retry = _first_sc.get("capability_failure_before_retry")
    _sc_resolved_failure = gen_meta.get("self_correction_resolved_failure")
    if _sc_resolved_failure is None and self_correction:
        _sc_resolved_failure = any(bool(item.get("resolved_failure")) for item in _sc_attempts)
\
    branching_forecast = (
        event.get("branching_forecast")
        if isinstance(event.get("branching_forecast"), dict)
        else graph_state.get("branching_forecast")
        if isinstance(graph_state.get("branching_forecast"), dict)
        else turn_aspect_ledger.get("branching_forecast")
        if isinstance(turn_aspect_ledger, dict) and isinstance(turn_aspect_ledger.get("branching_forecast"), dict)
        else {}
    )
    branch_option_count = int(branching_forecast.get("option_count") or 0) if branching_forecast else 0
    branching_forecast_present = (
        bool(branching_forecast)
        and str(branching_forecast.get("status") or "").strip() == "forecasted"
        and branch_option_count > 0
    )
    inactive_branches_non_authoritative = bool(
        branching_forecast
        and branching_forecast.get("forecast_only") is True
        and branching_forecast.get("authoritative") is False
        and branching_forecast.get("inactive_branches_authoritative") is False
        and branching_forecast.get("mutates_canonical_state") is False
    )
    _capability_projection = (
        turn_aspect_ledger.get("capability")
        if isinstance(turn_aspect_ledger, dict) and isinstance(turn_aspect_ledger.get("capability"), dict)
        else {}
    )
    _capability_selection_projection = (
        turn_aspect_ledger.get("capability_selection")
        if isinstance(turn_aspect_ledger, dict)
        and isinstance(turn_aspect_ledger.get("capability_selection"), dict)
        else {}
    )
    _validator_dispatch_report = (
        turn_aspect_ledger.get("validator_dispatch_report")
        if isinstance(turn_aspect_ledger, dict)
        and isinstance(turn_aspect_ledger.get("validator_dispatch_report"), dict)
        else {}
    )
    _readiness_policy_input = (
        graph_state.get("readiness_policy_input")
        if isinstance(graph_state.get("readiness_policy_input"), dict)
        else turn_aspect_ledger.get("readiness_policy_input")
        if isinstance(turn_aspect_ledger, dict)
        and isinstance(turn_aspect_ledger.get("readiness_policy_input"), dict)
        else None
    )
    narrator_path_selected = str(graph_state.get("director_path_mode") or "").strip() == "narrator_path"
    summary = {
        "contract": "story_runtime_path_observability.v1",
        "session_id": session.session_id,
        "module_id": session.module_id,
        "runtime_profile_id": _runtime_profile_id,
        "environment": environment,
        "turn_number": event.get("turn_number"),
        "turn_kind": event.get("turn_kind"),
        "raw_player_input": str(event.get("raw_input") or graph_state.get("player_input") or "").strip() or None,
        "turn_aspect_ledger_present": bool(
            isinstance(turn_aspect_ledger, dict)
            and isinstance(turn_aspect_ledger.get("turn_aspect_ledger"), dict)
        ),
        "turn_aspect_ledger": turn_aspect_ledger,
        "branching_forecast": branching_forecast,
        "branching_forecast_status": branching_forecast.get("status") if branching_forecast else None,
        "branching_forecast_present": branching_forecast_present,
        "branch_option_count": branch_option_count,
        "branching_forecast_only": bool(branching_forecast.get("forecast_only")) if branching_forecast else False,
        "inactive_branches_non_authoritative": inactive_branches_non_authoritative,
        "inactive_branches_mutate_state": bool(branching_forecast.get("mutates_canonical_state"))
        if branching_forecast
        else False,
        "selected_player_role": _spr or None,
        "human_actor_id": (session.runtime_projection or {}).get("human_actor_id") if isinstance(session.runtime_projection, dict) else None,
        "player_role_display_name": goc_player_role_display_name(_spr or None),
        "session_input_language": getattr(session, "session_input_language", None) or getattr(session, "session_output_language", None) or DEFAULT_SESSION_LANGUAGE,
        "session_output_language": getattr(session, "session_output_language", None) or DEFAULT_SESSION_LANGUAGE,
        "npc_actor_ids": list((session.runtime_projection or {}).get("npc_actor_ids") or []) if isinstance(session.runtime_projection, dict) else [],
        "nodes_executed": nodes,
        "route_model_called": False if narrator_path_selected else "route_model" in nodes or bool(routing),
        "invoke_model_called": False if narrator_path_selected else "invoke_model" in nodes,
        "fallback_model_called": "fallback_model" in nodes or bool(generation.get("fallback_used")),
        "graph_fallback_node_called": "fallback_model" in nodes,
        "retrieval_called": False if narrator_path_selected else "retrieve_context" in nodes or bool(retrieval),
        "validation_called": "validate_seam" in nodes or bool(validation),
        "commit_called": "commit_seam" in nodes or bool(committed),
        "render_visible_called": "render_visible" in nodes or isinstance(event.get("visible_output_bundle"), dict),
        "route_id": routing.get("route_id"),
        "route_family": routing.get("route_family"),
        "selected_provider": routing.get("selected_provider"),
        "selected_model": routing.get("selected_model"),
        "fallback_model": routing.get("fallback_model"),
        "fallback_chain": routing.get("fallback_chain"),
        "registered_adapter_providers": routing.get("registered_adapter_providers"),
        "generation_execution_mode": routing.get("generation_execution_mode"),
        "adapter": gen_meta.get("adapter"),
        "api_model": gen_meta.get("model"),
        "adapter_invocation_mode": gen_meta.get("adapter_invocation_mode"),
        # ADR-0033 §13.10 primary-vs-final clarity. ``adapter``/``api_model`` describe
        # the FINAL committed invocation (e.g. ldss_fallback after live opening failure).
        # The primary-attempt block surfaces what live route was tried first so
        # operators do not misread degraded fallback traces as healthy openai turns.
        "primary_attempt_adapter": gen_meta.get("primary_attempt_adapter"),
        "primary_attempt_model": gen_meta.get("primary_attempt_model"),
        "primary_attempt_provider": (
            gen_meta.get("primary_attempt_provider")
            or routing.get("selected_provider")
        ),
        "primary_attempt_selected_model": (
            gen_meta.get("primary_attempt_selected_model")
            or routing.get("selected_model")
        ),
        "primary_attempt_invocation_mode": gen_meta.get("primary_attempt_invocation_mode"),
        "final_adapter": gen_meta.get("final_adapter") or gen_meta.get("adapter"),
        "final_adapter_invocation_mode": (
            gen_meta.get("final_adapter_invocation_mode")
            or gen_meta.get("adapter_invocation_mode")
        ),
        "fallback_reason": gen_meta.get("fallback_reason") or routing.get("fallback_reason"),
        "ldss_fallback_after_live_opening_failure": bool(
            gen_meta.get("ldss_fallback_after_live_opening_failure")
        ),
        "generation_attempted": bool(generation.get("attempted")),
        "generation_success": generation.get("success"),
        "generation_error": _short_text(generation.get("error") or gen_meta.get("error")),
        "generation_fallback_used": bool(generation.get("fallback_used")),
        "parser_error": _short_text(gen_meta.get("langchain_parser_error") or generation.get("parser_error")),
        "structured_output_present": isinstance(structured, dict),
        "structured_output_keys": sorted(structured.keys()) if isinstance(structured, dict) else [],
        # PRIMARY-PARSER-EVIDENCE-01: primary attempt diagnosis fields.
        "primary_attempt_api_success": gen_meta.get("primary_attempt_api_success"),
        "primary_attempt_parser_error_present": gen_meta.get("primary_attempt_parser_error_present"),
        "primary_attempt_parser_error": gen_meta.get("primary_attempt_parser_error"),
        "primary_attempt_structured_output_present": gen_meta.get("primary_attempt_structured_output_present"),
        "primary_attempt_raw_output_sha256": gen_meta.get("primary_attempt_raw_output_sha256"),
        "primary_attempt_raw_output_excerpt": gen_meta.get("primary_attempt_raw_output_excerpt"),
        "self_correction_attempted": _sc_attempted,
        "self_correction_attempt_count": _sc_attempt_count,
        "self_correction_success": _sc_success,
        "self_correction_model": _sc_model,
        "self_correction_trigger_source": _sc_trigger_source,
        "runtime_aspect_failure_before_retry": _runtime_aspect_failure_before_retry,
        "capability_failure_before_retry": _capability_failure_before_retry,
        "self_correction_resolved_failure": _sc_resolved_failure,
        "usage_available": bool(gen_meta.get("usage_available")) or usage_total > 0,
        "usage_source": gen_meta.get("usage_source"),
        "usage_details": {
            "input": _u_in,
            "output": _u_out,
            "total": usage_total,
        },
        "langfuse_prompt_name": _langfuse_prompt_name,
        "provided_model_name": str(gen_meta.get("model") or "").strip() or None,
        "generation_latency_ms": round(_lat_ms, 3) if isinstance(_lat_ms, (int, float)) else None,
        "llm_invocation_streaming": _streaming,
        "time_to_first_token_ms": _ttft_ms,
        "time_to_first_token_note": (
            "non_streaming_latency_proxy" if _streaming is False and _ttft_ms is not None else None
        ),
        "tokens_per_second_output": _tps_out,
        "retrieval_status": retrieval.get("status"),
        "retrieval_route": retrieval.get("retrieval_route"),
        "retrieval_hit_count": retrieval.get("hit_count"),
        "retrieval_profile": retrieval.get("profile"),
        "retrieval_domain": retrieval.get("domain"),
        "retrieval_context_attached": bool(graph_state.get("context_text") or generation.get("retrieval_context_attached")),
        "retrieval_top_hit_score": retrieval.get("top_hit_score"),
        "retrieval_documents_used": retrieval.get("documents_used"),
        "retrieval_provenance": retrieval.get("provenance"),
        "retrieval_authority_level": retrieval.get("authority_level")
        or retrieval.get("governance_authority_level"),
        "retrieval_corpus_fingerprint": retrieval.get("corpus_fingerprint"),
        "retrieval_index_version": retrieval.get("index_version"),
        "retrieval_degradation_mode": retrieval.get("degradation_mode"),
        "retrieval_governance_summary": retrieval.get("retrieval_governance_summary"),
        "selected_capabilities": (
            _capability_projection.get("selected_capabilities")
            or _capability_selection_projection.get("selected_capabilities")
            or (
                (graph_state.get("realization_plan") or {}).get("capabilities_selected")
                if isinstance(graph_state.get("realization_plan"), dict)
                else None
            )
            or []
        ),
        "realization_plan": graph_state.get("realization_plan")
        if isinstance(graph_state.get("realization_plan"), dict)
        else None,
        "realize_via_capabilities_used_capability": graph_state.get(
            "realize_via_capabilities_used_capability"
        ),
        "realize_via_capabilities_outcome": graph_state.get("realize_via_capabilities_outcome"),
        "kanon_break": bool(graph_state.get("kanon_break")),
        "kanon_break_reason": graph_state.get("kanon_break_reason"),
        # PR-B: live effect propagation fields. The hold-effect dict is
        # ``None`` for action classes that must not hold (unknown / criminal
        # / high-risk / non-commit). The realization contract is always
        # emitted; ``visible_block_emitted`` and ``non_realization_reason``
        # carry the explicit status. See
        # ``docs/implementation_logs/pr_b_live_effect_propagation_piv.md``.
        "canonical_path_hold_effect": (
            graph_state.get("canonical_path_hold_effect")
            if isinstance(graph_state.get("canonical_path_hold_effect"), dict)
            else None
        ),
        "free_player_action_resolution": (
            graph_state.get("free_player_action_resolution")
            if isinstance(graph_state.get("free_player_action_resolution"), dict)
            else None
        ),
        "narrator_consequence_realization": (
            graph_state.get("narrator_consequence_realization")
            if isinstance(graph_state.get("narrator_consequence_realization"), dict)
            else None
        ),
        "director_gathering_state": (
            graph_state.get("director_gathering_state")
            if isinstance(graph_state.get("director_gathering_state"), dict)
            else None
        ),
        "gathering_paused_beat_suppression": graph_state.get(
            "gathering_paused_beat_suppression"
        ),
        "director_pause_transition_reaction": (
            graph_state.get("director_pause_transition_reaction")
            if isinstance(graph_state.get("director_pause_transition_reaction"), dict)
            else None
        ),
        "visible_block_emitted": bool(
            (
                graph_state.get("narrator_consequence_realization")
                if isinstance(graph_state.get("narrator_consequence_realization"), dict)
                else {}
            ).get("visible_block_emitted")
        ),
        "director_path_mode": graph_state.get("director_path_mode")
        or (
            "director_realization_composer"
            if isinstance(graph_state.get("realization_plan"), dict)
            else None
        ),
\
        "narrator_path_selected": narrator_path_selected,
        "director_narrator_path_plan": graph_state.get("director_narrator_path_plan")
        if isinstance(graph_state.get("director_narrator_path_plan"), dict)
        else None,
        "narrator_path": graph_state.get("narrator_path")
        if isinstance(graph_state.get("narrator_path"), dict)
        else None,
        "validator_dispatch_mode": (
            _validator_dispatch_report.get("dispatch_mode")
            or _validator_dispatch_report.get("mode")
            or graph_state.get("validator_dispatch_mode")
        ),
        "readiness_policy_input": _readiness_policy_input,
        "validation_status": validation.get("status"),
        "validation_reason": validation.get("reason"),
        "intent_surface_diagnostics": (
            validation.get("intent_surface_diagnostics")
            if isinstance(validation.get("intent_surface_diagnostics"), dict)
            else {}
        ),
        "npc_narrated_player_action_violation": bool(
            (
                validation.get("intent_surface_diagnostics")
                if isinstance(validation.get("intent_surface_diagnostics"), dict)
                else {}
            ).get("npc_narrated_player_action_violation")
        ),
        "actor_lane_validation_status": actor_lane_validation.get("status"),
        "actor_lane_validation_reason": actor_lane_validation.get("reason"),
        "commit_applied": bool(committed.get("commit_applied")),
        "player_input_kind": str(interpreted_input.get("player_input_kind") or "").strip().lower() or None,
        "player_input_kind_family": player_input_kind_family(_player_input_kind) if _player_input_kind else None,
        "intent_contract_version": INTENT_CONTRACT_VERSION,
        "player_action_committed": bool(interpreted_input.get("player_action_committed")),
        "player_speech_committed": bool(interpreted_input.get("player_speech_committed")),
        "narrator_response_expected": bool(interpreted_input.get("narrator_response_expected")),
        "npc_response_expected": bool(interpreted_input.get("npc_response_expected")),
        "player_action_frame_present": bool(
            graph_state.get("player_action_frame")
            if isinstance(graph_state.get("player_action_frame"), dict)
            else False
        ),
        "affordance_resolution_present": bool(
            graph_state.get("affordance_resolution")
            if isinstance(graph_state.get("affordance_resolution"), dict)
            else False
        ),
        "affordance_status": (
            str(
                (
                    graph_state.get("affordance_resolution")
                    if isinstance(graph_state.get("affordance_resolution"), dict)
                    else {}
                ).get("affordance_status")
                or ""
            ).strip()
            or None
        ),
        "action_commit_policy": (
            str(
                (
                    graph_state.get("affordance_resolution")
                    if isinstance(graph_state.get("affordance_resolution"), dict)
                    else {}
                ).get("action_commit_policy")
                or ""
            ).strip()
            or None
        ),
        "action_resolution_branch": routing.get("action_resolution_branch"),
        "action_resolution_short_path": bool(routing.get("action_resolution_short_path")),
        "action_resolution_short_path_reason": routing.get("action_resolution_short_path_reason"),
        "synthetic_short_path": bool(routing.get("action_resolution_short_path")),
        "authoritative_action_resolution_reason": (
            routing.get("action_resolution_short_path_reason")
            if routing.get("action_resolution_short_path")
            else None
        ),
        "generation_required": (
            bool(routing.get("generation_required"))
            if routing.get("generation_required") is not None
            else bool("invoke_model" in nodes or "fallback_model" in nodes)
        ),
        "semantic_move_kind": str(semantic_move_record.get("move_type") or "").strip() or None,
        "subtext_surface_mode": str(_subtext_record.get("surface_mode") or "").strip() or None,
        "subtext_hidden_intent_hypothesis": (
            str(_subtext_record.get("hidden_intent_hypothesis") or "").strip() or None
        ),
        "subtext_function": str(_subtext_record.get("subtext_function") or "").strip() or None,
        "subtext_sincerity_band": str(_subtext_record.get("sincerity_band") or "").strip() or None,
        "subtext_policy_source": str(_subtext_record.get("policy_source") or "").strip() or None,
        "subtext_policy_rule_id": str(_subtext_record.get("policy_rule_id") or "").strip() or None,
        "subtext_evidence_codes": list(_subtext_record.get("evidence_codes") or [])
        if isinstance(_subtext_record.get("evidence_codes"), list)
        else [],
        "scene_director_selection_source": (
            str(multi_pressure_resolution.get("selection_source") or "").strip()
            or str(scene_plan_record.get("selection_source") or "").strip()
            or None
        ),
        "planner_rationale_codes": list(scene_plan_record.get("planner_rationale_codes") or [])
        if isinstance(scene_plan_record.get("planner_rationale_codes"), list)
        else [],
        "scene_energy_target": (
            graph_state.get("scene_energy_target")
            if isinstance(graph_state.get("scene_energy_target"), dict)
            else scene_plan_record.get("scene_energy_target")
            if isinstance(scene_plan_record.get("scene_energy_target"), dict)
            else {}
        ),
        "scene_energy_transition": (
            graph_state.get("scene_energy_transition")
            if isinstance(graph_state.get("scene_energy_transition"), dict)
            else scene_plan_record.get("scene_energy_transition")
            if isinstance(scene_plan_record.get("scene_energy_transition"), dict)
            else {}
        ),
        "scene_energy_validation": (
            graph_state.get("scene_energy_validation")
            if isinstance(graph_state.get("scene_energy_validation"), dict)
            else {}
        ),
        "pacing_rhythm_state": (
            graph_state.get("pacing_rhythm_state")
            if isinstance(graph_state.get("pacing_rhythm_state"), dict)
            else scene_plan_record.get("pacing_rhythm_state")
            if isinstance(scene_plan_record.get("pacing_rhythm_state"), dict)
            else {}
        ),
        "pacing_rhythm_target": (
            graph_state.get("pacing_rhythm_target")
            if isinstance(graph_state.get("pacing_rhythm_target"), dict)
            else scene_plan_record.get("pacing_rhythm_target")
            if isinstance(scene_plan_record.get("pacing_rhythm_target"), dict)
            else {}
        ),
        "pacing_rhythm_validation": (
            graph_state.get("pacing_rhythm_validation")
            if isinstance(graph_state.get("pacing_rhythm_validation"), dict)
            else {}
        ),
        "temporal_control_state": (
            graph_state.get("temporal_control_state")
            if isinstance(graph_state.get("temporal_control_state"), dict)
            else scene_plan_record.get("temporal_control_state")
            if isinstance(scene_plan_record.get("temporal_control_state"), dict)
            else {}
        ),
        "temporal_control_target": (
            graph_state.get("temporal_control_target")
            if isinstance(graph_state.get("temporal_control_target"), dict)
            else scene_plan_record.get("temporal_control_target")
            if isinstance(scene_plan_record.get("temporal_control_target"), dict)
            else {}
        ),
        "temporal_control_validation": (
            graph_state.get("temporal_control_validation")
            if isinstance(graph_state.get("temporal_control_validation"), dict)
            else {}
        ),
        "sensory_context_state": (
            graph_state.get("sensory_context_state")
            if isinstance(graph_state.get("sensory_context_state"), dict)
            else scene_plan_record.get("sensory_context_state")
            if isinstance(scene_plan_record.get("sensory_context_state"), dict)
            else {}
        ),
        "sensory_context_target": (
            graph_state.get("sensory_context_target")
            if isinstance(graph_state.get("sensory_context_target"), dict)
            else scene_plan_record.get("sensory_context_target")
            if isinstance(scene_plan_record.get("sensory_context_target"), dict)
            else {}
        ),
        "sensory_context_validation": (
            graph_state.get("sensory_context_validation")
            if isinstance(graph_state.get("sensory_context_validation"), dict)
            else {}
        ),
        "genre_awareness_state": (
            graph_state.get("genre_awareness_state")
            if isinstance(graph_state.get("genre_awareness_state"), dict)
            else scene_plan_record.get("genre_awareness_state")
            if isinstance(scene_plan_record.get("genre_awareness_state"), dict)
            else {}
        ),
        "genre_awareness_target": (
            graph_state.get("genre_awareness_target")
            if isinstance(graph_state.get("genre_awareness_target"), dict)
            else scene_plan_record.get("genre_awareness_target")
            if isinstance(scene_plan_record.get("genre_awareness_target"), dict)
            else {}
        ),
        "genre_awareness_validation": (
            graph_state.get("genre_awareness_validation")
            if isinstance(graph_state.get("genre_awareness_validation"), dict)
            else {}
        ),
        "symbolic_object_resonance_state": (
            graph_state.get("symbolic_object_resonance_state")
            if isinstance(graph_state.get("symbolic_object_resonance_state"), dict)
            else scene_plan_record.get("symbolic_object_resonance_state")
            if isinstance(scene_plan_record.get("symbolic_object_resonance_state"), dict)
            else {}
        ),
        "symbolic_object_resonance_target": (
            graph_state.get("symbolic_object_resonance_target")
            if isinstance(graph_state.get("symbolic_object_resonance_target"), dict)
            else scene_plan_record.get("symbolic_object_resonance_target")
            if isinstance(scene_plan_record.get("symbolic_object_resonance_target"), dict)
            else {}
        ),
        "symbolic_object_resonance_validation": (
            graph_state.get("symbolic_object_resonance_validation")
            if isinstance(graph_state.get("symbolic_object_resonance_validation"), dict)
            else {}
        ),
        "social_pressure_state": (
            graph_state.get("social_pressure_state")
            if isinstance(graph_state.get("social_pressure_state"), dict)
            else scene_plan_record.get("social_pressure_state")
            if isinstance(scene_plan_record.get("social_pressure_state"), dict)
            else {}
        ),
        "social_pressure_target": (
            graph_state.get("social_pressure_target")
            if isinstance(graph_state.get("social_pressure_target"), dict)
            else scene_plan_record.get("social_pressure_target")
            if isinstance(scene_plan_record.get("social_pressure_target"), dict)
            else {}
        ),
        "social_pressure_validation": (
            graph_state.get("social_pressure_validation")
            if isinstance(graph_state.get("social_pressure_validation"), dict)
            else {}
        ),
        "expectation_variation_state": (
            graph_state.get("expectation_variation_state")
            if isinstance(graph_state.get("expectation_variation_state"), dict)
            else scene_plan_record.get("expectation_variation_state")
\
            if isinstance(scene_plan_record.get("expectation_variation_state"), dict)
            else {}
        ),
        "expectation_variation_target": (
            graph_state.get("expectation_variation_target")
            if isinstance(graph_state.get("expectation_variation_target"), dict)
            else scene_plan_record.get("expectation_variation_target")
            if isinstance(scene_plan_record.get("expectation_variation_target"), dict)
            else {}
        ),
        "expectation_variation_validation": (
            graph_state.get("expectation_variation_validation")
            if isinstance(graph_state.get("expectation_variation_validation"), dict)
            else {}
        ),
        "narrative_momentum_state": (
            graph_state.get("narrative_momentum_state")
            if isinstance(graph_state.get("narrative_momentum_state"), dict)
            else scene_plan_record.get("narrative_momentum_state")
            if isinstance(scene_plan_record.get("narrative_momentum_state"), dict)
            else {}
        ),
        "narrative_momentum_target": (
            graph_state.get("narrative_momentum_target")
            if isinstance(graph_state.get("narrative_momentum_target"), dict)
            else scene_plan_record.get("narrative_momentum_target")
            if isinstance(scene_plan_record.get("narrative_momentum_target"), dict)
            else {}
        ),
        "narrative_momentum_validation": (
            graph_state.get("narrative_momentum_validation")
            if isinstance(graph_state.get("narrative_momentum_validation"), dict)
            else {}
        ),
        "keyword_scene_candidates_used": bool(
            multi_pressure_resolution.get("keyword_scene_candidates_used")
        ),
        "intent_surface_contract_pass": 1 if _intent_surface_contract_pass else 0,
        "player_input_attribution_pass": 1 if _player_input_attribution_pass else 0,
        "semantic_move_alignment_pass": 1 if _semantic_move_alignment_pass else 0,
        "subtext_contract_pass": 1 if _subtext_contract_pass else 0,
        "npc_action_narration_boundary_pass": 1 if _npc_action_narration_boundary_pass else 0,
        "quality_class": governance.get("quality_class") or graph_state.get("quality_class"),
        "degradation_signals": list(governance.get("degradation_signals") or graph_state.get("degradation_signals") or []),
        "degradation_summary": governance.get("degradation_summary") or graph_state.get("degradation_summary"),
        "live_opening_failure_reason": gen_meta.get("live_opening_failure_reason") or generation.get("live_opening_failure_reason"),
        "graph_errors": graph_errors,
        "failure_markers": _str_list(graph_state.get("failure_markers")),
        "primary_responder_id": (
            graph_state.get("primary_responder_id")
            or graph_state.get("responder_id")
            or (event.get("actor_turn_summary") or {}).get("primary_responder_id")
        ),
        "response_present": bool(vitality.get("response_present"))
        or _final_visible_actor_response_in_event(event),
        "initiative_present": vitality.get("initiative_present"),
        "multi_actor_realized": vitality.get("multi_actor_realized"),
        "realized_actor_ids": list(vitality.get("realized_actor_ids") or []),
        "rendered_actor_ids": list(vitality.get("rendered_actor_ids") or []),
        "why_turn_felt_passive": (
            list(governance.get("why_turn_felt_passive"))
            if isinstance(governance.get("why_turn_felt_passive"), list)
            else list(passivity.get("why_turn_felt_passive") or [])
        ),
        "primary_passivity_factors": (
            list(governance.get("primary_passivity_factors"))
            if isinstance(governance.get("primary_passivity_factors"), list)
            else list(passivity.get("primary_passivity_factors") or [])
        ),
        "trace_origin": trace_origin,
        "execution_tier": execution_tier,
        "langfuse_environment": environment,
        "canonical_player_flow": canonical_player_flow,
        "test_case_id": test_case_id,
        "runtime_mode": runtime_mode,
    }
    if local_evidence_meta:
        summary.update(local_evidence_meta)
        summary["langfuse_environment"] = summary.get("environment")
    _quality = str(summary.get("quality_class") or "").strip().lower()
    if bool(summary.get("fallback_model_called")) or bool(summary.get("generation_fallback_used")):
        summary["runtime_quality"] = "fallback"
    elif _quality == "healthy":
        summary["runtime_quality"] = "healthy"
    elif _quality:
        summary["runtime_quality"] = "degraded"
    else:
        summary["runtime_quality"] = None
    opening_norm = graph_state.get("_opening_narration_normalization")
    if isinstance(opening_norm, dict):
        for key in (
            "opening_narration_normalized",
            "opening_narration_source",
            "opening_narration_beat_count",
            "narration_summary_input_kind",
        ):
            if key in opening_norm:
                summary[key] = opening_norm[key]
    ev_proj = graph_state.get("_actor_block_projection_evidence")
    if isinstance(ev_proj, dict):
        for key in (
            "actor_block_source",
            "actor_block_filtered_reason",
            "actor_line_count_before_projection",
            "action_line_count_before_projection",
            "actor_block_count_after_projection",
        ):
            if key in ev_proj:
                summary[key] = ev_proj[key]
    vis_contract = graph_state.get("_visible_narrative_contract")
    if isinstance(vis_contract, dict):
        for key in (
            "visible_language_detected",
            "mixed_language_detected",
            "visible_language_contract_pass",
            "selected_role_visible_in_opening",
            "player_identity_anchor_present",
            "visible_narrative_contract_version",
            "name_only_actor_block_removed",
            "label_only_line_removed",
            "duplicate_actor_label_removed",
            "placeholder_action_removed",
            "actor_line_action_tail_stripped",
            "near_duplicate_visible_block_removed",
        ):
            if key in vis_contract:
                summary[key] = vis_contract[key]
    transition_diag = graph_state.get("_opening_transition_diagnostics")
    if isinstance(transition_diag, dict):
        for key, val in transition_diag.items():
            summary[key] = val
    if session.module_id == GOD_OF_CARNAGE_MODULE_ID:
        actor_lane_context = StoryRuntimeManager._extract_actor_lane_context(session)
        knowledge_summary = build_knowledge_path_summary(
            graph_state=graph_state,
            event=event,
            actor_lane_context=actor_lane_context,
        )
        summary.update(knowledge_summary)
    _plc_gs = graph_state.get("player_local_context")
    summary["player_local_context"] = _plc_gs if isinstance(_plc_gs, dict) else None
    _lct_gs = graph_state.get("local_context_transition")
    summary["local_context_transition"] = _lct_gs if isinstance(_lct_gs, dict) else None
    _ncp_gs = graph_state.get("narrator_consequence_plan")
    summary["narrator_consequence_plan"] = _ncp_gs if isinstance(_ncp_gs, dict) else None
    _env_gs = graph_state.get("environment_state")
    summary["environment_state"] = _env_gs if isinstance(_env_gs, dict) else None
    _env_tr = graph_state.get("environment_transition")
    summary["environment_transition"] = _env_tr if isinstance(_env_tr, dict) else None
    summary["movement_return_intent"] = bool(interpreted_input.get("movement_return_intent"))
    if "speech_projection_allowed" in interpreted_input:
        summary["speech_projection_allowed"] = bool(interpreted_input.get("speech_projection_allowed"))
    _aff_gs = graph_state.get("affordance_resolution") if isinstance(graph_state.get("affordance_resolution"), dict) else {}
    summary["resolved_target_id"] = _aff_gs.get("resolved_target_id")
    summary["target_resolution_source"] = _aff_gs.get("target_resolution_source")
    summary["authoritative_action_surface"] = bool(
        gen_meta.get("authoritative_action_resolution") is True
        or str(gen_meta.get("adapter") or "").strip().lower() == "action_resolution_authoritative"
    )
    if (
        bool(interpreted_input.get("movement_return_intent"))
        and str(summary.get("affordance_status") or "").strip().lower() == "ambiguous"
        and str(summary.get("action_commit_policy") or "").strip().lower() == "needs_clarification"
    ):
        summary["turn_status"] = "needs_clarification"

    summary["p0_action_resolution_evidence"] = _build_p0_action_resolution_evidence(
        event=event,
        graph_state=graph_state,
        interpreted_input=interpreted_input,
        validation=validation,
        committed_result=committed,
    )
    summary["generation_mode"] = _infer_generation_mode(summary)
    tn = event.get("turn_number")
    summary["canonical_turn_id"] = _canonical_turn_id(session.session_id, int(tn or 0))
    return summary

__all__ = ['_build_langfuse_path_summary']
