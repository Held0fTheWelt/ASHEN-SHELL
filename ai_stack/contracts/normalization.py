"""Shared value normalization helpers for AI-stack contracts."""

from __future__ import annotations

from typing import Any

from ai_stack.contracts.serialization import as_list


def clean_text(value: Any) -> str:
    """Return a stripped string for scalar contract values."""
    return str(value or "").strip()


def clean_str_list(
    value: Any,
    *,
    allowed: frozenset[str] | None = None,
    lower: bool = False,
    allow_scalar: bool = True,
    include_sets: bool = False,
) -> list[str]:
    """Return unique non-empty strings from list-like contract input."""
    if isinstance(value, set):
        items = sorted(value) if include_sets else ([] if not allow_scalar else [value])
    elif allow_scalar:
        items = as_list(value)
    elif isinstance(value, (list, tuple)):
        items = list(value)
    else:
        items = []

    out: list[str] = []
    for item in items:
        text = clean_text(item)
        if lower:
            text = text.lower()
        if not text:
            continue
        if allowed is not None and text not in allowed:
            continue
        if text not in out:
            out.append(text)
    return out


def bounded_int(value: Any, default: int, *, minimum: int, maximum: int) -> int:
    """Coerce an integer and clamp it to the inclusive bounds."""
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        parsed = default
    return max(minimum, min(maximum, parsed))


__all__ = ["bounded_int", "clean_str_list", "clean_text"]
