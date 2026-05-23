"""Readout fragments for the session-state API."""
from __future__ import annotations

from collections.abc import Callable

from .._deps import *


def extract_last_committed_turn_surfaces(session: StorySession) -> dict[str, Any]:
    last_committed_turn = session.history[-1] if session.history else None
    surfaces: dict[str, Any] = {"last_committed_turn": last_committed_turn}
    if not isinstance(last_committed_turn, dict):
        return surfaces
    for source_key, target_key in (
        ("narrative_commit", "last_narrative_commit"),
        ("committed_turn_authority", "last_committed_turn_authority"),
        ("dramatic_context_summary", "last_dramatic_context_summary"),
        ("actor_turn_summary", "last_actor_turn_summary"),
    ):
        value = last_committed_turn.get(source_key)
        if isinstance(value, dict):
            surfaces[target_key] = value
    branching = last_committed_turn.get("branching_forecast")
    if not isinstance(branching, dict):
        ledger = last_committed_turn.get("turn_aspect_ledger")
        if isinstance(ledger, dict):
            branching = ledger.get("branching_forecast")
    if isinstance(branching, dict):
        surfaces["last_branching_forecast"] = branching
    return surfaces


def build_narrative_commit_summary(
    *,
    last_narrative_commit: dict[str, Any] | None,
    last_actor_turn_summary: dict[str, Any] | None,
) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    if not isinstance(last_narrative_commit, dict):
        return None, last_actor_turn_summary
    actor_summary = last_actor_turn_summary
    planner_truth = (
        last_narrative_commit.get("planner_truth")
        if isinstance(last_narrative_commit.get("planner_truth"), dict)
        else {}
    )
    if not actor_summary and planner_truth:
        actor_summary = {
            "contract": "actor_turn_summary.v1",
            "primary_responder_id": planner_truth.get("primary_responder_id")
            or planner_truth.get("responder_id"),
            "secondary_responder_ids": planner_truth.get("secondary_responder_ids") or [],
            "spoken_line_count": planner_truth.get("spoken_line_count") or 0,
            "action_line_count": planner_truth.get("action_line_count") or 0,
            "initiative_summary": planner_truth.get("initiative_summary") or {},
            "last_actor_outcome_summary": planner_truth.get("last_actor_outcome_summary"),
        }
    summary = {
        "situation_status": last_narrative_commit.get("situation_status"),
        "allowed": last_narrative_commit.get("allowed"),
        "commit_reason_code": last_narrative_commit.get("commit_reason_code"),
        "committed_scene_id": last_narrative_commit.get("committed_scene_id"),
        "proposed_scene_id": last_narrative_commit.get("proposed_scene_id"),
        "selected_candidate_source": last_narrative_commit.get("selected_candidate_source"),
        "is_terminal": last_narrative_commit.get("is_terminal"),
        "primary_responder_id": (actor_summary or {}).get("primary_responder_id"),
        "spoken_line_count": (actor_summary or {}).get("spoken_line_count") or 0,
        "action_line_count": (actor_summary or {}).get("action_line_count") or 0,
        "initiative_summary": (actor_summary or {}).get("initiative_summary") or {},
        "last_actor_outcome_summary": (actor_summary or {}).get("last_actor_outcome_summary"),
    }
    return summary, actor_summary


def extract_last_commit_lists(
    last_narrative_commit: dict[str, Any] | None,
) -> tuple[list[str], list[str]]:
    if not isinstance(last_narrative_commit, dict):
        return [], []
    consequences = last_narrative_commit.get("committed_consequences")
    pressures = last_narrative_commit.get("open_pressures")
    return (
        [str(x) for x in consequences] if isinstance(consequences, list) else [],
        [str(x) for x in pressures] if isinstance(pressures, list) else [],
    )


def build_canonical_turn_counts(history_rows: list[Any]) -> dict[str, Any]:
    latest_canonical_turn_id: str | None = None
    last_hist = history_rows[-1] if history_rows else None
    if isinstance(last_hist, dict):
        lid = str(last_hist.get("canonical_turn_id") or "").strip()
        latest_canonical_turn_id = lid or None
    committed_count = len(history_rows)
    return {
        "committed_canonical_turn_count": committed_count,
        "opening_committed": any(
            isinstance(h, dict) and str(h.get("turn_kind") or "") == "opening"
            for h in history_rows
        ),
        "player_committed_turns": sum(
            1
            for h in history_rows
            if isinstance(h, dict) and str(h.get("turn_kind") or "") != "opening"
        ),
        "total_canonical_turns": committed_count,
        "latest_canonical_turn_id": latest_canonical_turn_id,
    }


def copy_session_surface_snapshot(
    reader: Callable[..., dict[str, Any]],
    *,
    session_id: str,
) -> dict[str, Any] | None:
    try:
        surface = reader(session_id=session_id)
        snapshot = surface.get("snapshot") if isinstance(surface.get("snapshot"), dict) else {}
        return copy.deepcopy(snapshot)
    except Exception:
        return None


__all__ = [
    "build_canonical_turn_counts",
    "build_narrative_commit_summary",
    "copy_session_surface_snapshot",
    "extract_last_commit_lists",
    "extract_last_committed_turn_surfaces",
]
