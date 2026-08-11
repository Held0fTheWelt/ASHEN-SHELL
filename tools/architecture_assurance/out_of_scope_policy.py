"""Policy for architecture-assurance classification outside direct coverage.

Reasons must start with a known category so coverage cannot hide units behind
opaque free text. Categories are closed; detail text remains free-form.
"""

from __future__ import annotations

import re

OUT_OF_SCOPE_CATEGORIES: frozenset[str] = frozenset(
    {
        "generated",
        "vendored",
        "test-fixture",
        "archived",
        "unmapped",
        "violation",
    }
)

# Classification may temporarily cover an entire scan boundary. This ceiling is
# not a coverage claim: direct representation is reported independently.
OUT_OF_SCOPE_MAX_SHARE = 1.0

_REASON_RE = re.compile(
    r"^(?P<category>generated|vendored|test-fixture|archived|unmapped|violation):\s+(?P<detail>\S.*)$",
    re.DOTALL,
)


def parse_out_of_scope_reason(reason: str) -> tuple[str, str]:
    """Return ``(category, detail)`` or raise ``ValueError``."""
    text = (reason or "").strip()
    match = _REASON_RE.match(text)
    if match is None:
        raise ValueError(
            "out_of_scope reason must be '<category>: <detail>' with category in "
            + ", ".join(sorted(OUT_OF_SCOPE_CATEGORIES))
        )
    category = match.group("category")
    detail = match.group("detail").strip()
    if category not in OUT_OF_SCOPE_CATEGORIES or not detail:
        raise ValueError("invalid out_of_scope category or empty detail")
    return category, detail


def format_out_of_scope_reason(category: str, detail: str) -> str:
    if category not in OUT_OF_SCOPE_CATEGORIES:
        raise ValueError(f"unknown out_of_scope category: {category}")
    cleaned = (detail or "").strip()
    if not cleaned:
        raise ValueError("out_of_scope detail must be non-empty")
    return f"{category}: {cleaned}"


def out_of_scope_share(discovered_count: int, out_of_scope_count: int) -> float:
    if discovered_count <= 0:
        return 0.0
    return out_of_scope_count / discovered_count
