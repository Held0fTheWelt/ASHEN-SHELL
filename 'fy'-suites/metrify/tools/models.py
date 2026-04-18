from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class UsageEvent:
    timestamp_utc: str
    suite: str
    run_id: str
    model: str
    service_tier: str = 'standard'
    input_tokens: int = 0
    cached_input_tokens: int = 0
    output_tokens: int = 0
    reasoning_tokens: int = 0
    cost_usd: float = 0.0
    technique_tags: list[str] = field(default_factory=list)
    utility_score: float | None = None
    resolved_findings: int = 0
    notes: str = ''
    source: str = 'manual'

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
