"""Shared serialization helpers for story-runtime-core diagnostic payloads."""

from __future__ import annotations

from typing import Any


def json_safe(value: Any) -> Any:
    """Return deterministic JSON-compatible runtime evidence."""
    if isinstance(value, dict):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(item) for item in value]
    if isinstance(value, set):
        return sorted(json_safe(item) for item in value)
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def as_list(value: Any) -> list[Any]:
    """Return list-like input as a list; wrap scalar values for policy fields."""
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    if value is None:
        return []
    return [value]


def sequence_list(value: Any) -> list[Any]:
    """Return only list/tuple input as a list; ignore scalar values."""
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    return []
