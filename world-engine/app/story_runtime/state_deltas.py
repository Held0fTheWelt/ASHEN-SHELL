"""State delta + guard model for story-runtime authority (Wave 4 / D26).

A turn may partially apply: some deltas accepted, some rejected. This is the
technical substrate for SituationStatus ``partial`` (Wave 3 / E9).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class GuardOutcome(str, Enum):
    """Classification of a turn's delta set after policy + gate evaluation."""

    ACCEPTED = "accepted"
    PARTIAL = "partial"
    REJECTED = "rejected"


@dataclass(slots=True)
class StateDelta:
    """One proposed mutation against session / story state."""

    target_path: str
    operation: str = "set"
    value: Any = None
    source: str = "ai"  # player | ai | script
    reason: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "target_path": self.target_path,
            "operation": self.operation,
            "value": self.value,
            "source": self.source,
            "reason": self.reason,
        }

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> StateDelta:
        return cls(
            target_path=str(raw.get("target_path") or raw.get("path") or "").strip(),
            operation=str(raw.get("operation") or "set").strip() or "set",
            value=raw.get("value"),
            source=str(raw.get("source") or "ai").strip() or "ai",
            reason=(str(raw["reason"]) if raw.get("reason") is not None else None),
        )


@dataclass(slots=True)
class DeltaPartition:
    """Accepted vs rejected deltas for one turn."""

    accepted: list[StateDelta] = field(default_factory=list)
    rejected: list[StateDelta] = field(default_factory=list)
    guard_outcome: GuardOutcome = GuardOutcome.ACCEPTED

    def to_dict(self) -> dict[str, Any]:
        return {
            "accepted_deltas": [d.to_dict() for d in self.accepted],
            "rejected_deltas": [d.to_dict() for d in self.rejected],
            "guard_outcome": self.guard_outcome.value,
        }


def partition_deltas(
    *,
    candidates: list[StateDelta],
    accept: list[bool],
) -> DeltaPartition:
    """Partition candidates by parallel accept flags; derive GuardOutcome."""
    if len(accept) != len(candidates):
        raise ValueError("accept flags must align with candidates")
    accepted: list[StateDelta] = []
    rejected: list[StateDelta] = []
    for delta, ok in zip(candidates, accept, strict=True):
        (accepted if ok else rejected).append(delta)
    if not rejected:
        outcome = GuardOutcome.ACCEPTED
    elif not accepted:
        outcome = GuardOutcome.REJECTED
    else:
        outcome = GuardOutcome.PARTIAL
    return DeltaPartition(accepted=accepted, rejected=rejected, guard_outcome=outcome)
