"""Defaulting and attribution setup for player-visible turn events."""
from __future__ import annotations

from ._deps import *
from .recoverable_aspect_ledger import _canonical_turn_id, _stamp_turn_aspect_ledger_identity
from .session.session_payloads import _build_human_input_attribution_record


def prepare_player_visible_event(
    *,
    session: StorySession,
    graph_state: dict[str, Any],
    event: dict[str, Any],
    trace_id: str | None,
    commit_turn_number: int,
    player_input: str,
) -> tuple[dict[str, Any], list[Any], dict[str, Any]]:
    event.setdefault("canonical_turn_id", _canonical_turn_id(session.session_id, commit_turn_number))
    event.setdefault("http_status", 200)
    event.setdefault("turn_status", "rejected_recoverable")
    event.setdefault("trace_id", trace_id or "")
    event.setdefault("raw_input", player_input)
    if isinstance(event.get("turn_aspect_ledger"), dict):
        event["turn_aspect_ledger"] = _stamp_turn_aspect_ledger_identity(
            event.get("turn_aspect_ledger"),
            session=session,
            commit_turn_number=commit_turn_number,
            turn_kind=str(event.get("turn_kind") or "player_rejected_recoverable"),
        )
    interpreted_input = (
        event.get("interpreted_input")
        if isinstance(event.get("interpreted_input"), dict)
        else graph_state.get("interpreted_input")
        if isinstance(graph_state.get("interpreted_input"), dict)
        else {}
    )
    selected_responder_set = (
        event.get("selected_responder_set")
        if isinstance(event.get("selected_responder_set"), list)
        else graph_state.get("selected_responder_set")
        if isinstance(graph_state.get("selected_responder_set"), list)
        else []
    )
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
    return interpreted_input, selected_responder_set, human_att


def copy_player_visible_defaults_to_graph_state(
    *,
    graph_state: dict[str, Any],
    event: dict[str, Any],
    interpreted_input: dict[str, Any],
) -> None:
    graph_state.setdefault("turn_aspect_ledger", event.get("turn_aspect_ledger"))
    graph_state.setdefault("validation_outcome", event.get("validation_outcome"))
    graph_state.setdefault("visible_output_bundle", event.get("visible_output_bundle"))
    graph_state.setdefault("interpreted_input", interpreted_input)
    if isinstance(event.get("no_dead_end_recovery"), dict):
        graph_state["no_dead_end_recovery"] = event["no_dead_end_recovery"]


__all__ = [
    "copy_player_visible_defaults_to_graph_state",
    "prepare_player_visible_event",
]
