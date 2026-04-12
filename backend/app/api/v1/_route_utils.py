"""Shared API v1 route utilities — leaf module, no app.services imports."""
from __future__ import annotations

from typing import Optional


def _parse_int(value: Optional[str], default: int, min_val: Optional[int] = None, max_val: Optional[int] = None) -> int:
    """Parse an optional string query parameter as int with optional clamping."""
    if value is None:
        return default
    try:
        n = int(value)
        if min_val is not None and n < min_val:
            return default
        if max_val is not None and n > max_val:
            return max_val
        return n
    except (TypeError, ValueError):
        return default
