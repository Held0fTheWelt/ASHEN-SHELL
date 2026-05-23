"""Condition matching helpers for narrative governance notification rules."""

from __future__ import annotations

from typing import Any


def _matches_operator(actual: Any, operator: str, expected: Any) -> bool:
    if operator == "$gte":
        return isinstance(actual, (int, float)) and actual >= expected
    if operator == "$lte":
        return isinstance(actual, (int, float)) and actual <= expected
    if operator == "$eq":
        return actual == expected
    if operator == "$in":
        return isinstance(expected, list) and actual in expected
    return False


def is_condition_match(condition: dict[str, object], payload: dict[str, object]) -> bool:
    """Evaluate basic JSON-rule condition operators for notification rules."""
    if not condition:
        return True
    for key, expected in condition.items():
        actual = payload.get(key)
        if isinstance(expected, dict):
            if not all(_matches_operator(actual, str(operator), value) for operator, value in expected.items()):
                return False
        elif actual != expected:
            return False
    return True
