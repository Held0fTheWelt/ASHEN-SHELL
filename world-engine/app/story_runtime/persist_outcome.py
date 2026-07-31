"""Explicit outcomes for live story-session persistence (Wave 2)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True, slots=True)
class Persisted:
    revision: int
    reason: str = "committed"


@dataclass(frozen=True, slots=True)
class SkippedSimulation:
    reason: str = "branching_simulation"


@dataclass(frozen=True, slots=True)
class NoStoreConfigured:
    reason: str = "session_store_missing"


PersistOutcome = Persisted | SkippedSimulation | NoStoreConfigured

PersistKind = Literal["persisted", "skipped_simulation", "no_store"]


def persist_outcome_kind(outcome: PersistOutcome) -> PersistKind:
    if isinstance(outcome, Persisted):
        return "persisted"
    if isinstance(outcome, SkippedSimulation):
        return "skipped_simulation"
    return "no_store"


__all__ = [
    "NoStoreConfigured",
    "PersistKind",
    "PersistOutcome",
    "Persisted",
    "SkippedSimulation",
    "persist_outcome_kind",
]
