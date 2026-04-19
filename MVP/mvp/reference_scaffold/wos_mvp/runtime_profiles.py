from __future__ import annotations
from dataclasses import dataclass

@dataclass(slots=True)
class DecisionOutcome:
    code: str
    player_safe_status: str
    explicit: bool = True


def accept_strong() -> DecisionOutcome:
    return DecisionOutcome("ACCEPT_STRONG", "committed")


def accept_constrained() -> DecisionOutcome:
    return DecisionOutcome("ACCEPT_CONSTRAINED", "committed_constrained")


def accept_degraded_safe() -> DecisionOutcome:
    return DecisionOutcome("ACCEPT_DEGRADED_SAFE", "committed_degraded_safe")
