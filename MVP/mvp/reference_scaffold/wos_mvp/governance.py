from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
# UTC compatibility for Python 3.10
UTC = timezone.utc

@dataclass
class AuditEntry:
    timestamp: datetime
    layer: str
    action: str
    details: dict

@dataclass
class GovernanceEngine:
    audit_log: list[AuditEntry] = field(default_factory=list)

    def log(self, layer: str, action: str, **details) -> None:
        self.audit_log.append(AuditEntry(timestamp=datetime.now(UTC), layer=layer, action=action, details=details))

    def degraded_mode_allowed(self, task_profile: str, index_state: str) -> bool:
        if task_profile == "audit" and index_state in {"failed", "building"}:
            return False
        return True
