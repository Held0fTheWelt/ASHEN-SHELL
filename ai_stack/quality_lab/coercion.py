"""Shared coercion helpers for Quality Lab interpreters."""

from __future__ import annotations

from typing import Any


def as_list(value: Any) -> list[Any]:
    """Return list-like input as a list, sorting sets for stable output."""
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    if isinstance(value, set):
        return sorted(value)
    return [value]


__all__ = ["as_list"]
