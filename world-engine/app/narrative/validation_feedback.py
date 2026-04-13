"""Validation feedback contracts for corrective retry loops."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ValidationViolation(BaseModel):
    """Machine-usable validation violation record."""

    violation_type: str
    specific_issue: str
    rule_violated: str
    suggested_fix: str
    severity: str = "blocking"


class ValidationFeedback(BaseModel):
    """Actionable feedback passed into corrective retry calls."""

    passed: bool
    violations: list[ValidationViolation] = Field(default_factory=list)
    corrections_needed: list[str] = Field(default_factory=list)
    legal_alternatives: dict[str, list[str]] = Field(default_factory=dict)
