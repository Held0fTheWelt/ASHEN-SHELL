"""Unsharded manager method `_finalize_committed_turn` (Wave 1)."""
from __future__ import annotations

from ._deps import *
from .commit_evidence_projection import build_commit_evidence_projection
from world_engine.story_runtime.persist_outcome import persist_outcome_payload
from .visible_projection_policy import (
    resolve_visible_projection_policy,
    rich_scene_projection_enabled,
)


class _CommitFinalizationMixin:
    def _finalize_committed_turn(
        self,
        *,
        session: StorySession,
        graph_state: dict[str, Any],
        trace_id: str | None,
        commit_turn_number: int,
        player_input: str,
        turn_kind: str | None,
        prior_scene_id: str,
        history_tail: list,
        graph_threads: list[dict[str, Any]] | None,
        graph_summary: str | None,
        host_experience_template: dict[str, Any] | None,
        prior_ci: list[dict[str, Any]] | None,
    ) -> dict[str, Any]:
        visible_projection_policy = resolve_visible_projection_policy(
            module_id=session.module_id,
            runtime_projection=session.runtime_projection,
            graph_state=graph_state,
        )
        use_rich_scene_projection = rich_scene_projection_enabled(visible_projection_policy)
        prior_narrative_threads_for_rollback = copy.deepcopy(session.narrative_threads)
        prior_thread_update_trace_for_rollback = copy.deepcopy(session.last_thread_update_trace)
        prior_continuity_impacts_for_rollback = copy.deepcopy(session.prior_continuity_impacts)
        goc_append_continuity_impacts(session.module_id, session.prior_continuity_impacts, graph_state)
        graph_diag = graph_state.get("graph_diagnostics", {}) if isinstance(graph_state.get("graph_diagnostics"), dict) else {}
        errors = graph_diag.get("errors", []) if isinstance(graph_diag.get("errors"), list) else []
        gen = graph_state.get("generation", {}) if isinstance(graph_state.get("generation"), dict) else {}
        interpreted_input = graph_state.get("interpreted_input", {})
        if not isinstance(interpreted_input, dict):
            interpreted_input = {}
        validation_outcome = (
            graph_state.get("validation_outcome") if isinstance(graph_state.get("validation_outcome"), dict) else {}
        )
        turn_lc = TurnLifecycleChain()
        turn_lc.advance("received")
        turn_lc.advance("interpreted")
        prior_beat = _prior_beat_from_session(session)
        narrative_commit = resolve_narrative_commit(
            turn_number=commit_turn_number,
            prior_scene_id=prior_scene_id,
            player_input=player_input,
            interpreted_input=interpreted_input,
            generation=gen,
            runtime_projection=session.runtime_projection,
            graph_state=graph_state,
            prior_beat_progression=prior_beat,
        )
        model_ok = gen.get("success") is True
        turn_lc.advance("generated_or_resolved")
        turn_lc.advance("validated")
        session.current_scene_id = narrative_commit.committed_scene_id
        if isinstance(graph_state.get("environment_state"), dict):
            session.environment_state = dict(graph_state["environment_state"])
        session.narrative_threads, session.last_thread_update_trace = update_narrative_threads(
            prior=session.narrative_threads,
            latest_commit=narrative_commit,
            history_tail=history_tail,
            committed_scene_id=narrative_commit.committed_scene_id,
            turn_number=commit_turn_number,
        )
        turn_lc.advance("committed")
        outcome = "ok" if model_ok and not errors else "degraded"
        actor_survival_telemetry = (
            graph_state.get("actor_survival_telemetry")
            if isinstance(graph_state.get("actor_survival_telemetry"), dict)
            else {}
        )
        vitality_telemetry_v1 = (
            actor_survival_telemetry.get("vitality_telemetry_v1")
            if isinstance(actor_survival_telemetry.get("vitality_telemetry_v1"), dict)
            else None
        )
        passivity_diagnosis_v1 = (
            actor_survival_telemetry.get("passivity_diagnosis_v1")
            if isinstance(actor_survival_telemetry.get("passivity_diagnosis_v1"), dict)
            else None
        )

        commit_evidence = build_commit_evidence_projection(
            graph_state=graph_state,
            generation=gen,
            validation_outcome=validation_outcome,
            model_ok=model_ok,
            errors=errors,
            committed=narrative_commit is not None,
        )

        log_story_turn_event(
            trace_id=trace_id,
            story_session_id=session.session_id,
            module_id=session.module_id,
            turn_number=commit_turn_number,
            player_input=player_input,
            outcome=outcome,
            graph_error_count=len(errors),
            quality_class=str(graph_state.get("quality_class") or "") or None,
            degradation_signals=list(graph_state.get("degradation_signals") or []),
            vitality_telemetry=vitality_telemetry_v1,
            passivity_diagnosis=passivity_diagnosis_v1,
            llm_invocation_details=commit_evidence["llm_invocation_details"],
            validation_details=commit_evidence["validation_details"],
            commit_details=commit_evidence["commit_details"],
            retrieval_details=commit_evidence["retrieval_details"],
        )
        narrative_commit_payload = narrative_commit.model_dump(mode="json")
        beat_payload = (
            narrative_commit_payload.get("beat_progression")
            if isinstance(narrative_commit_payload.get("beat_progression"), dict)
            else {}
        )
        if isinstance(graph_state.get("turn_aspect_ledger"), dict) and beat_payload:
            ledger_for_beat_commit = normalize_runtime_aspect_ledger(graph_state.get("turn_aspect_ledger"))
            aspects_for_beat = ledger_for_beat_commit.get("turn_aspect_ledger")
            beat_record = aspects_for_beat.get(ASPECT_BEAT) if isinstance(aspects_for_beat, dict) else {}
            if isinstance(beat_record, dict):
                graph_state["turn_aspect_ledger"] = set_aspect_record(
                    ledger_for_beat_commit,
                    ASPECT_BEAT,
                    make_aspect_record(
                        applicable=True,
                        status=str(beat_record.get("status") or "partial"),
                        expected=beat_record.get("expected")
                        if isinstance(beat_record.get("expected"), dict)
                        else {},
                        selected=beat_record.get("selected")
                        if isinstance(beat_record.get("selected"), dict)
                        else {"selected_beat_id": beat_payload.get("beat_id")},
                        actual={
                            **(beat_record.get("actual") if isinstance(beat_record.get("actual"), dict) else {}),
                            "committed": True,
                            "committed_beat_id": beat_payload.get("beat_id"),
                            "beat_slot": beat_payload.get("beat_slot"),
                            "advanced": beat_payload.get("advanced"),
                            "advancement_reason": beat_payload.get("advancement_reason"),
                        },
                        reasons=beat_record.get("reasons") if isinstance(beat_record.get("reasons"), list) else [],
                        source="commit",
                        selected_beat=beat_payload.get("beat_id"),
                    ),
                )
        turn_thread_metrics = thread_continuity_metrics(session.narrative_threads)
        dramatic_context_summary = _build_committed_dramatic_context_summary(
            graph_state=graph_state,
            narrative_commit_payload=narrative_commit_payload,
            thread_metrics=turn_thread_metrics,
        )
        committed_turn_authority = _build_committed_turn_authority(
            narrative_commit_payload=narrative_commit_payload,
            graph_state=graph_state,
            committed_scene_id=session.current_scene_id,
            turn_number=commit_turn_number,
            dramatic_context_summary=dramatic_context_summary,
        )
        r_src = str(self._runtime_config_status.get("source") or "")
        governed_active = r_src in {"governed_runtime_config", "governed_runtime_config_with_injected_adapters"} and not bool(
            self._runtime_config_status.get("live_execution_blocked")
        )
        gov: dict[str, Any] = {
            "source": self._runtime_config_status.get("source"),
            "config_version": self._runtime_config_status.get("config_version"),
            "governed_runtime_active": governed_active,
            "legacy_default_registry_path": r_src == "default_registry",
            "live_execution_blocked": bool(self._runtime_config_status.get("live_execution_blocked")),
            # The authority version records which authority binding shaped this
            # committed turn. ``reload_runtime_config`` bumps the version; a
            # turn committed after reload shows the new value, making the live
            # binding auditable rather than inferred.
            "authority_version": self._authority_version,
            "authority_applied_at_iso": self._authority_applied_at_iso,
        }
        routing = graph_state.get("routing") if isinstance(graph_state.get("routing"), dict) else {}
        gov["primary_route_selection"] = {
            "selected_model_id": routing.get("selected_model"),
            "selected_provider_id": routing.get("selected_provider"),
            "route_reason_code": routing.get("route_reason_code"),
            "fallback_chain": routing.get("fallback_chain"),
            "route_id": routing.get("route_id"),
            "route_family": routing.get("route_family"),
            "route_family_expected": routing.get("route_family_expected"),
            "route_substitution_occurred": bool(routing.get("route_substitution_occurred")),
        }
        gov["fallback_stage_reached"] = routing.get("fallback_stage_reached") or (
            "graph_fallback_executed" if "fallback_model" in (graph_state.get("nodes_executed") or []) else "primary_only"
        )
        gen_meta = gen.get("metadata") if isinstance(gen.get("metadata"), dict) else {}
        gov["final_model_invocation"] = {
            "adapter": gen_meta.get("adapter"),
            "api_model": gen_meta.get("model"),
            "adapter_invocation_mode": gen_meta.get("adapter_invocation_mode"),
        }
        gov["route_selected_model"] = routing.get("selected_model")
        gov["route_selected_provider"] = routing.get("selected_provider")
        gov["route_reason_code"] = routing.get("route_reason_code")
        gov["adapter"] = gen_meta.get("adapter")
        gov["api_model"] = gen_meta.get("model")
        if graph_state.get("director_path_mode"):
            gov["director_path_mode"] = graph_state.get("director_path_mode")
            gov["director_narrator_path_plan"] = graph_state.get("director_narrator_path_plan")
            gov["narrator_path"] = graph_state.get("narrator_path")
        self_correction = graph_state.get("self_correction") if isinstance(graph_state.get("self_correction"), dict) else {}
        gov["self_correction_attempt_count"] = self_correction.get("attempt_count")
        val = validation_outcome
        gov["validation_reason"] = val.get("reason")
        gov["mock_output_flag"] = bool(str(gen.get("content") or "").strip().startswith("[mock]"))
