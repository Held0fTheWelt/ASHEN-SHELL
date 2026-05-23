"""Session-state API helpers.

Provides manager-facing read and update helpers for authoritative session state surfaces.
"""
from __future__ import annotations

from .._deps import *
from ..actor_tracking.session_state_w5_view import _maybe_build_w5_player_view_for_session
from .session_state_readout_parts import (
    build_canonical_turn_counts,
    build_narrative_commit_summary,
    copy_session_surface_snapshot,
    extract_last_commit_lists,
    extract_last_committed_turn_surfaces,
)
from .session_state_response_parts import (
    build_committed_state_readout,
    build_session_loop_readout,
    build_session_state_response,
)


class _SessionStateApiMixin:
    def get_state(self, session_id: str) -> dict[str, Any]:
        session = self.get_session(session_id)
        last_surfaces = extract_last_committed_turn_surfaces(session)
        last_committed_turn = last_surfaces.get("last_committed_turn")
        last_narrative_commit = last_surfaces.get("last_narrative_commit")
        last_committed_turn_authority = last_surfaces.get("last_committed_turn_authority")
        last_dramatic_context_summary = last_surfaces.get("last_dramatic_context_summary")
        last_actor_turn_summary = last_surfaces.get("last_actor_turn_summary")
        last_branching_forecast = last_surfaces.get("last_branching_forecast")
        summary, last_actor_turn_summary = build_narrative_commit_summary(
            last_narrative_commit=last_narrative_commit,
            last_actor_turn_summary=last_actor_turn_summary,
        )
        last_consequences, last_open_pressures = extract_last_commit_lists(last_narrative_commit)

        thread_metrics = thread_continuity_metrics(session.narrative_threads)
        module_scope_truth = _module_scope_truth(session.module_id)
        _, memory_policy = _load_module_memory_policy(
            module_id=session.module_id,
            runtime_profile_id=_runtime_profile_id_from_projection(
                session.runtime_projection if isinstance(session.runtime_projection, dict) else None
            ),
        )
        hierarchical_memory_context = project_hierarchical_memory_context(
            snapshot=session.hierarchical_memory
            if isinstance(session.hierarchical_memory, dict)
            else None,
            memory_policy=memory_policy,
        )
        last_thread_summary: str | None = None
        if session.last_thread_update_trace is not None:
            last_thread_summary = session.last_thread_update_trace.summary or None

        story_entries = _story_window_entries_for_session(session)
        runtime_world = session.runtime_world if isinstance(session.runtime_world, dict) else {}
        runtime_world_summary = self._runtime_world_summary(runtime_world)
        session_loop = build_session_loop_readout(
            session=session,
            runtime_world=runtime_world,
            runtime_world_summary=runtime_world_summary,
        )
        player_shell_context = _player_shell_context_from_dramatic_context(
            last_dramatic_context_summary,
            session=session,
        )
        w5_player_view, w5_player_view_diagnostics = _maybe_build_w5_player_view_for_session(session)
        history_rows = session.history or []
        canonical_counts = build_canonical_turn_counts(history_rows)
        callback_web_snapshot = copy_session_surface_snapshot(
            self.get_callback_web,
            session_id=session.session_id,
        )
        consequence_cascade_snapshot = copy_session_surface_snapshot(
            self.get_consequence_cascade,
            session_id=session.session_id,
        )
        committed_state = build_committed_state_readout(
            session=session,
            last_narrative_commit=last_narrative_commit,
            last_committed_turn_authority=last_committed_turn_authority,
            last_dramatic_context_summary=last_dramatic_context_summary,
            last_actor_turn_summary=last_actor_turn_summary,
            last_branching_forecast=last_branching_forecast,
            callback_web_snapshot=callback_web_snapshot,
            consequence_cascade_snapshot=consequence_cascade_snapshot,
            player_shell_context=player_shell_context,
            module_scope_truth=module_scope_truth,
            summary=summary,
            last_consequences=last_consequences,
            last_open_pressures=last_open_pressures,
            last_thread_summary=last_thread_summary,
            thread_metrics=thread_metrics,
            hierarchical_memory_context=hierarchical_memory_context,
            w5_player_view=w5_player_view,
            w5_player_view_diagnostics=w5_player_view_diagnostics,
        )

        return build_session_state_response(
            session=session,
            canonical_counts=canonical_counts,
            runtime_world=runtime_world,
            session_loop=session_loop,
            history_rows=history_rows,
            committed_state=committed_state,
            module_scope_truth=module_scope_truth,
            player_shell_context=player_shell_context,
            last_branching_forecast=last_branching_forecast,
            callback_web_snapshot=callback_web_snapshot,
            consequence_cascade_snapshot=consequence_cascade_snapshot,
            story_entries=story_entries,
            last_committed_turn=last_committed_turn,
            w5_player_view=w5_player_view,
            w5_player_view_diagnostics=w5_player_view_diagnostics,
        )


__all__ = ["_SessionStateApiMixin"]
