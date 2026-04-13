"""Domain error helpers for operational governance APIs."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class GovernanceError(Exception):
    """Typed domain error with explicit code/status/details."""

    code: str
    message: str
    status_code: int
    details: dict[str, Any]

    def __str__(self) -> str:  # pragma: no cover - trivial wrapper
        return f"{self.code}: {self.message}"


def governance_error(code: str, message: str, status_code: int, details: dict[str, Any] | None = None) -> GovernanceError:
    """Build a governance error with optional details."""
    return GovernanceError(code=code, message=message, status_code=status_code, details=details or {})
