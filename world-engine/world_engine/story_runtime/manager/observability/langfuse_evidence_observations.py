"""Unsharded manager helper `_emit_langfuse_evidence_observations` (Wave 1)."""
from __future__ import annotations

from .._deps import *

def _emit_langfuse_evidence_observations(
    *,
    path_summary: dict[str, Any],
    graph_state: dict[str, Any],
    event: dict[str, Any],
) -> None:
    try:
        adapter = LangfuseAdapter.get_instance()
    except Exception:
        logger.debug("Langfuse adapter unavailable for evidence observations", exc_info=True)
        return
    try:
        if not adapter or not adapter.is_enabled():
            return
    except Exception:
        return

    # Wave 0-C: prefer per-call ledger rows over path_summary reconstruction.
    ledger_calls = []
    phase_costs = graph_state.get("phase_costs") if isinstance(graph_state, dict) else None
    if isinstance(phase_costs, dict):
        summary = phase_costs.get("_ledger_summary")
        for phase_name, record in phase_costs.items():
            if phase_name == "_ledger_summary" or not isinstance(record, dict):
                continue
            nested = record.get("calls")
            if isinstance(nested, list) and nested:
                for row in nested:
                    if isinstance(row, dict):
                        ledger_calls.append(row)
            elif record.get("phase") or phase_name:
                ledger_calls.append(record)
        if isinstance(summary, dict) and not ledger_calls:
            # summary alone is not enough to emit generations
            pass
    _PHASE_OBS_NAME = {
        "model_generation": "story.model.generation",
        "input_translation": "story.model.translation.input",
        "output_translation": "story.model.translation.output",
        "self_correction": "story.model.self_correction",
        "fallback": "story.model.fallback",
        "unattributed": "story.model.generation",
    }
    if ledger_calls:
        for row in ledger_calls:
            phase = str(row.get("phase") or "unattributed")
            obs_name = _PHASE_OBS_NAME.get(phase, "story.model.generation")
            try:
                usage = None
                tin = int(row.get("input_tokens") or 0)
                tout = int(row.get("output_tokens") or 0)
                if tin or tout:
                    usage = {"input": tin, "output": tout, "total": tin + tout}
                adapter.record_generation(
                    name=obs_name,
                    model=str(row.get("model") or path_summary.get("selected_model") or "unknown"),
                    provider=str(row.get("provider") or path_summary.get("selected_provider") or "unknown"),
                    prompt="",
                    completion="",
                    usage_details=usage,
                    latency_ms=float(row["latency_ms"]) if row.get("latency_ms") is not None else None,
                    metadata={
                        "session_id": path_summary.get("session_id"),
                        "module_id": path_summary.get("module_id"),
                        "turn_number": path_summary.get("turn_number"),
                        "attempt_index": row.get("attempt_index"),
                        "trigger": row.get("trigger"),
                        "phase": phase,
                        "generation_observation_source": "turn_call_ledger",
                        "budget_warning": row.get("budget_warning"),
                    },
                )
            except Exception:
                logger.debug("Langfuse ledger generation observation failed", exc_info=True)
        # Skip the legacy path_summary dual-generation path when ledger rows exist.
        generation = (
            (event.get("model_route") or {}).get("generation")
            if isinstance(event.get("model_route"), dict)
            else {}
        )
        if not isinstance(generation, dict):
            generation = {}
        # Fall through to retrieval / score emission below without re-recording generation.
        record_final_generation = False
        record_primary_attempt_generation = False
        adapter_name = ""
        primary_adapter_name = ""
        usage_for_lf = None
        model_name = "unknown"
        provider = "unknown"
        _lat_ev_f = None
        _tps_ev_f = None
        _ttft_ev_f = None
        _provided = ""
        _prompt_name_ev = None
        _ud_in = _ud_out = _ud_tot = 0
    else:
        generation = (
            (event.get("model_route") or {}).get("generation")
            if isinstance(event.get("model_route"), dict)
            else {}
        )
        if not isinstance(generation, dict):
            generation = {}
        gen_meta = generation.get("metadata") if isinstance(generation.get("metadata"), dict) else {}
        adapter_name = str(gen_meta.get("adapter") or "").strip()
        primary_adapter_name = str(path_summary.get("primary_attempt_adapter") or "").strip()
        deterministic_adapters = {"mock", "ldss_fallback", "ldss_deterministic", NARRATOR_PATH_ADAPTER}
        primary_attempt_api_success = path_summary.get("primary_attempt_api_success") is True
        record_primary_attempt_generation = (
            primary_attempt_api_success
            and bool(primary_adapter_name)
            and primary_adapter_name not in deterministic_adapters
        )
        record_final_generation = bool(adapter_name) and adapter_name not in deterministic_adapters
        usage_details = path_summary.get("usage_details") if isinstance(path_summary.get("usage_details"), dict) else {}
        _ud_in = int(usage_details.get("input") or 0)
        _ud_out = int(usage_details.get("output") or 0)
        _ud_tot = int(usage_details.get("total") or 0)
        if _ud_tot <= 0 and (_ud_in > 0 or _ud_out > 0):
            _ud_tot = _ud_in + _ud_out
        usage_for_lf = (
            {"input": _ud_in, "output": _ud_out, "total": _ud_tot} if (_ud_in or _ud_out or _ud_tot) else None
        )
        model_name = str(
            (
                path_summary.get("primary_attempt_model")
                if record_primary_attempt_generation and not record_final_generation
                else None
            )
            or path_summary.get("api_model")
            or path_summary.get("selected_model")
            or gen_meta.get("model")
            or "unknown"
        ).strip()
        provider = str(
            (
                path_summary.get("primary_attempt_provider")
                if record_primary_attempt_generation and not record_final_generation
                else None
            )
            or path_summary.get("selected_provider")
            or primary_adapter_name
            or adapter_name
            or "unknown"
        ).strip()
        _lat_ev = path_summary.get("generation_latency_ms")
        _lat_ev_f = float(_lat_ev) if isinstance(_lat_ev, (int, float)) else None
        _tps_ev = path_summary.get("tokens_per_second_output")
        _tps_ev_f = float(_tps_ev) if isinstance(_tps_ev, (int, float)) else None
        _ttft_ev = path_summary.get("time_to_first_token_ms")
        _ttft_ev_f = float(_ttft_ev) if isinstance(_ttft_ev, (int, float)) else None
        _provided = str(
            path_summary.get("provided_model_name")
            or (
                path_summary.get("primary_attempt_model")
                if record_primary_attempt_generation and not record_final_generation
                else None
            )
            or gen_meta.get("model")
            or model_name
        ).strip()
        _prompt_name_ev = path_summary.get("langfuse_prompt_name")
    if record_final_generation or record_primary_attempt_generation:
        completion_text = (
            generation.get("model_raw_text")
            or generation.get("content")
            or path_summary.get("primary_attempt_raw_output_excerpt")
            or ""
        )
        try:
            adapter.record_generation(
                name="story.model.generation",
                model=model_name,
                provider=provider,
                prompt=str(graph_state.get("model_prompt") or "")[:20000],
                completion=str(completion_text)[:20000],
                usage_details=usage_for_lf,
                provided_model_name=_provided or None,
                prompt_name=str(_prompt_name_ev).strip() if _prompt_name_ev else None,
                latency_ms=_lat_ev_f,
                time_to_first_token_ms=_ttft_ev_f,
                tokens_per_second=_tps_ev_f,
                metadata={
                    "session_id": path_summary.get("session_id"),
                    "module_id": path_summary.get("module_id"),
                    "turn_number": path_summary.get("turn_number"),
                    "canonical_turn_id": path_summary.get("canonical_turn_id"),
                    "opening_turn": int(path_summary.get("turn_number") or 0) == 0,
                    "turn_kind": path_summary.get("turn_kind"),
                    "adapter": adapter_name,
                    "generation_observation_source": (
                        "primary_attempt" if record_primary_attempt_generation and not record_final_generation else "final"
                    ),
                    "primary_attempt_adapter": path_summary.get("primary_attempt_adapter"),
                    "primary_attempt_model": path_summary.get("primary_attempt_model"),
                    "primary_attempt_provider": path_summary.get("primary_attempt_provider"),
                    "primary_attempt_invocation_mode": path_summary.get("primary_attempt_invocation_mode"),
                    "primary_attempt_api_success": path_summary.get("primary_attempt_api_success"),
                    "primary_attempt_structured_output_present": path_summary.get(
                        "primary_attempt_structured_output_present"
                    ),
                    "primary_attempt_raw_output_sha256": path_summary.get("primary_attempt_raw_output_sha256"),
                    "adapter_invocation_mode": path_summary.get("adapter_invocation_mode"),
                    "final_adapter": path_summary.get("final_adapter"),
                    "final_adapter_invocation_mode": path_summary.get("final_adapter_invocation_mode"),
                    "route_id": path_summary.get("route_id"),
                    "route_family": path_summary.get("route_family"),
                    "selected_model": path_summary.get("selected_model"),
                    "fallback_model": path_summary.get("fallback_model"),
                    "fallback_used": path_summary.get("generation_fallback_used"),
                    "structured_output_present": path_summary.get("structured_output_present"),
                    "parser_error": path_summary.get("parser_error"),
                    "retrieval_context_attached": path_summary.get("retrieval_context_attached"),
                    "usage_available": path_summary.get("usage_available"),
                    "usage_source": path_summary.get("usage_source"),
                    "trace_origin": path_summary.get("trace_origin"),
                    "execution_tier": path_summary.get("execution_tier"),
                    "canonical_player_flow": path_summary.get("canonical_player_flow"),
                    "test_case_id": path_summary.get("test_case_id"),
                    "runtime_mode": path_summary.get("runtime_mode"),
                    "generation_mode": path_summary.get("generation_mode"),
                    "input_tokens": _ud_in,
                    "output_tokens": _ud_out,
                    "total_tokens": _ud_tot,
                    "time_to_first_token_note": path_summary.get("time_to_first_token_note"),
                },
            )
        except Exception:
            logger.debug("Langfuse generation observation failed", exc_info=True)

    retrieval = event.get("retrieval") if isinstance(event.get("retrieval"), dict) else {}
    sources = retrieval.get("sources") if isinstance(retrieval.get("sources"), list) else []
    documents: list[dict[str, Any]] = []
    for source in sources[:8]:
        if not isinstance(source, dict):
            continue
        documents.append(
            {
                "id": source.get("chunk_id") or source.get("source_path"),
                "content": source.get("snippet"),
                "score": source.get("score"),
                "metadata": {
                    "source_path": source.get("source_path"),
                    "content_class": source.get("content_class"),
                    "pack_role": source.get("pack_role"),
                    "source_evidence_lane": source.get("source_evidence_lane"),
                    "policy_note": source.get("policy_note"),
                },
            }
        )
    if retrieval:
        try:
            adapter.record_retrieval(
                name="story.rag.retrieval",
                query=str(retrieval.get("query") or event.get("raw_input") or "")[:4000],
                documents=documents,
                metadata={
                    "session_id": path_summary.get("session_id"),
                    "module_id": path_summary.get("module_id"),
                    "turn_number": path_summary.get("turn_number"),
                    "canonical_turn_id": path_summary.get("canonical_turn_id"),
                    "status": path_summary.get("retrieval_status"),
                    "retrieval_route": path_summary.get("retrieval_route"),
                    "hit_count": path_summary.get("retrieval_hit_count"),
                    "profile": path_summary.get("retrieval_profile"),
                    "domain": path_summary.get("retrieval_domain"),
                    "context_attached": path_summary.get("retrieval_context_attached"),
                    "top_hit_score": path_summary.get("retrieval_top_hit_score"),
                    "corpus_fingerprint": path_summary.get("retrieval_corpus_fingerprint"),
                    "index_version": path_summary.get("retrieval_index_version"),
                    "degradation_mode": path_summary.get("retrieval_degradation_mode"),
                    "governance_summary": path_summary.get("retrieval_governance_summary"),
                    "trace_origin": path_summary.get("trace_origin"),
                    "execution_tier": path_summary.get("execution_tier"),
                    "canonical_player_flow": path_summary.get("canonical_player_flow"),
                    "test_case_id": path_summary.get("test_case_id"),
                    "runtime_mode": path_summary.get("runtime_mode"),
                    "generation_mode": path_summary.get("generation_mode"),
                },
            )
        except Exception:
            logger.debug("Langfuse retrieval observation failed", exc_info=True)

    # Align with player-visible truth: opening turns often have gm_narration / generation text
    # before scene_blocks projection; counting only scene_blocks yields false 0 (see Langfuse traces).
    has_visible_surface = bool(_scene_blocks_from_turn_event(event)) or bool(
        _visible_lines_from_turn_event(event)
    )
    _authoritative_action_surface = adapter_name in {
        "action_resolution_authoritative",
        "action_resolution_synthetic",
    }
    deterministic_scores = {
        "non_mock_generation_pass": (
            1.0
            if _authoritative_action_surface
            or adapter_name not in {"", "mock", "ldss_fallback", "ldss_deterministic"}
            else 0.0
        ),
        "visible_output_present": 1.0 if has_visible_surface else 0.0,
        "actor_lane_safety_pass": 1.0 if path_summary.get("actor_lane_validation_status") in {"approved", None} else 0.0,
        "fallback_absent": 0.0 if path_summary.get("generation_fallback_used") else 1.0,
        "usage_present": 1.0 if int(usage_details.get("total") or 0) > 0 or _authoritative_action_surface else 0.0,
        "rag_context_attached": 1.0 if path_summary.get("retrieval_context_attached") else 0.0,
    }
    narrator_path_selected = bool(path_summary.get("narrator_path_selected")) or (
        str(path_summary.get("director_path_mode") or "").strip() == "narrator_path"
    )
    if narrator_path_selected:
        deterministic_scores["usage_present"] = 1.0
        deterministic_scores["rag_context_attached"] = 1.0
    intent_kind = str(path_summary.get("player_input_kind") or "").strip().lower()
    semantic_move_kind = str(path_summary.get("semantic_move_kind") or "").strip()
    semantic_alignment_pass = True
    if semantic_move_kind:
        semantic_alignment_pass = True
    if is_question_punctuation_probe_guarded(intent_kind) and semantic_move_kind:
        semantic_alignment_pass = (
            semantic_alignment_pass
\
            and semantic_move_kind not in FORBIDDEN_NON_SPEECH_ACTION_SEMANTIC_MOVES
        )
    npc_action_narration_boundary_pass = not bool(
        path_summary.get("npc_narrated_player_action_violation")
    )
    player_input_attribution = path_summary.get("player_input_attribution_pass")
    player_input_attribution_pass = (
        True if player_input_attribution is None else bool(player_input_attribution)
    )
    intent_surface_contract_pass = True
    if intent_kind:
        intent_surface_contract_pass = (
            intent_kind in PLAYER_INPUT_KINDS
            and isinstance(path_summary.get("player_action_committed"), bool)
            and isinstance(path_summary.get("player_speech_committed"), bool)
            and isinstance(path_summary.get("narrator_response_expected"), bool)
            and isinstance(path_summary.get("npc_response_expected"), bool)
        )
    deterministic_scores["intent_surface_contract_pass"] = 1.0 if intent_surface_contract_pass else 0.0
    deterministic_scores["player_input_attribution_pass"] = 1.0 if player_input_attribution_pass else 0.0
    deterministic_scores["semantic_move_alignment_pass"] = 1.0 if semantic_alignment_pass else 0.0
    subtext_contract_raw = path_summary.get("subtext_contract_pass")
    if subtext_contract_raw is None:
        subtext_fields_present = any(
            path_summary.get(key)
            for key in (
                "subtext_surface_mode",
                "subtext_hidden_intent_hypothesis",
                "subtext_function",
                "subtext_sincerity_band",
            )
        )
        subtext_contract_pass = True
        if subtext_fields_present:
            subtext_contract_pass = all(
                bool(str(path_summary.get(key) or "").strip())
                for key in (
                    "subtext_surface_mode",
                    "subtext_hidden_intent_hypothesis",
                    "subtext_function",
                    "subtext_sincerity_band",
                )
            )
    else:
        subtext_contract_pass = bool(subtext_contract_raw)
    deterministic_scores["subtext_contract_pass"] = 1.0 if subtext_contract_pass else 0.0
    deterministic_scores["npc_action_narration_boundary_pass"] = (
        1.0 if npc_action_narration_boundary_pass else 0.0
    )
    # OPEN-SCORE-SPLIT-01:
    # - opening_shape_contract_pass: purely visible opening-shape quality (can pass in fixtures/mocks).
    # - live_opening_contract_pass: strict live-only success marker for canonical live_ui opening.
    # ``opening_contract_pass`` is kept as a compatibility alias to opening_shape_contract_pass.
    # Turn > 0 trivially passes the shape check (opening-only structural contract).
    _turn_number = int(path_summary.get("turn_number") or 0)
    _opening_blocks: list[dict[str, Any]] = []
    _opening_shape_subgates: dict[str, bool] = {}
    _opening_shape_failure_reasons: list[str] = []
    _scene_block_summary: list[dict[str, Any]] = []
    first_actor_block_index_val: int | None = None
    narrator_block_count_val = 0
    structured_narration_summary_kind: str | None = None
    if _turn_number == 0:
        _opening_blocks = _scene_blocks_from_turn_event(event)
        opening_shape_pass = (
            1.0 if _opening_block_contract_satisfied(_opening_blocks) else 0.0
        )
        # OPEN-SHAPE-EVIDENCE-01: Decompose the contract into auditable subgates and
        # capture a small scene-block excerpt so dashboards can answer "why did
        # opening_shape_contract_pass fail?" without re-fetching the trace body.
        _opening_shape_subgates, _opening_shape_failure_reasons = (
            _compute_opening_shape_subgates(_opening_blocks)
        )
        if narrator_path_selected:
            narrator_only_shape_pass = (
                len(_opening_blocks) >= 4
                and all(
                    str(block.get("block_type") or block.get("type") or "").strip().lower()
                    == "narrator"
                    for block in _opening_blocks
                    if isinstance(block, dict)
                )
            )
            _opening_shape_subgates["narrator_path_narrator_only_valid"] = narrator_only_shape_pass
            if narrator_only_shape_pass:
                opening_shape_pass = 1.0
                _opening_shape_failure_reasons = [
                    reason
                    for reason in _opening_shape_failure_reasons
                    if reason not in {"no_actor_block_present", "first_actor_missing"}
                ]
        _scene_block_summary = _compact_scene_block_summary(_opening_blocks)

        def _bt_ev(b: dict) -> str:
            return str(b.get("block_type") or b.get("type") or "").strip().lower()

        narrator_block_count_val = sum(1 for b in _opening_blocks if _bt_ev(b) == "narrator")
        for i, b in enumerate(_opening_blocks):
            if _bt_ev(b) in {"actor_line", "actor_action"}:
                first_actor_block_index_val = i
                break
        gen_ev = ((event.get("model_route") or {}).get("generation") or {}) if isinstance(event.get("model_route"), dict) else {}
        meta_ev = gen_ev.get("metadata") if isinstance(gen_ev.get("metadata"), dict) else {}
        struct_ev = meta_ev.get("structured_output") if isinstance(meta_ev.get("structured_output"), dict) else None
        if struct_ev is None and isinstance(gen_ev.get("structured_output"), dict):
            struct_ev = gen_ev["structured_output"]
        if isinstance(struct_ev, dict):
            ns_ev = struct_ev.get("narration_summary")
            if isinstance(ns_ev, str) and ns_ev.strip():
                structured_narration_summary_kind = "str"
            elif isinstance(ns_ev, list):
                structured_narration_summary_kind = "list"
            else:
                structured_narration_summary_kind = "absent"
        else:
            structured_narration_summary_kind = "missing_structured"
        if (
            opening_shape_pass < 1.0
            and structured_narration_summary_kind == "str"
            and "narration_summary_single_string" not in _opening_shape_failure_reasons
        ):
            _opening_shape_failure_reasons = list(_opening_shape_failure_reasons) + [
                "narration_summary_single_string"
            ]
    else:
        opening_shape_pass = 1.0
    deterministic_scores["opening_shape_contract_pass"] = opening_shape_pass
    deterministic_scores["opening_contract_pass"] = opening_shape_pass
    # STAGING-OPENING-LOCALE-LDSS-AND-ACTION-CONTEXT-REPAIR-01 P6: promote role_anchor_present
    # to its own top-level numeric score so dashboards can filter without nested metadata joins.
    if _turn_number == 0:
        deterministic_scores["opening_role_anchor_pass"] = (
            1.0 if _opening_shape_subgates.get("role_anchor_present") else 0.0
        )
    else:
        deterministic_scores["opening_role_anchor_pass"] = 1.0
    deterministic_scores["hard_forbidden_absent"] = (
        1.0 if path_summary.get("hard_forbidden_absent", True) else 0.0
    )
    deterministic_scores["opening_summary_only_absent"] = (
        1.0 if path_summary.get("opening_summary_only_absent", True) else 0.0
    )
    deterministic_scores["opening_event_coverage_pass"] = (
        1.0 if (_turn_number > 0 or path_summary.get("opening_event_coverage_pass", True)) else 0.0
    )
    # GOC-KNOWLEDGE-RUNTIME-INTEGRATION P0.3/P0.4: per-category absent-scores derived
    # from hard_forbidden_detection.detected detection_keys. Deterministic 1.0 / 0.0.
    _hfd_for_scores = path_summary.get("hard_forbidden_detection") if isinstance(path_summary.get("hard_forbidden_detection"), dict) else {}
    _detected_keys: set[str] = set()
    for _hit in (_hfd_for_scores.get("detected") or []):
        if isinstance(_hit, dict):
            _key = str(_hit.get("detection_key") or "").strip()
            if _key:
                _detected_keys.add(_key)
    _absent_score_map = {
        "opening_player_speech_absent": "forced_player_speech",
        "opening_npc_exposition_absent": "npc_world_explanation",
        "npc_exposition_absent": "npc_world_explanation",
        "player_agency_violation_absent": "player_agency_violation",
        "meta_runtime_language_absent": "meta_runtime_language",
        "stage_direction_labels_absent": "stage_direction_labels",
        "source_reproduction_absent": "source_text_reproduction",
    }
    for _score_name, _detection_key in _absent_score_map.items():
        deterministic_scores[_score_name] = 0.0 if _detection_key in _detected_keys else 1.0
    if _turn_number == 0:
        if narrator_path_selected:
            _transition_diag_for_scores = {
                "narrator_path_transition_contract_pass": True,
                "narrator_path_transition_mode": "speech_free_scene_setup",
            }
        else:
            _transition_diag_for_scores = compute_opening_transition_from_scene_blocks(
                _opening_blocks,
                human_actor_id=str(path_summary.get("human_actor_id") or "").strip() or None,
                selected_player_role=str(path_summary.get("selected_player_role") or "").strip() or None,
            )
            deterministic_scores["opening_transition_contract_pass"] = (
                1.0 if _transition_diag_for_scores.get("opening_transition_contract_pass") else 0.0
            )
    else:
        _transition_diag_for_scores = {}
        if not narrator_path_selected:
            deterministic_scores["opening_transition_contract_pass"] = 1.0
    _p0_player_turn_langfuse_scores = frozenset(
        {
            "player_action_frame_present",
            "affordance_resolution_present",
            "affordance_status_valid",
            "action_commit_policy_present",
        }
    )
    live_contract_pass = all(
        value == 1.0
        for key, value in deterministic_scores.items()
        if _turn_number > 0 or key not in _p0_player_turn_langfuse_scores
    ) and path_summary.get("quality_class") not in {"degraded", "failed"}
    deterministic_scores["live_runtime_contract_pass"] = 1.0 if live_contract_pass else 0.0
    # Player-visible path only (excludes mock/usage/RAG gates). Stays green in mock_only when UI output is present.
    qc = path_summary.get("quality_class")
    surface_ok = (
        deterministic_scores["visible_output_present"] == 1.0
        and deterministic_scores["actor_lane_safety_pass"] == 1.0
        and deterministic_scores["fallback_absent"] == 1.0
        and qc not in {"degraded", "failed"}
    )
    deterministic_scores["live_runtime_visible_surface_pass"] = 1.0 if surface_ok else 0.0
    _valid_aff = frozenset(
        {"allowed", "allowed_offscreen", "partial", "ambiguous", "blocked", "unknown_target", "unsafe"}
    )
    _aff_st_ev = str(path_summary.get("affordance_status") or "").strip().lower()
    _aff_pres_ev = bool(path_summary.get("affordance_resolution_present"))
    # P0 player-action Langfuse scores apply only to real player turns (``turn_number > 0``).
    # Opening traces must not contribute ``player_action_frame_present`` / affordance scores
    # that could be mistaken for P0 correctness evidence.
    if _turn_number > 0:
        deterministic_scores["player_action_frame_present"] = (
            1.0 if bool(path_summary.get("player_action_frame_present")) else 0.0
        )
        deterministic_scores["affordance_resolution_present"] = 1.0 if _aff_pres_ev else 0.0
        deterministic_scores["affordance_status_valid"] = (
            1.0 if (not _aff_pres_ev or _aff_st_ev in _valid_aff) else 0.0
        )
        deterministic_scores["action_commit_policy_present"] = (
            1.0 if str(path_summary.get("action_commit_policy") or "").strip() else 0.0
        )
        # PLAYER-LOCAL-CONTEXT-AND-NARRATOR-CONSEQUENCE-01 scores (action-resolution short-path only).
        _lct = path_summary.get("local_context_transition") if isinstance(path_summary.get("local_context_transition"), dict) else None
        _ncp = path_summary.get("narrator_consequence_plan") if isinstance(path_summary.get("narrator_consequence_plan"), dict) else None
        _intent_kind_for_consequence = str(path_summary.get("player_input_kind") or "").strip().lower()
        _is_action_resolution_turn = _authoritative_action_surface and _intent_kind_for_consequence in {
            "action",
            "perception",
            "object_interaction",
            "physical_action",
            "movement_action",
            "perception_action",
        }
        # STAGING-OPENING-LOCALE-LDSS-AND-ACTION-CONTEXT-REPAIR-01 P4: emit deterministic
        # action-context scores on every player turn — not only the authoritative action
