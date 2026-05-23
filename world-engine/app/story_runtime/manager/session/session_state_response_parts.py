"""Response builders for the session-state API."""
from __future__ import annotations

from .._deps import *


def build_session_loop_readout(
    *,
    session: StorySession,
    runtime_world: dict[str, Any],
    runtime_world_summary: dict[str, Any],
) -> dict[str, Any]:
    return {
        "status": "runtime_engine_initialized"
        if runtime_world.get("status") == "initialized"
        else "runtime_engine_uninitialized",
        "session_id": session.session_id,
        "module_id": session.module_id,
        "turn_counter": session.turn_counter,
        "current_scene_id": session.current_scene_id,
        "history_len": len(session.history),
        "diagnostics_len": len(session.diagnostics),
        "runtime_world": runtime_world_summary,
    }


def build_committed_state_readout(
    *,
    session: StorySession,
    last_narrative_commit: dict[str, Any] | None,
    last_committed_turn_authority: dict[str, Any] | None,
    last_dramatic_context_summary: dict[str, Any] | None,
    last_actor_turn_summary: dict[str, Any] | None,
    last_branching_forecast: dict[str, Any] | None,
    callback_web_snapshot: dict[str, Any] | None,
    consequence_cascade_snapshot: dict[str, Any] | None,
    player_shell_context: dict[str, Any],
    module_scope_truth: dict[str, Any],
    summary: dict[str, Any] | None,
    last_consequences: list[str],
    last_open_pressures: list[str],
    last_thread_summary: str | None,
    thread_metrics: dict[str, Any],
    hierarchical_memory_context: dict[str, Any],
    w5_player_view: dict[str, Any] | None,
    w5_player_view_diagnostics: dict[str, Any] | None,
) -> dict[str, Any]:
    state = {
        "current_scene_id": session.current_scene_id,
        "turn_counter": session.turn_counter,
        "environment_state": session.environment_state
        if isinstance(session.environment_state, dict)
        else {},
        "last_narrative_commit": last_narrative_commit,
        "last_committed_turn_authority": last_committed_turn_authority,
        "last_dramatic_context_summary": last_dramatic_context_summary,
        "last_actor_turn_summary": last_actor_turn_summary,
        "last_branching_forecast": last_branching_forecast,
        "callback_web": callback_web_snapshot,
        "callback_web_continuity": callback_web_snapshot,
        "consequence_cascade": consequence_cascade_snapshot,
        "last_actor_outcome_summary": (
            last_actor_turn_summary.get("last_actor_outcome_summary")
            if isinstance(last_actor_turn_summary, dict)
            else None
        ),
        "player_shell_context": player_shell_context,
        "module_scope_truth": module_scope_truth,
        "last_narrative_commit_summary": summary,
        "last_committed_consequences": last_consequences,
        "last_open_pressures": last_open_pressures,
        "narrative_thread_continuity": {
            "narrative_threads": session.narrative_threads.model_dump(mode="json"),
            "active_narrative_threads": [
                t.model_dump(mode="json")
                for t in session.narrative_threads.active
                if t.status != "resolved"
            ],
            "thread_count": thread_metrics["thread_count"],
            "dominant_thread_kind": thread_metrics["dominant_thread_kind"],
            "thread_pressure_level": thread_metrics["thread_pressure_level"],
            "last_narrative_thread_update_summary": last_thread_summary,
        },
        "hierarchical_memory": {
            "snapshot": session.hierarchical_memory,
            "context": hierarchical_memory_context,
        },
    }
    if w5_player_view_diagnostics is not None:
        state["w5_player_view"] = w5_player_view
        state["w5_player_view_diagnostics"] = w5_player_view_diagnostics
    return state


def build_session_state_response(
    *,
    session: StorySession,
    canonical_counts: dict[str, Any],
    runtime_world: dict[str, Any],
    session_loop: dict[str, Any],
    history_rows: list[Any],
    committed_state: dict[str, Any],
    module_scope_truth: dict[str, Any],
    player_shell_context: dict[str, Any],
    last_branching_forecast: dict[str, Any] | None,
    callback_web_snapshot: dict[str, Any] | None,
    consequence_cascade_snapshot: dict[str, Any] | None,
    story_entries: list[dict[str, Any]],
    last_committed_turn: Any,
    w5_player_view: dict[str, Any] | None,
    w5_player_view_diagnostics: dict[str, Any] | None,
) -> dict[str, Any]:
    response = {
        "session_id": session.session_id,
        "module_id": session.module_id,
        "turn_counter": session.turn_counter,
        "committed_canonical_turn_count": canonical_counts["committed_canonical_turn_count"],
        "opening_committed": canonical_counts["opening_committed"],
        "player_committed_turns": canonical_counts["player_committed_turns"],
        "total_canonical_turns": canonical_counts["total_canonical_turns"],
        "canonical_turn_count": canonical_counts["total_canonical_turns"],
        "latest_canonical_turn_id": canonical_counts["latest_canonical_turn_id"],
        "current_scene_id": session.current_scene_id,
        "content_provenance": session.content_provenance,
        "runtime_projection": session.runtime_projection,
        "runtime_world": runtime_world,
        "session_loop": session_loop,
        "history_count": len(history_rows),
        "committed_state": committed_state,
        "module_scope_truth": module_scope_truth,
        "player_shell_context": player_shell_context,
        "branching_forecast": last_branching_forecast,
        "callback_web": callback_web_snapshot,
        "consequence_cascade": consequence_cascade_snapshot,
        "story_window": {
            "contract": "authoritative_story_window_v1",
            "source": "world_engine_story_runtime",
            "entries": story_entries,
            "entry_count": len(story_entries),
            "latest_entry": story_entries[-1] if story_entries else None,
        },
        "last_committed_turn": last_committed_turn,
        "updated_at": session.updated_at.isoformat(),
    }
    if w5_player_view_diagnostics is not None:
        response["w5_player_view"] = w5_player_view
        response["w5_player_view_diagnostics"] = w5_player_view_diagnostics
        response["feature_flags"] = {"W5_AST_FRONTEND_PLAYER_VIEW_ENABLED": True}
    return response


__all__ = [
    "build_committed_state_readout",
    "build_session_loop_readout",
    "build_session_state_response",
]
