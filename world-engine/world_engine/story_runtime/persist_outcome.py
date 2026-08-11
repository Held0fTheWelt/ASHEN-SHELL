"""Explicit outcomes for live story-session persistence (Wave 2)."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal


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


def persist_outcome_payload(outcome: PersistOutcome) -> dict[str, Any]:
    """Return the stable caller-facing representation of a persistence result."""

    payload: dict[str, Any] = {
        "schema_version": "story_persist_outcome.v1",
        "kind": persist_outcome_kind(outcome),
        "reason": outcome.reason,
    }
    if isinstance(outcome, Persisted):
        payload["revision"] = outcome.revision
    return payload


__all__ = [
    "NoStoreConfigured",
    "PersistKind",
    "PersistOutcome",
    "Persisted",
    "SkippedSimulation",
    "persist_outcome_kind",
    "persist_outcome_payload",
]