\
        # short-path — so dashboards observe degraded/fallback behaviour rather than gaps.
        _action_diag = _compute_action_consequence_diagnostics(path_summary)
        for _name in (
            "local_context_transition_present",
            "narrator_consequence_present",
            "new_location_established",
            "perception_result_present",
            "action_consequence_contract_pass",
            "npc_consequence_takeover_absent",
        ):
            _value = _action_diag.get(_name)
            if isinstance(_value, (int, float)):
                deterministic_scores[_name] = float(_value)
    # live_opening_contract_pass is only meaningful on the opening turn (turn 0).
    # Writing it on subsequent turns would produce false negatives that pollute
    # the trace score history and make passing openings appear to have failed.
    _live_subgates: dict[str, bool] = {}
    _live_failure_reasons: list[str] = []
    if _turn_number == 0:
        final_adapter = str(path_summary.get("final_adapter") or path_summary.get("adapter") or "").strip().lower()
        trace_origin = str(path_summary.get("trace_origin") or "").strip().lower()
        execution_tier = str(path_summary.get("execution_tier") or "").strip().lower()
        canonical_player_flow = bool(path_summary.get("canonical_player_flow"))
        _live_subgates = {
            "turn_0": True,
            "trace_origin_live_ui": trace_origin == "live_ui",
            "execution_tier_live": execution_tier == "live",
            "canonical_player_flow": canonical_player_flow,
            "opening_shape_pass": deterministic_scores["opening_shape_contract_pass"] == 1.0,
            (
                "narrator_path_transition_pass"
                if narrator_path_selected
                else "opening_transition_pass"
            ): (
                bool(_transition_diag_for_scores.get("narrator_path_transition_contract_pass"))
                if narrator_path_selected
                else deterministic_scores.get("opening_transition_contract_pass", 1.0) == 1.0
            ),
            "live_runtime_pass": deterministic_scores["live_runtime_contract_pass"] == 1.0,
            "not_ldss_fallback": final_adapter not in {"ldss_fallback"},
            "fallback_absent": deterministic_scores["fallback_absent"] == 1.0,
            "non_mock_generation": deterministic_scores["non_mock_generation_pass"] == 1.0,
            "quality_class_ok": qc not in {"degraded", "failed"},
        }
        _live_failure_reasons = [k for k, v in _live_subgates.items() if not v]
        live_opening_ok = all(_live_subgates.values())
        deterministic_scores["live_opening_contract_pass"] = 1.0 if live_opening_ok else 0.0
    canonical_signals = _build_canonical_degradation_signals(path_summary)
    degradation_chain = _build_degradation_chain(path_summary)
    degradation_prose_summary = _build_degradation_prose_summary(path_summary)
    live_opening_failure_reason = path_summary.get("live_opening_failure_reason")
    score_metadata_base = {
        "session_id": path_summary.get("session_id"),
        "turn_number": path_summary.get("turn_number"),
        "canonical_turn_id": path_summary.get("canonical_turn_id"),
        "selected_player_role": path_summary.get("selected_player_role"),
        "human_actor_id": path_summary.get("human_actor_id"),
        "quality_class": path_summary.get("quality_class"),
        "degradation_signals": canonical_signals,
        "degradation_chain": degradation_chain,
        "degradation_summary": degradation_prose_summary,
        "player_input_kind": path_summary.get("player_input_kind"),
        "player_input_kind_family": path_summary.get("player_input_kind_family")
        or player_input_kind_family(path_summary.get("player_input_kind")),
        "intent_contract_version": path_summary.get("intent_contract_version")
        or INTENT_CONTRACT_VERSION,
        "player_action_committed": path_summary.get("player_action_committed"),
        "player_speech_committed": path_summary.get("player_speech_committed"),
        "narrator_response_expected": path_summary.get("narrator_response_expected"),
        "npc_response_expected": path_summary.get("npc_response_expected"),
        "p0_action_resolution_evidence": path_summary.get("p0_action_resolution_evidence"),
        "semantic_move_kind": path_summary.get("semantic_move_kind"),
        "subtext_surface_mode": path_summary.get("subtext_surface_mode"),
        "subtext_hidden_intent_hypothesis": path_summary.get(
            "subtext_hidden_intent_hypothesis"
        ),
        "subtext_function": path_summary.get("subtext_function"),
        "subtext_sincerity_band": path_summary.get("subtext_sincerity_band"),
        "subtext_policy_source": path_summary.get("subtext_policy_source"),
        "subtext_policy_rule_id": path_summary.get("subtext_policy_rule_id"),
        "subtext_evidence_codes": path_summary.get("subtext_evidence_codes"),
        "scene_director_selection_source": path_summary.get("scene_director_selection_source"),
        "planner_rationale_codes": path_summary.get("planner_rationale_codes"),
        "keyword_scene_candidates_used": path_summary.get(
            "keyword_scene_candidates_used"
        ),
        "npc_narrated_player_action_violation": path_summary.get(
            "npc_narrated_player_action_violation"
        ),
        "intent_surface_contract_pass": deterministic_scores.get("intent_surface_contract_pass"),
        "player_input_attribution_pass": deterministic_scores.get("player_input_attribution_pass"),
        "semantic_move_alignment_pass": deterministic_scores.get("semantic_move_alignment_pass"),
        "subtext_contract_pass": deterministic_scores.get("subtext_contract_pass"),
        "npc_action_narration_boundary_pass": deterministic_scores.get(
            "npc_action_narration_boundary_pass"
        ),
        "live_opening_failure_reason": live_opening_failure_reason,
        "live_opening_subgates": _live_subgates,
        "live_opening_failure_reasons": _live_failure_reasons,
        # OPEN-SHAPE-EVIDENCE-01: opening_shape_contract_pass subgate decomposition
        # + truncated scene_block excerpts. Surfaced on every score row to mirror
        # the live_opening_* pattern; only populated on turn 0 (empty otherwise).
        "opening_shape_subgates": _opening_shape_subgates,
        "opening_shape_failure_reasons": _opening_shape_failure_reasons,
        "scene_block_summary": _scene_block_summary,
        "first_actor_block_index": first_actor_block_index_val,
        "narrator_block_count": narrator_block_count_val,
        "structured_narration_summary_kind": structured_narration_summary_kind,
        "opening_event_coverage_pass": path_summary.get("opening_event_coverage_pass"),
        "opening_missing_event_ids": path_summary.get("opening_missing_event_ids"),
        "opening_missing_must_establish": path_summary.get("opening_missing_must_establish"),
        "opening_first_playable_scene_phase_expected": path_summary.get(
            "opening_first_playable_scene_phase_expected"
        ),
        "opening_first_playable_scene_phase_actual": path_summary.get(
            "opening_first_playable_scene_phase_actual"
        ),
        "hard_forbidden_absent": path_summary.get("hard_forbidden_absent"),
        "opening_summary_only_absent": path_summary.get("opening_summary_only_absent"),
        "hard_forbidden_detection": path_summary.get("hard_forbidden_detection"),
        # ADR-0033 §13.10 primary-vs-final clarity (metadata only; no gate semantics).
        "primary_attempt_adapter": path_summary.get("primary_attempt_adapter"),
        "primary_attempt_model": path_summary.get("primary_attempt_model"),
        "primary_attempt_provider": path_summary.get("primary_attempt_provider"),
        "primary_attempt_invocation_mode": path_summary.get("primary_attempt_invocation_mode"),
        "final_adapter": path_summary.get("final_adapter"),
        "final_adapter_invocation_mode": path_summary.get("final_adapter_invocation_mode"),
        "fallback_reason": path_summary.get("fallback_reason"),
        "ldss_fallback_after_live_opening_failure": path_summary.get(
            "ldss_fallback_after_live_opening_failure"
        ),
        "trace_origin": path_summary.get("trace_origin"),
        "execution_tier": path_summary.get("execution_tier"),
        "canonical_player_flow": path_summary.get("canonical_player_flow"),
        "test_case_id": path_summary.get("test_case_id"),
        "runtime_mode": path_summary.get("runtime_mode"),
        "generation_mode": path_summary.get("generation_mode"),
        # PRIMARY-PARSER-EVIDENCE-01: primary attempt diagnosis (score context only; no gate semantics).
        "primary_attempt_api_success": path_summary.get("primary_attempt_api_success"),
        "primary_attempt_parser_error_present": path_summary.get("primary_attempt_parser_error_present"),
        "self_correction_attempted": path_summary.get("self_correction_attempted"),
        "self_correction_attempt_count": path_summary.get("self_correction_attempt_count"),
        "self_correction_success": path_summary.get("self_correction_success"),
        "self_correction_model": path_summary.get("self_correction_model"),
        "self_correction_trigger_source": path_summary.get("self_correction_trigger_source"),
        "runtime_aspect_failure_before_retry": path_summary.get(
            "runtime_aspect_failure_before_retry"
        ),
        "capability_failure_before_retry": path_summary.get("capability_failure_before_retry"),
        "self_correction_resolved_failure": path_summary.get("self_correction_resolved_failure"),
        # OPEN-ACTOR-BLOCK-PROJECTION-01: structured lane → scene_blocks audit fields.
        "actor_block_source": path_summary.get("actor_block_source"),
        "actor_block_filtered_reason": path_summary.get("actor_block_filtered_reason"),
        "actor_line_count_before_projection": path_summary.get("actor_line_count_before_projection"),
        "action_line_count_before_projection": path_summary.get("action_line_count_before_projection"),
        "actor_block_count_after_projection": path_summary.get("actor_block_count_after_projection"),
        # VISIBLE-NARRATIVE-CONTRACT-01 (metadata only; not part of deterministic_scores gates).
        "visible_language_detected": path_summary.get("visible_language_detected"),
        "mixed_language_detected": path_summary.get("mixed_language_detected"),
        "visible_language_contract_pass": path_summary.get("visible_language_contract_pass"),
        "selected_role_visible_in_opening": path_summary.get("selected_role_visible_in_opening"),
        "player_identity_anchor_present": path_summary.get("player_identity_anchor_present"),
        "visible_narrative_contract_version": path_summary.get("visible_narrative_contract_version"),
        "name_only_actor_block_removed": path_summary.get("name_only_actor_block_removed"),
        "label_only_line_removed": path_summary.get("label_only_line_removed"),
        "duplicate_actor_label_removed": path_summary.get("duplicate_actor_label_removed"),
        "placeholder_action_removed": path_summary.get("placeholder_action_removed"),
        "actor_line_action_tail_stripped": path_summary.get("actor_line_action_tail_stripped"),
        "near_duplicate_visible_block_removed": path_summary.get("near_duplicate_visible_block_removed"),
        "player_role_display_name": path_summary.get("player_role_display_name"),
        "session_output_language": path_summary.get("session_output_language"),
        **_transition_diag_for_scores,
    }
    if narrator_path_selected and _turn_number == 0:
        narrator_path_gate_scores = {
            "non_mock_generation_pass",
            "visible_output_present",
            "actor_lane_safety_pass",
            "fallback_absent",
            "usage_present",
            "rag_context_attached",
            "opening_shape_contract_pass",
            "opening_contract_pass",
            "opening_role_anchor_pass",
            "hard_forbidden_absent",
            "opening_summary_only_absent",
            "opening_event_coverage_pass",
            "opening_player_speech_absent",
            "opening_npc_exposition_absent",
            "npc_exposition_absent",
            "player_agency_violation_absent",
            "meta_runtime_language_absent",
            "stage_direction_labels_absent",
            "source_reproduction_absent",
            "live_runtime_contract_pass",
            "live_runtime_visible_surface_pass",
            "live_opening_contract_pass",
        }
        deterministic_scores = {
            key: value
            for key, value in deterministic_scores.items()
            if key in narrator_path_gate_scores
        }
    for name, value in deterministic_scores.items():
        try:
            adapter.add_score(
                name=name,
                value=value,
                comment="deterministic live story runtime evidence gate",
                metadata=dict(score_metadata_base),
            )
        except Exception:
            logger.debug("Langfuse score write failed for %s", name, exc_info=True)

__all__ = ['_emit_langfuse_evidence_observations']
