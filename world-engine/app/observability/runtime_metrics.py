"""Lightweight counters for story-runtime and config application (operator visibility)."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
from threading import Lock
from typing import Any


@dataclass
class StoryRuntimeMetrics:
    counters: Counter = field(default_factory=Counter)
    last_events: list[dict[str, Any]] = field(default_factory=list)
    _lock: Lock = field(default_factory=Lock)

    def incr(self, key: str, amount: int = 1, **event: Any) -> None:
        with self._lock:
            self.counters[key] += amount
            if event:
                event.setdefault("metric", key)
                event.setdefault("timestamp", datetime.now(timezone.utc).isoformat())
                self.last_events.append(event)
                self.last_events = self.last_events[-50:]

    def summary(self) -> dict[str, Any]:
        with self._lock:
            return {
                "counters": dict(self.counters),
                "recent_events": list(self.last_events),
            }
