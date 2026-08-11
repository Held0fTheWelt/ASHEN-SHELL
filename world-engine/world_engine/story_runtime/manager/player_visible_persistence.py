"""Player-visible persistence helpers.

Persists player-visible turn events and rendered surfaces after authoritative runtime commit.
"""
from __future__ import annotations

from ._deps import *
from .commit_side_effects import apply_committed_turn_side_effects
from world_engine.story_runtime.persist_outcome import persist_outcome_payload
from .player_visible_canonical_record import build_player_visible_canonical_record
from .player_visible_event_defaults import (
    copy_player_visible_defaults_to_graph_state,
    prepare_player_visible_event,
)
from .player_visible_runtime_surfaces import copy_player_visible_runtime_surfaces

class _PlayerVisiblePersistenceMixin:
    def _persist_player_visible_turn_event(
        self,
        *,
        session: StorySession,
        graph_state: dict[str, Any],
        event: dict[str, Any],
        trace_id: str | None,
        commit_turn_number: int,
        player_input: str,
        turn_outcome: str,
    ) -> dict[str, Any]:
        """Persist a player-visible non-approved outcome as a canonical turn."""
        interpreted_input, selected_responder_set, human_att = prepare_player_visible_event(
            session=session,
            graph_state=graph_state,
            event=event,
            trace_id=trace_id,
            commit_turn_number=commit_turn_number,
            player_input=player_input,
        )
        copy_player_visible_runtime_surfaces(
            event=event,
            graph_state=graph_state,
            selected_responder_set=selected_responder_set,
        )
        copy_player_visible_defaults_to_graph_state(
            graph_state=graph_state,
            event=event,
            interpreted_input=interpreted_input,
        )
        _record_hierarchical_memory_aspect(
            session=session,
            graph_state=graph_state,
            event=event,
            committed_turn={
                "canonical_turn_id": event.get("canonical_turn_id"),
                "module_id": session.module_id,
                "runtime_profile_id": _runtime_profile_id_from_projection(
                    session.runtime_projection if isinstance(session.runtime_projection, dict) else None
                ),
                "turn_number": commit_turn_number,
                "turn_kind": event.get("turn_kind") or "player_rejected_recoverable",
                "turn_outcome": turn_outcome,
                "recoverable_outcome": True,
                "no_dead_end_recovery": event.get("no_dead_end_recovery"),
                "narrative_commit": event.get("narrative_commit"),
                "turn_aspect_ledger": event.get("turn_aspect_ledger"),
                "visible_output_bundle": event.get("visible_output_bundle"),
            },
            allow_write=False,
        )
        if isinstance(event.get("diagnostics"), dict):
            event["diagnostics"]["turn_aspect_ledger"] = event.get("turn_aspect_ledger")
            event["diagnostics"]["hierarchical_memory"] = event.get("hierarchical_memory")
        turn_lc = TurnLifecycleChain()
        turn_lc.advance("received")
        turn_lc.advance("interpreted")
        turn_lc.advance("generated_or_resolved")
        turn_lc.advance("validated")
        turn_lc.advance("committed")
        turn_lc.advance("projected")

        canonical_record = build_player_visible_canonical_record(
            session=session,
            graph_state=graph_state,
            event=event,
            trace_id=trace_id,
            commit_turn_number=commit_turn_number,
            turn_outcome=turn_outcome,
            human_att=human_att,
        )
        canonical_record["lifecycle_state"] = "observed"
        event["lifecycle_state"] = "observed"
        session.history.append(canonical_record)
        apply_committed_turn_side_effects(
            self,
            session=session,
            graph_state=graph_state,
            event=event,
            include_w5_shadow=False,
        )
        session.updated_at = datetime.now(timezone.utc)
        persistence_outcome = self._persist_session(session)
        turn_lc.advance("persisted")
        persistence_evidence = persist_outcome_payload(persistence_outcome)
        event["persistence_outcome"] = persistence_evidence
        canonical_record["persistence_outcome"] = persistence_evidence
        turn_lc.advance("observed")
        return event


__all__ = ["_PlayerVisiblePersistenceMixin"]