\
        gov["transition_pattern"] = graph_state.get("transition_pattern")
        gov["dramatic_quality_gate"] = val.get("dramatic_quality_gate")
        gate_outcome = val.get("dramatic_effect_gate_outcome") if isinstance(val.get("dramatic_effect_gate_outcome"), dict) else {}
        gov["dramatic_effect_rationale_codes"] = (
            list(gate_outcome.get("effect_rationale_codes") or [])
            if isinstance(gate_outcome, dict)
            else []
        )
        actor_lane_validation = val.get("actor_lane_validation") if isinstance(val.get("actor_lane_validation"), dict) else {}
        gov["actor_lane_validation_status"] = actor_lane_validation.get("status")
        gov["actor_lane_validation_reason"] = actor_lane_validation.get("reason")
        gov["quality_class"] = graph_state.get("quality_class")
        gov["degradation_signals"] = list(graph_state.get("degradation_signals") or [])
        gov["degradation_summary"] = graph_state.get("degradation_summary")
        # The live player-turn path always routes through ``run_validation_seam``
        # inside the graph, which populates ``validator_lane``. Publishing it
        # here makes the "which validator ran" question auditable per turn and
        # distinguishes the canonical live lane from the operator endpoint at
        # /api/internal/narrative/runtime/validate-and-recover.
        gov["validator_lane"] = val.get("validator_lane")
        gov["validator_layers_used"] = narrative_commit.planner_truth.validator_layers_used
        reconciliation = graph_state.get("responder_reconciliation")
        if isinstance(reconciliation, dict):
            gov["responder_reconciliation"] = reconciliation
        social_summary = narrative_commit.planner_truth.social_state_summary
        if social_summary:
            gov["social_state_truth"] = {
                "committed": True,
                "fingerprint": social_summary.get("fingerprint"),
                "validated": social_summary.get("validated"),
                "social_risk_band": social_summary.get("social_risk_band"),
                "responder_asymmetry_code": social_summary.get("responder_asymmetry_code"),
                "social_continuity_status": social_summary.get("social_continuity_status"),
                "prior_social_state_fingerprint": social_summary.get("prior_social_state_fingerprint"),
            }
        # Publish the committed beat identity and the advancement decision on
        # the per-turn governance surface so continuity is observable turn by
        # turn, alongside authority, routing, and validator truth.
        if narrative_commit.beat_progression is not None:
            bp = narrative_commit.beat_progression
            gov["beat_progression"] = {
                "beat_id": bp.beat_id,
                "beat_slot": bp.beat_slot,
                "advanced": bp.advanced,
                "advancement_reason": bp.advancement_reason,
                "continuity_carry_forward_reason": bp.continuity_carry_forward_reason,
                "prior_beat_id": bp.prior_beat_id,
                "pressure_state": bp.pressure_state,
            }
        gov["dramatic_context_summary"] = dramatic_context_summary
        if isinstance(graph_state.get("scene_energy_target"), dict):
            gov["scene_energy_target"] = graph_state.get("scene_energy_target")
        if isinstance(graph_state.get("scene_energy_transition"), dict):
            gov["scene_energy_transition"] = graph_state.get("scene_energy_transition")
        if isinstance(graph_state.get("scene_energy_validation"), dict):
            gov["scene_energy_validation"] = graph_state.get("scene_energy_validation")
        if isinstance(graph_state.get("pacing_rhythm_state"), dict):
            gov["pacing_rhythm_state"] = graph_state.get("pacing_rhythm_state")
        if isinstance(graph_state.get("pacing_rhythm_target"), dict):
            gov["pacing_rhythm_target"] = graph_state.get("pacing_rhythm_target")
        if isinstance(graph_state.get("pacing_rhythm_validation"), dict):
            gov["pacing_rhythm_validation"] = graph_state.get("pacing_rhythm_validation")
        if isinstance(graph_state.get("temporal_control_state"), dict):
            gov["temporal_control_state"] = graph_state.get("temporal_control_state")
        if isinstance(graph_state.get("temporal_control_target"), dict):
            gov["temporal_control_target"] = graph_state.get("temporal_control_target")
        if isinstance(graph_state.get("temporal_control_validation"), dict):
            gov["temporal_control_validation"] = graph_state.get("temporal_control_validation")
        if isinstance(graph_state.get("sensory_context_state"), dict):
            gov["sensory_context_state"] = graph_state.get("sensory_context_state")
        if isinstance(graph_state.get("sensory_context_target"), dict):
            gov["sensory_context_target"] = graph_state.get("sensory_context_target")
        if isinstance(graph_state.get("sensory_context_validation"), dict):
            gov["sensory_context_validation"] = graph_state.get("sensory_context_validation")
        if isinstance(graph_state.get("genre_awareness_state"), dict):
            gov["genre_awareness_state"] = graph_state.get("genre_awareness_state")
        if isinstance(graph_state.get("genre_awareness_target"), dict):
            gov["genre_awareness_target"] = graph_state.get("genre_awareness_target")
        if isinstance(graph_state.get("genre_awareness_validation"), dict):
            gov["genre_awareness_validation"] = graph_state.get("genre_awareness_validation")
        if isinstance(graph_state.get("tonal_consistency_target"), dict):
            gov["tonal_consistency_target"] = graph_state.get("tonal_consistency_target")
        if isinstance(graph_state.get("tonal_consistency_validation"), dict):
            gov["tonal_consistency_validation"] = graph_state.get("tonal_consistency_validation")
        if isinstance(graph_state.get("narrative_momentum_state"), dict):
            gov["narrative_momentum_state"] = graph_state.get("narrative_momentum_state")
        if isinstance(graph_state.get("narrative_momentum_target"), dict):
            gov["narrative_momentum_target"] = graph_state.get("narrative_momentum_target")
        if isinstance(graph_state.get("narrative_momentum_validation"), dict):
            gov["narrative_momentum_validation"] = graph_state.get(
                "narrative_momentum_validation"
            )
        if isinstance(graph_state.get("symbolic_object_resonance_state"), dict):
            gov["symbolic_object_resonance_state"] = graph_state.get(
                "symbolic_object_resonance_state"
            )
        if isinstance(graph_state.get("symbolic_object_resonance_target"), dict):
            gov["symbolic_object_resonance_target"] = graph_state.get(
                "symbolic_object_resonance_target"
            )
        if isinstance(graph_state.get("symbolic_object_resonance_validation"), dict):
            gov["symbolic_object_resonance_validation"] = graph_state.get(
                "symbolic_object_resonance_validation"
            )
        if isinstance(graph_state.get("social_pressure_state"), dict):
            gov["social_pressure_state"] = graph_state.get("social_pressure_state")
        if isinstance(graph_state.get("social_pressure_target"), dict):
            gov["social_pressure_target"] = graph_state.get("social_pressure_target")
        if isinstance(graph_state.get("social_pressure_validation"), dict):
            gov["social_pressure_validation"] = graph_state.get("social_pressure_validation")
        if isinstance(graph_state.get("expectation_variation_state"), dict):
            gov["expectation_variation_state"] = graph_state.get("expectation_variation_state")
        if isinstance(graph_state.get("expectation_variation_target"), dict):
            gov["expectation_variation_target"] = graph_state.get("expectation_variation_target")
        if isinstance(graph_state.get("expectation_variation_validation"), dict):
            gov["expectation_variation_validation"] = graph_state.get("expectation_variation_validation")
        if isinstance(session.environment_state, dict) and session.environment_state:
            gov["environment_state"] = session.environment_state
        # Story Runtime Experience packaging: re-pack the visible bundle
        # according to the governed experience policy. The policy is a real
        # first-class runtime value pulled from the resolved config, so
        # recap / dramatic_turn / live modes differ in packaging truth, not
        # only in prompt wording.
        raw_bundle = graph_state.get("visible_output_bundle")
        experience_policy = self._story_runtime_experience_policy()
        packaged_bundle = self._apply_experience_packaging(raw_bundle, experience_policy)
        packaged_bundle = _finalize_visible_bundle_opening_gm_narration(
            session=session,
            graph_state=graph_state,
            packaged_bundle=packaged_bundle,
            commit_turn_number=commit_turn_number,
            normalization_enabled=bool(
                visible_projection_policy.get("opening_narration_normalization_enabled")
            ),
        )
        visible_bundle_for_summary = (
            packaged_bundle if isinstance(packaged_bundle, dict) else raw_bundle if isinstance(raw_bundle, dict) else {}
        )
        actor_turn_summary = _build_actor_turn_summary(
            graph_state=graph_state,
            visible_output_bundle=visible_bundle_for_summary,
            dramatic_context_summary=dramatic_context_summary,
        )
        selected_responder_set = (
            graph_state.get("selected_responder_set")
            if isinstance(graph_state.get("selected_responder_set"), list)
            else []
        )
        if selected_responder_set:
            gov["selected_responder_set"] = selected_responder_set
            gov["selected_responder_ids"] = [
                str(row.get("actor_id") or row.get("responder_id") or "").strip()
                for row in selected_responder_set
                if isinstance(row, dict)
                and str(row.get("actor_id") or row.get("responder_id") or "").strip()
            ]
        if vitality_telemetry_v1:
            gov["vitality_telemetry_v1"] = vitality_telemetry_v1
            gov["realized_actor_ids"] = list(vitality_telemetry_v1.get("realized_actor_ids") or [])
            gov["rendered_actor_ids"] = list(vitality_telemetry_v1.get("rendered_actor_ids") or [])
            passivity_diagnosis = (
                actor_survival_telemetry.get("passivity_diagnosis_v1")
                if isinstance(actor_survival_telemetry.get("passivity_diagnosis_v1"), dict)
                else {}
            )
            operator_hints = (
                actor_survival_telemetry.get("operator_diagnostic_hints")
                if isinstance(actor_survival_telemetry.get("operator_diagnostic_hints"), dict)
                else {}
            )
            canonical_diagnosis = passivity_diagnosis if passivity_diagnosis else operator_hints
            if passivity_diagnosis:
                gov["passivity_diagnosis_v1"] = passivity_diagnosis
            gov["why_turn_felt_passive"] = list(canonical_diagnosis.get("why_turn_felt_passive") or [])
            gov["primary_passivity_factors"] = list(canonical_diagnosis.get("primary_passivity_factors") or [])
        quality_class, degradation_signals, degradation_summary = _canonical_quality_fields_from_surfaces(
            runtime_governance_surface=gov,
            authority_summary={
                "validation_status": val.get("status"),
                "commit_applied": bool((graph_state.get("committed_result") or {}).get("commit_applied")),
            },
        )
        gov["quality_class"] = quality_class
        gov["degradation_signals"] = degradation_signals
        gov["degradation_summary"] = degradation_summary
        turn_aspect_ledger = (
            normalize_runtime_aspect_ledger(graph_state.get("turn_aspect_ledger"))
            if isinstance(graph_state.get("turn_aspect_ledger"), dict)
            else None
        )
        turn_aspect_ledger = ensure_runtime_aspect_ledger(
            turn_aspect_ledger,
            session_id=session.session_id,
            module_id=session.module_id,
            turn_number=commit_turn_number,
            turn_kind=turn_kind or "player",
            raw_player_input=player_input,
            input_kind=interpreted_input.get("player_input_kind") or interpreted_input.get("kind"),
            trace_id=trace_id,
            runtime_profile_id=_runtime_profile_id_from_projection(
                session.runtime_projection if isinstance(session.runtime_projection, dict) else None
            ),
        )
        turn_aspect_ledger = _stamp_turn_aspect_ledger_identity(
            turn_aspect_ledger,
            session=session,
            commit_turn_number=commit_turn_number,
            turn_kind=turn_kind or "player",
        )
        canonical_turn_id = _canonical_turn_id(session.session_id, commit_turn_number)
        runtime_profile_id = _runtime_profile_id_from_projection(
            session.runtime_projection if isinstance(session.runtime_projection, dict) else None
        )
        narrator_path_opening = (
            str(turn_kind or "").strip().lower() == "opening"
            and str(graph_state.get("director_path_mode") or "").strip() == "narrator_path"
        )
        if narrator_path_opening:
            branching_forecast = {
                "schema_version": "branching_forecast.v1",
                "status": "not_applicable",
                "forecast_only": True,
                "authoritative": False,
                "inactive_branches_authoritative": False,
                "mutates_canonical_state": False,
                "option_count": 0,
                "reason": "narrator_path_opening_no_player_branch",
            }
        else:
            branching_forecast = build_branching_forecast(
                story_session_id=session.session_id,
                module_id=session.module_id,
                runtime_profile_id=runtime_profile_id,
                canonical_turn_id=canonical_turn_id,
                turn_number=commit_turn_number,
                turn_kind=turn_kind or "player",
                narrative_commit=narrative_commit_payload,
                narrative_threads=session.narrative_threads.model_dump(mode="json")
                if hasattr(session.narrative_threads, "model_dump")
                else session.narrative_threads,
                thread_metrics=turn_thread_metrics,
                selected_responder_set=selected_responder_set,
                actor_turn_summary=actor_turn_summary,
\
                graph_state=graph_state,
            )
        if isinstance(turn_aspect_ledger, dict):
            turn_aspect_ledger = dict(turn_aspect_ledger)
            turn_aspect_ledger["branching_forecast"] = branching_forecast
            turn_aspect_ledger = normalize_runtime_aspect_ledger(turn_aspect_ledger)
            graph_state["turn_aspect_ledger"] = turn_aspect_ledger
        graph_state["branching_forecast"] = branching_forecast
        gov["branching_forecast"] = {
            "status": branching_forecast.get("status"),
            "option_count": branching_forecast.get("option_count"),
            "forecast_only": branching_forecast.get("forecast_only"),
            "inactive_branches_authoritative": branching_forecast.get("inactive_branches_authoritative"),
            "mutates_canonical_state": branching_forecast.get("mutates_canonical_state"),
        }
        gov["visible_projection_policy"] = dict(visible_projection_policy)
        scene_plan_record = (
            graph_state.get("scene_plan_record")
            if isinstance(graph_state.get("scene_plan_record"), dict)
            else {}
        )
        narrative_move_proposal = (
            scene_plan_record.get("narrative_move_proposal")
            if isinstance(scene_plan_record.get("narrative_move_proposal"), dict)
            else None
        )
        if narrative_move_proposal:
            gov["narrative_move_proposal"] = dict(narrative_move_proposal)
        event: dict[str, Any] = {
            "turn_number": commit_turn_number,
            "canonical_turn_id": canonical_turn_id,
            "turn_kind": turn_kind or "player",
            "trace_id": trace_id or "",
            "raw_input": player_input,
            "turn_aspect_ledger": turn_aspect_ledger,
            "interpreted_input": interpreted_input,
            "narrative_commit": narrative_commit_payload,
            "retrieval": graph_state.get("retrieval", {}),
            "model_route": {**routing, "generation": gen},
            "graph": graph_diag,
            "visible_output_bundle": packaged_bundle if packaged_bundle is not None else raw_bundle,
            "story_runtime_experience": experience_policy.to_truth_surface(),
            "dramatic_context_summary": dramatic_context_summary,
            "diagnostics_refs": graph_state.get("diagnostics_refs"),
            "experiment_preview": graph_state.get("experiment_preview"),
            "validation_outcome": val,
            "committed_result": graph_state.get("committed_result"),
            "committed_turn_authority": committed_turn_authority,
            "environment_state": session.environment_state
            if isinstance(session.environment_state, dict)
            else {},
            "selected_scene_function": graph_state.get("selected_scene_function"),
            "director_path_mode": graph_state.get("director_path_mode"),
            "director_narrator_path_plan": graph_state.get("director_narrator_path_plan"),
            "narrator_path": graph_state.get("narrator_path"),
            "scene_energy_target": graph_state.get("scene_energy_target"),
            "scene_energy_transition": graph_state.get("scene_energy_transition"),
            "scene_energy_validation": graph_state.get("scene_energy_validation"),
            "temporal_control_state": graph_state.get("temporal_control_state"),
            "temporal_control_target": graph_state.get("temporal_control_target"),
            "temporal_control_validation": graph_state.get("temporal_control_validation"),
            "social_pressure_state": graph_state.get("social_pressure_state"),
            "social_pressure_target": graph_state.get("social_pressure_target"),
            "social_pressure_validation": graph_state.get("social_pressure_validation"),
            "tonal_consistency_target": graph_state.get("tonal_consistency_target"),
            "tonal_consistency_validation": graph_state.get("tonal_consistency_validation"),
            "expectation_variation_state": graph_state.get("expectation_variation_state"),
            "expectation_variation_target": graph_state.get("expectation_variation_target"),
            "expectation_variation_validation": graph_state.get("expectation_variation_validation"),
            "narrative_momentum_state": graph_state.get("narrative_momentum_state"),
            "narrative_momentum_target": graph_state.get("narrative_momentum_target"),
            "narrative_momentum_validation": graph_state.get("narrative_momentum_validation"),
            "dramatic_irony_record": graph_state.get("dramatic_irony_record"),
            "dramatic_irony_validation": graph_state.get("dramatic_irony_validation"),
            "selected_responder_set": selected_responder_set,
            "visibility_class_markers": graph_state.get("visibility_class_markers"),
            "failure_markers": graph_state.get("failure_markers"),
            "self_correction": self_correction,
            "branching_forecast": branching_forecast,
            "actor_survival_telemetry": actor_survival_telemetry,
            "actor_turn_summary": actor_turn_summary,
            "narrative_move_proposal": dict(narrative_move_proposal)
            if narrative_move_proposal
            else None,
            "runtime_governance_surface": gov,
        }
        projection_aspect_recorded = False

        def _recover_if_projection_gate_blocks_commit() -> dict[str, Any] | None:
            failure = _runtime_aspect_commit_blocking_failure(
                event.get("turn_aspect_ledger")
                if isinstance(event.get("turn_aspect_ledger"), dict)
                else graph_state.get("turn_aspect_ledger")
                if isinstance(graph_state.get("turn_aspect_ledger"), dict)
                else None
            )
            if not failure:
                return None
            reason = str(failure.get("failure_reason") or "runtime_aspect_projection_failure")
            session.current_scene_id = prior_scene_id
            session.narrative_threads = copy.deepcopy(prior_narrative_threads_for_rollback)
            session.last_thread_update_trace = copy.deepcopy(prior_thread_update_trace_for_rollback)
            session.prior_continuity_impacts = copy.deepcopy(prior_continuity_impacts_for_rollback)
            if str(turn_kind or "").strip().lower() == "opening":
                raise RuntimeError(f"Opening projection contract failure: {reason}")

            message = _recoverable_turn_message(session=session, reason=reason)
            turn_aspect_ledger = _recoverable_runtime_aspect_ledger(
                session_id=session.session_id,
                module_id=session.module_id,
                turn_number=commit_turn_number,
                turn_kind="player_projection_rejected_recoverable",
                player_input=player_input,
                trace_id=trace_id,
                reason=reason,
                validation_status="rejected",
                existing_ledger=event.get("turn_aspect_ledger")
                if isinstance(event.get("turn_aspect_ledger"), dict)
                else graph_state.get("turn_aspect_ledger")
                if isinstance(graph_state.get("turn_aspect_ledger"), dict)
                else None,
                visible_output_present=True,
            )
            val_projection: dict[str, Any] = {
                "status": "rejected",
                "reason": reason,
                "validator_lane": "runtime_aspect_projection_gate_v1",
                "recoverable_rejection": True,
                "hard_boundary_failure": False,
                "runtime_aspect_failure": failure,
            }
            recoverable_event = _recoverable_playable_turn_envelope(
                session=session,
                commit_turn_number=commit_turn_number,
                player_input=player_input,
                trace_id=trace_id,
                turn_kind="player_projection_rejected_recoverable",
                interpreted_input=interpreted_input,
                narrative_commit={
                    "situation_status": "continue",
                    "allowed": False,
                    "commit_reason_code": "runtime_aspect_projection_gate",
                    "committed_scene_id": prior_scene_id,
                    "proposed_scene_id": prior_scene_id,
                    "selected_candidate_source": "runtime_aspect_projection_gate",
                    "is_terminal": False,
                },
                validation_outcome=val_projection,
                message=message,
                turn_aspect_ledger=turn_aspect_ledger,
                reason=reason,
                diagnostics_extras={
                    "failure_class": failure.get("failure_class"),
                    "runtime_aspect_failure": failure,
                },
            )
            graph_state["turn_aspect_ledger"] = recoverable_event.get("turn_aspect_ledger")
            graph_state["validation_outcome"] = val_projection
            graph_state["visible_output_bundle"] = recoverable_event["visible_output_bundle"]
            graph_state["committed_result"] = {
                "commit_applied": False,
                "committed_effects": [],
                "reason": reason,
                "runtime_aspect_failure": failure,
            }
            return self._persist_player_visible_turn_event(
                session=session,
                graph_state=graph_state,
                event=recoverable_event,
                trace_id=trace_id,
                commit_turn_number=commit_turn_number,
                player_input=player_input,
                turn_outcome="recoverable_projection_failure",
            )
        if not use_rich_scene_projection:
            generic_scene_blocks = _scene_blocks_from_visible_bundle(
                event.get("visible_output_bundle")
                if isinstance(event.get("visible_output_bundle"), dict)
                else None
            )
            if generic_scene_blocks:
                event["turn_aspect_ledger"] = _record_visible_projection_aspect(
                    ledger=event.get("turn_aspect_ledger")
                    if isinstance(event.get("turn_aspect_ledger"), dict)
                    else graph_state.get("turn_aspect_ledger")
                    if isinstance(graph_state.get("turn_aspect_ledger"), dict)
                    else None,
                    session_id=session.session_id,
                    module_id=session.module_id,
                    turn_number=commit_turn_number,
                    turn_kind=turn_kind or "player",
                    raw_player_input=player_input,
                    trace_id=trace_id,
                    scene_blocks=generic_scene_blocks,
                )
                projection_aspect_recorded = True
                graph_state["turn_aspect_ledger"] = event["turn_aspect_ledger"]
                blocked_projection_event = _recover_if_projection_gate_blocks_commit()
                if blocked_projection_event is not None:
                    return blocked_projection_event
        # Build SceneTurnEnvelope.v2 for modules that explicitly select the
        # rich scene projection profile. Module identity is not a dispatch key.
        # Live graph/model output is primary. LDSS is reserved as the final
        # deterministic fallback when the live path cannot produce scene blocks.
        scene_turn_envelope: dict[str, Any] | None = None
        if use_rich_scene_projection:
            live_scene_blocks = []
            if gen.get("success") is True and not graph_state.get("force_ldss_scene_fallback"):
                gen_meta_for_blocks = gen.get("metadata") if isinstance(gen.get("metadata"), dict) else {}
                structured_for_projection = (
                    gen_meta_for_blocks.get("structured_output")
                    if isinstance(gen_meta_for_blocks.get("structured_output"), dict)
                    else None
                )
                if structured_for_projection is None and isinstance(gen.get("structured_output"), dict):
                    structured_for_projection = gen["structured_output"]
                live_scene_blocks = _live_scene_blocks_from_visible_bundle(
                    event.get("visible_output_bundle")
                    if isinstance(event.get("visible_output_bundle"), dict)
                    else {},
                    turn_number=commit_turn_number,
                    structured_output=structured_for_projection,
                    runtime_projection=session.runtime_projection
                    if isinstance(session.runtime_projection, dict)
                    else None,
                    graph_state=graph_state,
                    session_output_language=session.session_output_language,
                    player_input=player_input,
                    story_runtime_experience=experience_policy.effective,
                )
                if visible_projection_policy.get("opening_shape") == "two_movement_paragraphs":
                    live_scene_blocks = _maybe_split_opening_into_two_movements(
                        live_scene_blocks,
                        commit_turn_number=commit_turn_number,
                    )
            if live_scene_blocks:
                event_bundle = (
                    event.get("visible_output_bundle")
                    if isinstance(event.get("visible_output_bundle"), dict)
                    else {}
                )
                event["visible_output_bundle"] = {
                    **event_bundle,
                    "scene_blocks": [dict(block) for block in live_scene_blocks],
                }
                event["turn_aspect_ledger"] = _record_visible_projection_aspect(
                    ledger=event.get("turn_aspect_ledger")
                    if isinstance(event.get("turn_aspect_ledger"), dict)
                    else graph_state.get("turn_aspect_ledger")
                    if isinstance(graph_state.get("turn_aspect_ledger"), dict)
                    else None,
                    session_id=session.session_id,
                    module_id=session.module_id,
                    turn_number=commit_turn_number,
                    turn_kind=turn_kind or "player",
                    raw_player_input=player_input,
                    trace_id=trace_id,
                    scene_blocks=[dict(block) for block in live_scene_blocks if isinstance(block, dict)],
\
                )
                projection_aspect_recorded = True
                graph_state["turn_aspect_ledger"] = event["turn_aspect_ledger"]
                scene_turn_envelope = _build_live_scene_turn_envelope(
                    session=session,
                    graph_state=graph_state,
                    scene_blocks=live_scene_blocks,
                    turn_number=commit_turn_number,
                )
                graph_state.setdefault("phase_costs", {})["live_scene_projection"] = build_deterministic_phase_cost(
                    phase="live_scene_projection",
                    provider="world_engine",
                    model="live_runtime_graph_projection",
                    scene_block_count=len(live_scene_blocks),
                    visible_actor_response_present=bool(
                        scene_turn_envelope.get("diagnostics", {})
                        .get("npc_agency", {})
                        .get("visible_actor_response_present")
                    ),
                )
            elif visible_projection_policy.get("deterministic_fallback") == "ldss_v1":
                ldss_span = None
                try:
                    from world_engine.observability.langfuse_adapter import LangfuseAdapter
                    adapter = LangfuseAdapter.get_instance()
                    if adapter and adapter.is_enabled():
                        logger.info(f"[MANAGER] Creating LDSS fallback span for session {session.session_id}, turn {commit_turn_number}")
                        ldss_span = adapter.create_child_span(
                            name="story.phase.ldss_fallback",
                            input={
                                "session_id": session.session_id,
                                "turn_number": commit_turn_number,
                                "player_input_length": len(player_input) if player_input else 0,
                                "fallback_reason": "live_scene_blocks_missing",
                            },
                            metadata={
                                "phase": "ldss_fallback",
                                "turn_number": commit_turn_number,
                                "session_id": session.session_id,
                            }
                        )
                except Exception as e:
                    logger.error(f"[MANAGER] Exception creating LDSS fallback span: {e}", exc_info=True)

                try:
                    scene_turn_envelope = _build_ldss_scene_envelope(
                        session=session,
                        graph_state=graph_state,
                        player_input=player_input,
                        turn_number=commit_turn_number,
                    )
                    if scene_turn_envelope and ldss_span:
                        ldss_phase_cost = {}
                        if isinstance(scene_turn_envelope, dict):
                            diagnostics = scene_turn_envelope.get("diagnostics")
                            if isinstance(diagnostics, dict) and isinstance(diagnostics.get("phase_cost"), dict):
                                ldss_phase_cost = diagnostics["phase_cost"]
                        if not ldss_phase_cost:
                            raw_costs = graph_state.get("phase_costs")
                            if isinstance(raw_costs, dict) and isinstance(raw_costs.get("ldss"), dict):
                                ldss_phase_cost = raw_costs["ldss"]
                        ldss_span.update(
                            output={
                                "block_count": len(scene_turn_envelope.get("visible_scene_output", {}).get("blocks", [])) if isinstance(scene_turn_envelope.get("visible_scene_output"), dict) else 0,
                                "decision_count": scene_turn_envelope.get("decision_count", 0) if isinstance(scene_turn_envelope, dict) else 0,
                                "status": "approved"
                            },
                            metadata={
                                **ldss_phase_cost,
                                "phase_cost": dict(ldss_phase_cost),
                            }
                        )
                finally:
                    if ldss_span:
                        logger.info(f"[MANAGER] Ending LDSS fallback span")
                        ldss_span.end()

            if scene_turn_envelope:
                # Phase 2 Stage B/C — Dual Mode Block Stream (ADR-0058).
                # Augment envelope with parallel block_stream_events when the
                # feature flag is on. Real capability outputs from graph_state
                # are extracted and passed so NPC motivation scores use actual
                # runtime signals rather than defaults where available.
                # Bundle path and all existing keys are preserved unchanged.
                try:
                    from ai_stack.story_runtime.block_stream_dual_mode import (
                        augment_envelope_with_block_stream,
                        is_dual_mode_enabled,
                        is_primary_enabled,
                    )
                    from ai_stack.story_runtime.stream_readiness import (
                        compute_primary_selection,
                        compute_stream_readiness,
                        extract_capability_outputs_from_graph_state,
                        extract_module_policies_for_director,
                    )
                    if is_dual_mode_enabled():
                        cap_outputs = extract_capability_outputs_from_graph_state(graph_state)
                        # Stage F: pull Director policies from graph_state / module config.
                        module_policy_dict = (
                            graph_state.get("module_runtime_policy")
                            if isinstance(graph_state.get("module_runtime_policy"), dict)
                            else None
                        )
                        director_policies = extract_module_policies_for_director(
                            graph_state, module_policy_dict
                        )
                        off_stage_updates_policy = (
                            module_policy_dict.get("runtime_governance_policy", {}).get("off_stage_updates")
                            if isinstance(module_policy_dict, dict)
                            and isinstance(module_policy_dict.get("runtime_governance_policy"), dict)
                            else None
                        )
                        scene_turn_envelope = augment_envelope_with_block_stream(
                            scene_turn_envelope,
                            npc_ids=list(scene_turn_envelope.get("npc_actor_ids") or []),
                            scene_energy_output=cap_outputs["scene_energy_output"],
                            social_pressure_output=cap_outputs["social_pressure_output"],
                            relationship_state_output=cap_outputs["relationship_state_output"],
                            narrative_momentum_output=cap_outputs["narrative_momentum_output"],
                            actor_pressure_profiles=director_policies["actor_pressure_profiles"],
                            npc_motivation_score_policy=director_policies["npc_motivation_score_policy"],
                            pacing_rhythm_policy=director_policies["pacing_rhythm_policy"],
                            off_stage_updates_policy=off_stage_updates_policy,
                        )
                        # Stage C: readiness + primary selection — read-only, additive.
                        # Bundle path and all existing keys are never mutated.
                        readiness = compute_stream_readiness(
                            scene_turn_envelope,
                            graph_state=graph_state,
                            ws_session_loop_supported=False,
                            frontend_event_adapter_deployed=True,
                        )
                        primary_selection = compute_primary_selection(readiness)
                        primary_selection["primary_flag_enabled"] = is_primary_enabled()
                        existing_diag = scene_turn_envelope.get("diagnostics") or {}
                        scene_turn_envelope = {
                            **scene_turn_envelope,
                            "diagnostics": {
                                **existing_diag,
                                "phase2_event_stream_readiness": readiness,
                                "phase2_primary_selection": primary_selection,
                            },
                        }
                except Exception:
                    pass  # Dual-mode failure must never break the bundle path.

                event["scene_turn_envelope"] = scene_turn_envelope
                visible_scene_output = (
                    scene_turn_envelope.get("visible_scene_output")
                    if isinstance(scene_turn_envelope.get("visible_scene_output"), dict)
                    else {}
                )
                blocks = visible_scene_output.get("blocks")
                if isinstance(blocks, list) and blocks:
                    raw_scene_blocks = [dict(block) for block in blocks if isinstance(block, dict)]
                    projected_scene_blocks = _live_scene_blocks_from_visible_bundle(
                        {"scene_blocks": raw_scene_blocks},
                        turn_number=commit_turn_number,
                        structured_output=None,
                        runtime_projection=session.runtime_projection
                        if isinstance(session.runtime_projection, dict)
                        else None,
                        graph_state=graph_state,
                        session_output_language=session.session_output_language,
                        player_input=player_input,
                        story_runtime_experience=experience_policy.effective,
                    )
                    if not projected_scene_blocks:
                        projected_scene_blocks = raw_scene_blocks
                    visible_scene_output["blocks"] = [
                        dict(block) for block in projected_scene_blocks if isinstance(block, dict)
                    ]
                    event_bundle = (
                        event.get("visible_output_bundle")
                        if isinstance(event.get("visible_output_bundle"), dict)
                        else {}
                    )
                    event["visible_output_bundle"] = _ensure_gm_narration_from_narrator_scene_blocks(
                        {
                            **event_bundle,
                            "scene_blocks": [
                                dict(block)
                                for block in projected_scene_blocks
                                if isinstance(block, dict)
                            ],
                        }
                    )
                    event["turn_aspect_ledger"] = _record_visible_projection_aspect(
                        ledger=event.get("turn_aspect_ledger")
                        if isinstance(event.get("turn_aspect_ledger"), dict)
                        else graph_state.get("turn_aspect_ledger")
                        if isinstance(graph_state.get("turn_aspect_ledger"), dict)
                        else None,
                        session_id=session.session_id,
                        module_id=session.module_id,
                        turn_number=commit_turn_number,
                        turn_kind=turn_kind or "player",
                        raw_player_input=player_input,
                        trace_id=trace_id,
                        scene_blocks=[
                            dict(block)
                            for block in projected_scene_blocks
                            if isinstance(block, dict)
                        ],
                    )
                    projection_aspect_recorded = True
                    graph_state["turn_aspect_ledger"] = event["turn_aspect_ledger"]

            if not projection_aspect_recorded:
                generic_scene_blocks = _scene_blocks_from_visible_bundle(
                    event.get("visible_output_bundle")
                    if isinstance(event.get("visible_output_bundle"), dict)
                    else None
                )
                if generic_scene_blocks:
                    event["turn_aspect_ledger"] = _record_visible_projection_aspect(
                        ledger=event.get("turn_aspect_ledger")
                        if isinstance(event.get("turn_aspect_ledger"), dict)
                        else graph_state.get("turn_aspect_ledger")
                        if isinstance(graph_state.get("turn_aspect_ledger"), dict)
                        else None,
                        session_id=session.session_id,
                        module_id=session.module_id,
                        turn_number=commit_turn_number,
                        turn_kind=turn_kind or "player",
                        raw_player_input=player_input,
                        trace_id=trace_id,
                        scene_blocks=generic_scene_blocks,
                    )
                    projection_aspect_recorded = True
                    graph_state["turn_aspect_ledger"] = event["turn_aspect_ledger"]

            blocked_projection_event = _recover_if_projection_gate_blocks_commit()
            if blocked_projection_event is not None:
                return blocked_projection_event

            # MVP3: Orchestrate NarrativeRuntimeAgent streaming (after LDSS produces NPCAgencyPlan).
            # Opening turns already own the first visible narrative through the canonical opening
            # contract; streaming ambience here would prepend generic narrator cards before that
