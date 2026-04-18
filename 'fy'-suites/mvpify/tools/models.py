
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class MVPArtifact:
    path: str
    kind: str
    note: str = ''

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class SuiteSignal:
    name: str
    present: bool
    evidence: list[str] = field(default_factory=list)
    relevance: str = 'supporting'

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(slots=True)
class OrchestrationStep:
    phase: str
    suite: str
    objective: str
    why_now: str
    inputs: list[str] = field(default_factory=list)
    outputs: list[str] = field(default_factory=list)
    depends_on: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
