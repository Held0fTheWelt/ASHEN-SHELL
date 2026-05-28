"""Shared helpers for bounded runtime evidence projections."""

from __future__ import annotations

import hashlib
import json
from typing import Any

from story_runtime_core.serialization import json_safe

DEFAULT_EVIDENCE_HASH_LENGTH = 16
DEFAULT_EVIDENCE_TEXT_LIMIT = 96


def stable_evidence_hash(payload: Any, length: int = DEFAULT_EVIDENCE_HASH_LENGTH) -> str:
    """Return a stable hash for JSON-safe evidence payloads."""
    raw = json.dumps(json_safe(payload), sort_keys=True, default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:length]


def dedupe_sorted_evidence_text(values: list[Any], *, limit: int | None = None) -> list[str]:
    """Return sorted, unique, non-empty text values with an optional bound."""
    seen: set[str] = set()
    out: list[str] = []
    for value in values:
        text = str(value or "").strip()
        if not text or text in seen:
            continue
        seen.add(text)
        out.append(text)
    out.sort()
    return out[:limit] if limit is not None else out


def compact_evidence_text(value: Any, limit: int = DEFAULT_EVIDENCE_TEXT_LIMIT) -> str:
    """Trim evidence text while preserving a visible ellipsis marker."""
    text = str(value or "").strip()
    if len(text) <= limit:
        return text
    return text[: limit - 1] + "..."


__all__ = ["compact_evidence_text", "dedupe_sorted_evidence_text", "stable_evidence_hash"]