\
            # authored transition.
            runtime_state = {
                "session_id": session.session_id,
                "current_scene_id": session.current_scene_id,
                "actor_positions": graph_state.get("actor_positions", {}),
                "narrative_threads": [t.model_dump() if hasattr(t, 'model_dump') else t
                                     for t in (session.narrative_threads.active if hasattr(session.narrative_threads, 'active') else [])],
            }
            dramatic_context = (
                graph_state.get("dramatic_context_summary", {})
                if isinstance(graph_state.get("dramatic_context_summary"), dict)
                else {}
            )
            if narrator_path_opening:
                narrator_packet = {
                    "contract": "narrator_packet.v1",
                    "mode": "narrator_path_already_projected",
                    "streaming_required": False,
                    "opening_scene_sequence": graph_state.get("opening_scene_sequence")
                    if isinstance(graph_state.get("opening_scene_sequence"), dict)
                    else None,
                }
            else:
                narrator_packet = build_narrator_packet(
                    opening_scene_sequence=graph_state.get("opening_scene_sequence")
                    if isinstance(graph_state.get("opening_scene_sequence"), dict)
                    else None,
                    hard_forbidden_rules=graph_state.get("hard_forbidden_rules")
                    if isinstance(graph_state.get("hard_forbidden_rules"), dict)
                    else None,
                    actor_lane_context=self._extract_actor_lane_context(session),
                    session_output_language=session.session_output_language,
                    story_runtime_experience=experience_policy.effective,
                )
            runtime_state["narrator_packet"] = narrator_packet
            narrative_threads_list = [t.model_dump() if hasattr(t, 'model_dump') else t
                                     for t in (session.narrative_threads.active if hasattr(session.narrative_threads, 'active') else [])]

            # MVP4: Create child span for Narrator phase
            narrator_span = None
            previous_active_span = None
            adapter = None
            try:
                from world_engine.observability.langfuse_adapter import LangfuseAdapter
                adapter = LangfuseAdapter.get_instance()
                if not narrator_path_opening and adapter and adapter.is_enabled():
                    logger.info(f"[MANAGER] Creating Narrator phase span for session {session.session_id}, turn {commit_turn_number}")
                    narrator_span = adapter.create_child_span(
                        name="story.phase.narrator",
                        input={
                            "session_id": session.session_id,
                            "turn_number": commit_turn_number,
                            "npc_agency_plan": scene_turn_envelope.get("npc_agency_plan") if isinstance(scene_turn_envelope, dict) else None,
                            "narrator_packet": narrator_packet,
                        },
                        metadata={
                            "phase": "narrator",
                            "turn_number": commit_turn_number,
                            "session_id": session.session_id,
                        }
                    )
                    # Set as active span so NarrativeRuntimeAgent can create child spans
                    if narrator_span:
                        logger.info(f"[MANAGER] Narrator phase span created, setting as active context")
                        previous_active_span = adapter.get_active_span()
                        adapter.set_active_span(narrator_span)
                    else:
                        logger.warning(f"[MANAGER] Narrator phase span creation returned None")
            except Exception as e:
                logger.error(f"[MANAGER] Exception creating Narrator phase span: {e}", exc_info=True)

            try:
                if str(turn_kind or "").strip().lower() == "opening":
                    streaming_started = False
                else:
                    streaming_started = _orchestrate_narrative_agent(
                        manager=self,
                        session_id=session.session_id,
                        ldss_output=scene_turn_envelope,
                        runtime_state=runtime_state,
                        dramatic_signature=dramatic_context,
                        narrative_threads=narrative_threads_list,
                        turn_number=commit_turn_number,
                        trace_id=trace_id,
                        narrator_packet=narrator_packet,
                    )

                if streaming_started:
                    narrator_phase_cost = build_deterministic_phase_cost(
                        phase="narrator",
                        provider="world_engine",
                        model="narrative_runtime_agent_scheduled",
                        streaming_started=True,
                    )
                    graph_state.setdefault("phase_costs", {})["narrator"] = narrator_phase_cost

                if streaming_started and narrator_span:
                    narrator_span.update(
                        output={
                            "status": "streaming_started"
                        },
                        metadata={
                            **narrator_phase_cost,
                            "phase_cost": dict(narrator_phase_cost),
                        },
                    )
            finally:
                if narrator_span:
                    logger.info(f"[MANAGER] Ending Narrator phase span")
                    narrator_span.end()
                    logger.info(f"[MANAGER] Narrator phase span ended")
                if adapter is not None and narrator_span is not None:
                    adapter.set_active_span(previous_active_span)

            if streaming_started:
                event["narrative_agent_started"] = True
                event["narrator_streaming"] = {
                    "status": "streaming",
                    "session_id": session.session_id,
                }

        # MVP4: Build DiagnosticsEnvelope from committed state only.
        # Never exposes raw AI proposals as committed truth.
        if visible_projection_policy.get("diagnostics_envelope_enabled"):
            try:
                # Phase B: Collect degradation events
                degradation_events = []
                signals = graph_state.get("degradation_signals") or []
                for signal in signals:
                    severity = "critical" if signal in ("execution_error", "graph_error") \
                               else "moderate" if "fallback" in signal \
                               else "minor"
                    degradation_events.append(DegradationEvent(
                        marker=signal.upper(),
                        severity=severity,
                        timestamp=datetime.now(timezone.utc).isoformat(),
                        recovery_successful=graph_state.get("committed_result", {}).get("commit_applied", False),
                        context_snapshot={"turn_number": commit_turn_number},
                    ))

                _ensure_model_generation_phase_cost(graph_state)
                cost_summary = aggregate_phase_costs(graph_state.get("phase_costs", {}))

                diag_envelope = build_diagnostics_envelope(
                    session_id=session.session_id,
                    turn_number=commit_turn_number,
                    trace_id=trace_id or "",
                    player_input=player_input,
                    runtime_projection=session.runtime_projection,
                    graph_state=graph_state,
                    scene_turn_envelope=scene_turn_envelope,
                    langfuse_trace_id=get_langfuse_trace_id() or "",
                    langfuse_enabled=self._get_tracing_config(session.session_id),
                    degradation_events=degradation_events,
                )
                # Update cost_summary in the envelope
                diag_envelope.cost_summary = cost_summary
                event["diagnostics_envelope"] = diag_envelope.to_dict()
            except Exception as exc:
                log_story_runtime_failure(
                    trace_id=trace_id or "",
                    story_session_id=session.session_id,
                    operation="diagnostics_envelope",
                    message=str(exc),
                    failure_class="diagnostics_construction_error",
                )
                raise

        # Langfuse path summary and evidence scores must run after live projection
        # populates ``scene_blocks`` (GoC); otherwise ``visible_output_present`` is 0.
        if event.get("turn_status") is None:
            tk_final = str(turn_kind or "").strip().lower()
            if tk_final == "opening":
                event["turn_status"] = "opening_committed"
            else:
                event["turn_status"] = "committed" if outcome == "ok" else "committed_degraded"
        event.setdefault("http_status", 200)
        if visible_projection_policy.get("human_input_attribution_enabled"):
            human_att = _build_human_input_attribution_record(
                session=session,
                graph_state=graph_state,
                interpreted_input=interpreted_input,
                selected_responder_set=selected_responder_set,
                commit_turn_number=commit_turn_number,
                player_input=player_input,
            )
            graph_state["human_input_attribution"] = human_att
            event["human_input_attribution"] = human_att
        _reconcile_governance_passivity_with_final_projection(event)
        _attach_no_dead_end_recovery_to_event(
            session=session,
            graph_state=graph_state,
            event=event,
            player_input=player_input,
            turn_number=commit_turn_number,
            turn_kind=turn_kind or "player",
            turn_outcome=outcome,
            recoverable_outcome=False,
        )
        memory_source_turn = {
            "canonical_turn_id": event.get("canonical_turn_id"),
            "module_id": session.module_id,
            "runtime_profile_id": _runtime_profile_id_from_projection(
                session.runtime_projection if isinstance(session.runtime_projection, dict) else None
            ),
            "turn_number": commit_turn_number,
            "turn_kind": turn_kind or "player",
            "turn_outcome": outcome,
            "narrative_commit": narrative_commit_payload,
            "committed_turn_authority": committed_turn_authority,
            "dramatic_context_summary": dramatic_context_summary,
            "actor_turn_summary": actor_turn_summary,
            "no_dead_end_recovery": event.get("no_dead_end_recovery"),
            "turn_aspect_ledger": event.get("turn_aspect_ledger"),
            "visible_output_bundle": event.get("visible_output_bundle"),
            "committed_state_after": {
                "current_scene_id": session.current_scene_id,
                "turn_counter": session.turn_counter,
                "environment_state": session.environment_state
                if isinstance(session.environment_state, dict)
                else {},
            },
        }
        _record_hierarchical_memory_aspect(
            session=session,
            graph_state=graph_state,
            event=event,
            committed_turn=memory_source_turn,
            allow_write=True,
        )
        turn_lc.advance("projected")

        committed_record = {
            "canonical_turn_id": event.get("canonical_turn_id"),
            "turn_number": commit_turn_number,
            "turn_kind": turn_kind or "player",
            "trace_id": trace_id or "",
            "turn_outcome": outcome,
            "narrative_commit": narrative_commit_payload,
            "committed_turn_authority": committed_turn_authority,
\
            "dramatic_context_summary": dramatic_context_summary,
            "actor_turn_summary": actor_turn_summary,
            "branching_forecast": event.get("branching_forecast"),
            "no_dead_end_recovery": event.get("no_dead_end_recovery"),
            "turn_aspect_ledger": event.get("turn_aspect_ledger"),
            "visible_output_bundle": event.get("visible_output_bundle"),
            "scene_energy_target": event.get("scene_energy_target"),
            "scene_energy_transition": event.get("scene_energy_transition"),
            "scene_energy_validation": event.get("scene_energy_validation"),
            "temporal_control_state": event.get("temporal_control_state"),
            "temporal_control_target": event.get("temporal_control_target"),
            "temporal_control_validation": event.get("temporal_control_validation"),
            "social_pressure_state": event.get("social_pressure_state"),
            "social_pressure_target": event.get("social_pressure_target"),
            "social_pressure_validation": event.get("social_pressure_validation"),
            "expectation_variation_state": event.get("expectation_variation_state"),
            "expectation_variation_target": event.get("expectation_variation_target"),
            "expectation_variation_validation": event.get("expectation_variation_validation"),
            "narrative_momentum_state": event.get("narrative_momentum_state"),
            "narrative_momentum_target": event.get("narrative_momentum_target"),
            "narrative_momentum_validation": event.get("narrative_momentum_validation"),
            "human_input_attribution": event.get("human_input_attribution"),
            "hierarchical_memory_update": event.get("hierarchical_memory"),
            "committed_state_after": {
                "current_scene_id": session.current_scene_id,
                "turn_counter": session.turn_counter,
                "environment_state": session.environment_state
                if isinstance(session.environment_state, dict)
                else {},
            },
        }
        if isinstance(event.get("narrator_streaming"), dict):
            committed_record["narrator_streaming"] = event["narrator_streaming"]
        committed_record["lifecycle_state"] = "observed"
        event["lifecycle_state"] = "observed"
        session.history.append(committed_record)
        self._refresh_callback_web_after_commit(
            session=session,
            event=event,
            graph_state=graph_state,
        )
        self._refresh_consequence_cascade_after_commit(
            session=session,
            event=event,
            graph_state=graph_state,
        )
        self._emit_observability_path_for_event(session=session, graph_state=graph_state, event=event)
        session.diagnostics.append(event)
        # ADR-0063: W5 Actor Situation Tracker shadow extraction (Phase 1).
        # Best-effort; never fails the turn. No consumer reads w5_history yet.
        self._w5_shadow_extract_after_commit(
            session=session,
            graph_state=graph_state if isinstance(graph_state, dict) else {},
            event=event,
        )
        persistence_outcome = self._persist_session(session)
        turn_lc.advance("persisted")
        persistence_evidence = persist_outcome_payload(persistence_outcome)
        event["persistence_outcome"] = persistence_evidence
        committed_record["persistence_outcome"] = persistence_evidence
        turn_lc.advance("observed")
        return event


__all__ = ['_CommitFinalizationMixin']
