from __future__ import annotations
from dataclasses import dataclass
from datetime import UTC, datetime
from math import exp

from .enums import ReviewStatus
from .records import MemoryEntry, QueryContext

@dataclass
class RelevanceScorer:
    now_provider: callable = lambda: datetime.now(UTC)

    def compute_relevance(self, entry: MemoryEntry, query_context: QueryContext) -> float:
        if entry.review_status == ReviewStatus.DEPRECATED:
            return 0.0
        status_score = 0.1 if entry.review_status == ReviewStatus.SUPERSEDED else 1.0
        age_hours = max((self.now_provider() - entry.last_accessed).total_seconds() / 3600.0, 0.0)
        recency = exp(-age_hours / 24.0)
        frequency = min(1.0, entry.access_count / 10.0)
        authority = entry.authority_level.value / 4.0
        task_overlap = len(entry.task_tags & query_context.task_tags)
        task_proximity = task_overlap / max(len(entry.task_tags), 1)
        conflict_safety = 1.0 - entry.conflict_risk
        final = (
            0.2 * recency
            + 0.15 * frequency
            + 0.25 * authority
            + 0.15 * status_score
            + 0.15 * task_proximity
            + 0.1 * conflict_safety
        )
        return round(final * entry.temporal_weight, 6)
