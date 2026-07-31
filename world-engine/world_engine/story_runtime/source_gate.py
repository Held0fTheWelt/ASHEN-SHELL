"""Source gate for proposed state mutations (Wave 4 / D26).

Rejects proposals from disallowed origins without applying deltas. Produces a
commit-shaped rejection so authority can record the attempt without advancing
revision when wired to PersistOutcome (see D18 / Wave 2).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable

from world_engine.story_runtime.state_deltas import GuardOutcome, StateDelta


ALLOWED_SOURCES = frozenset({"player", "ai", "script"})


@dataclass(slots=True)
class SourceGateDecision:
    allowed: bool
    reason_code: str
    reason_message: str
    rejected_deltas: list[StateDelta]


def evaluate_source_gate(
    deltas: Iterable[StateDelta],
    *,
    allowed_sources: frozenset[str] | None = None,
) -> SourceGateDecision:
    """Allow when every delta source is in the allow-set; else reject all."""
    allow = allowed_sources if allowed_sources is not None else ALLOWED_SOURCES
    rejected: list[StateDelta] = []
    for delta in deltas:
        src = str(delta.source or "").strip().lower()
        if src not in allow:
            rejected.append(delta)
    if rejected:
        return SourceGateDecision(
            allowed=False,
            reason_code="source_gate_rejected",
            reason_message="One or more deltas have a disallowed proposal source.",
            rejected_deltas=list(deltas) if isinstance(deltas, list) else list(deltas),
        )
    return SourceGateDecision(
        allowed=True,
        reason_code="source_gate_passed",
        reason_message="All delta sources are permitted.",
        rejected_deltas=[],
    )


def narrative_commit_for_source_gate_rejection(
    *,
    turn_number: int,
    prior_scene_id: str,
    rejected_deltas: list[StateDelta],
    reason_message: str | None = None,
) -> dict[str, Any]:
    """JSON-safe commit summary when the source gate rejects (no deltas applied)."""
    targets = sorted({d.target_path for d in rejected_deltas if d.target_path})
    return {
        "turn_number": turn_number,
        "prior_scene_id": prior_scene_id,
        "committed_scene_id": prior_scene_id,
        "situation_status": "continue",
        "allowed": False,
        "commit_reason_code": "source_gate_rejected",
        "authoritative_reason": reason_message
        or "Proposal source rejected by source gate; no state deltas applied.",
        "accepted_deltas": [],
        "rejected_deltas": [d.to_dict() for d in rejected_deltas],
        "rejected_delta_targets": targets,
        "guard_outcome": GuardOutcome.REJECTED.value,
        "committed_consequences": [
            f"scene_continue:{prior_scene_id}",
            "source_gate_rejected",
        ],
        "is_terminal": False,
        "degraded_mode": None,
    }
