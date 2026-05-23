"""Opening turn execution.

Runs the opening-turn path that seeds session state, narrator output, and initial visible projection.
"""
from __future__ import annotations

from ._deps import *

class _OpeningExecutionMixin:
    def _run_generic_opening_graph(
        self,
        *,
        session: StorySession,
        prompt: str,
        trace_id: str | None,
        graph_threads: list[dict[str, Any]],
        graph_summary: dict[str, Any],
        host_experience_template: dict[str, Any] | None,
        prior_ci: list[dict[str, Any]],
    ) -> dict[str, Any]:
        actor_lane_ctx = self._extract_actor_lane_context(session)
        try:
            return self.turn_graph.run(
                session_id=session.session_id,
                module_id=session.module_id,
                current_scene_id=session.current_scene_id,
                player_input=prompt,
                trace_id=trace_id,
                host_versions={"world_engine_app_version": APP_VERSION},
                active_narrative_threads=graph_threads or None,
                thread_pressure_summary=graph_summary,
                host_experience_template=host_experience_template,
                prior_continuity_impacts=prior_ci if prior_ci else None,
                prior_callback_web_state=self._prior_callback_web_state_for_graph(session),
                prior_consequence_cascade_state=self._prior_consequence_cascade_state_for_graph(session),
                prior_temporal_control_state=_prior_temporal_control_state_from_session(session),
                prior_expectation_variation_state=_prior_expectation_variation_state_from_session(session),
                prior_narrative_momentum_state=_prior_narrative_momentum_state_from_session(session),
                prior_symbolic_object_resonance_state=_prior_symbolic_object_resonance_state_from_session(session),
                prior_pacing_rhythm_state=_prior_pacing_rhythm_state_from_session(session),
                prior_social_pressure_state=_prior_social_pressure_state_from_session(session),
                prior_relationship_state_record=_prior_relationship_state_record_from_session(session),
                turn_number=0,
                turn_initiator_type="engine",
                turn_input_class="opening",
                live_player_truth_surface=True,
                actor_lane_context=actor_lane_ctx,
                session_input_language=session.session_input_language,
                session_output_language=session.session_output_language,
                story_runtime_experience=self._story_runtime_experience_policy().effective,
                validation_execution_mode=self._validation_execution_mode(),
                environment_state=session.environment_state
                if isinstance(session.environment_state, dict)
                else None,
            )
        except Exception as exc:
            log_story_runtime_failure(
                trace_id=trace_id,
                story_session_id=session.session_id,
                operation="execute_opening",
                message=str(exc),
                failure_class="graph_execution_exception",
            )
            raise

    def _build_opening_graph_state(
        self,
        *,
        session: StorySession,
        trace_id: str | None,
        graph_threads: list[dict[str, Any]],
        graph_summary: dict[str, Any],
        host_experience_template: dict[str, Any] | None,
        prior_ci: list[dict[str, Any]],
    ) -> tuple[str, dict[str, Any]]:
        narrator_path_prompt = "Director selected narrator_path for speech-free canonical opening."
        if session.module_id == GOD_OF_CARNAGE_MODULE_ID:
            return narrator_path_prompt, self._build_narrator_path_opening_state(
                session=session,
                trace_id=trace_id,
            )
        prompt = self._build_opening_prompt(session)
        return prompt, self._run_generic_opening_graph(
            session=session,
            prompt=prompt,
            trace_id=trace_id,
            graph_threads=graph_threads,
            graph_summary=graph_summary,
            host_experience_template=host_experience_template,
            prior_ci=prior_ci,
        )

    def _opening_graph_state_with_fallbacks(self, graph_state: dict[str, Any]) -> dict[str, Any]:
        if not self._opening_commit_acceptable(graph_state):
            validation = graph_state.get("validation_outcome") if isinstance(graph_state.get("validation_outcome"), dict) else {}
            reason = str(validation.get("reason") or "opening_validation_not_approved")
            self.metrics.incr("opening_ldss_fallback", reason=reason)
            return self._ldss_opening_fallback_state(
                graph_state,
                reason=reason,
            )
        if not self._visible_narration_present(graph_state):
            gen = graph_state.get("generation") if isinstance(graph_state.get("generation"), dict) else {}
            gen_error = gen.get("error") or (gen.get("metadata") or {}).get("error") or "no error details available"
            reason = f"no_visible_narration:{gen_error}"
            self.metrics.incr("opening_ldss_fallback", reason="no_visible_narration")
            return self._ldss_opening_fallback_state(
                graph_state,
                reason=reason,
            )
        return graph_state

    def _last_opening_step_id(self, graph_state: dict[str, Any]) -> str:
        opening_step_ids = (
            graph_state.get("narrator_path", {}).get("canonical_step_ids")
            if isinstance(graph_state.get("narrator_path"), dict)
            else None
        ) or []
        if not opening_step_ids:
            opening_step_ids = [
                str(sid).strip()
                for sid in (graph_state.get("opening_scene_sequence", {}).get("canonical_step_ids") or [])
                if str(sid).strip()
            ]
        return opening_step_ids[-1] if opening_step_ids else ""

    def _opening_block_count(self, graph_state: dict[str, Any]) -> int:
        visible_output_bundle = graph_state.get("visible_output_bundle")
        scene_blocks = visible_output_bundle.get("scene_blocks", []) if isinstance(visible_output_bundle, dict) else []
        return len(scene_blocks)

    def _maybe_build_opening_continuation(
        self,
        *,
        session: StorySession,
        graph_state: dict[str, Any],
        last_opening_step_id: str,
        trace_id: str | None,
    ) -> dict[str, Any] | None:
        if not last_opening_step_id or session.module_id != GOD_OF_CARNAGE_MODULE_ID:
            return None
        try:
            return self._build_scripted_continuation(
                session=session,
                after_step_id=last_opening_step_id,
                opening_block_count=self._opening_block_count(graph_state),
                trace_id=trace_id,
            )
        except Exception as exc:
            log_story_runtime_failure(
                trace_id=trace_id,
                story_session_id=session.session_id,
                operation="scripted_continuation",
                message=str(exc),
                failure_class="scripted_continuation_exception",
            )
            return None

    def _opening_state_with_continuation(
        self,
        graph_state: dict[str, Any],
        continuation_result: dict[str, Any] | None,
    ) -> dict[str, Any]:
        if continuation_result and continuation_result.get("scene_blocks"):
            return self._merge_continuation_into_opening_state(
                graph_state,
                continuation_result,
            )
        return graph_state

    def _advance_opening_canonical_step(
        self,
        *,
        session: StorySession,
        continuation_result: dict[str, Any] | None,
        last_opening_step_id: str,
    ) -> None:
        if continuation_result and continuation_result.get("last_step_id"):
            session.canonical_step_id = continuation_result["last_step_id"]
        elif last_opening_step_id:
            session.canonical_step_id = last_opening_step_id

    def _opening_continuation_summary(self, continuation_result: dict[str, Any]) -> dict[str, Any]:
        return {
            "contract": continuation_result.get("contract"),
            "canonical_step_ids": continuation_result.get("canonical_step_ids", []),
            "last_step_id": continuation_result.get("last_step_id"),
            "realized_beat_ids": continuation_result.get("realized_beat_ids", []),
            "stopped_at_player_window": continuation_result.get("stopped_at_player_window", False),
            "stopped_at_beat_id": continuation_result.get("stopped_at_beat_id"),
            "scene_block_count": len(continuation_result.get("scene_blocks", [])),
        }

    def _execute_opening_locked(self, session_id: str, trace_id: str | None) -> dict[str, Any]:
        session = self.get_session(session_id)
        prior_scene_id = session.current_scene_id
        history_tail = session.history[-(NARRATIVE_COMMIT_HISTORY_TAIL - 1) :]
        graph_threads, graph_summary = build_graph_thread_export(session.narrative_threads)
        host_experience_template = (
            goc_host_experience_template(session.runtime_projection)
            if session.module_id == GOD_OF_CARNAGE_MODULE_ID
            else None
        )
        prior_ci = goc_prior_continuity_for_graph(session.module_id, session.prior_continuity_impacts)
        prompt, graph_state = self._build_opening_graph_state(
            session=session,
            trace_id=trace_id,
            graph_threads=graph_threads,
            graph_summary=graph_summary,
            host_experience_template=host_experience_template,
            prior_ci=prior_ci,
        )
        graph_state = self._opening_graph_state_with_fallbacks(graph_state)
        session.updated_at = datetime.now(timezone.utc)
        last_opening_step_id = self._last_opening_step_id(graph_state)
        continuation_result = self._maybe_build_opening_continuation(
            session=session,
            graph_state=graph_state,
            last_opening_step_id=last_opening_step_id,
            trace_id=trace_id,
        )
        graph_state = self._opening_state_with_continuation(graph_state, continuation_result)
        self._advance_opening_canonical_step(
            session=session,
            continuation_result=continuation_result,
            last_opening_step_id=last_opening_step_id,
        )
        result = self._finalize_committed_turn(
            session=session,
            graph_state=graph_state,
            trace_id=trace_id,
            commit_turn_number=0,
            player_input=prompt,
            turn_kind="opening",
            prior_scene_id=prior_scene_id,
            history_tail=history_tail,
            graph_threads=graph_threads,
            graph_summary=graph_summary,
            host_experience_template=host_experience_template,
            prior_ci=prior_ci,
        )

        if continuation_result:
            result["scripted_continuation"] = self._opening_continuation_summary(continuation_result)

        return result

    def execute_opening(self, *, session_id: str, trace_id: str | None = None) -> dict[str, Any]:
        with self._session_turn_lock(session_id):
            session = self.get_session(session_id)
            for row in reversed(session.history or []):
                if isinstance(row, dict) and str(row.get("turn_kind") or "").strip().lower() == "opening":
                    return row
            self._assert_live_player_governance()
            return self._execute_opening_locked(session_id, trace_id=trace_id)

    def _create_story_session_record(
        self,
        *,
        module_id: str,
        runtime_projection: dict[str, Any],
        session_input_language: str | None = None,
        session_output_language: str = DEFAULT_SESSION_LANGUAGE,
        content_provenance: dict[str, Any] | None = None,
        session_id: str | None = None,
    ) -> StorySession:
        _validate_runtime_projection_contract(module_id, runtime_projection)
        session_id = str(session_id or uuid4().hex).strip() or uuid4().hex
        current_scene_id = str(runtime_projection.get("start_scene_id") or "")
        prov = dict(content_provenance) if isinstance(content_provenance, dict) else {}
        if not prov:
            mid = runtime_projection.get("module_id")
            ver = runtime_projection.get("module_version")
            if isinstance(mid, str) and mid.strip():
                prov.setdefault("runtime_projection_module_id", mid.strip())
            if isinstance(ver, str) and ver.strip():
                prov.setdefault("runtime_projection_module_version", ver.strip())
        session = StorySession(
            session_id=session_id,
            module_id=module_id,
            runtime_projection=runtime_projection,
            current_scene_id=current_scene_id,
            session_input_language=session_input_language or session_output_language,
            session_output_language=session_output_language,
            content_provenance=prov,
        )
        env_model = build_environment_model(
            module_id=module_id,
            runtime_profile_id=_runtime_profile_id_from_projection(runtime_projection),
        )
        session.environment_state = normalize_environment_state(
            None,
            module_id=module_id,
            environment_model=env_model,
            runtime_projection=runtime_projection,
            actor_lane_context=self._extract_actor_lane_context(session),
            turn_number=0,
        )
        session.runtime_world = initialize_runtime_world(
            module_id=module_id,
            runtime_projection=runtime_projection,
            environment_model=env_model,
            environment_state=session.environment_state,
        )
        session.diagnostics.append(
            runtime_world_session_diagnostic(
                session.runtime_world,
                session_id=session_id,
            )
        )
        self.sessions[session_id] = session
        with self._session_locks_guard:
            self._session_turn_locks.setdefault(session_id, threading.Lock())
        self._persist_session(session)
        return session


__all__ = ["_OpeningExecutionMixin"]
