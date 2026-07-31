"""Runtime degradation counters and operator-facing summaries."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(slots=True)
class RuntimeHealthCounters:
    """Live quality counters for first-pass, retry, and fallback behavior."""

    total_turns: int = 0
    first_pass_successes: int = 0
    corrective_retry_uses: int = 0
    safe_fallback_uses: int = 0
    recent_events: list[dict[str, object]] = field(default_factory=list)

    def record_first_pass_success(self, module_id: str, scene_id: str) -> None:
        self.total_turns += 1
        self.first_pass_successes += 1
        self.recent_events.append(
            {"event_type": "first_pass_success", "module_id": module_id, "scene_id": scene_id}
        )

    def record_corrective_retry(self, module_id: str, scene_id: str) -> None:
        self.total_turns += 1
        self.corrective_retry_uses += 1
        self.recent_events.append(
            {"event_type": "corrective_retry_used", "module_id": module_id, "scene_id": scene_id}
        )

    def record_safe_fallback(self, module_id: str, scene_id: str) -> None:
        self.total_turns += 1
        self.safe_fallback_uses += 1
        self.recent_events.append(
            {"event_type": "safe_fallback_used", "module_id": module_id, "scene_id": scene_id}
        )

    def summary(self) -> dict[str, object]:
        """Return operator-visible health metrics."""
        if self.total_turns <= 0:
            return {
                "total_turns": 0,
                "first_pass_success_rate": 0.0,
                "corrective_retry_rate": 0.0,
                "safe_fallback_rate": 0.0,
                "events": [],
            }
        return {
            "total_turns": self.total_turns,
            "first_pass_success_rate": self.first_pass_successes / self.total_turns,
            "corrective_retry_rate": self.corrective_retry_uses / self.total_turns,
            "safe_fallback_rate": self.safe_fallback_uses / self.total_turns,
            "events": self.recent_events[-50:],
        }
