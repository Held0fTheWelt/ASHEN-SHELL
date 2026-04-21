from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any
import json
from pathlib import Path

@dataclass(slots=True)
class IncidentRecord:
    incident_code: str
    severity: str
    message: str
    session_id: str | None = None
    details: dict[str, Any] = field(default_factory=dict)


def load_story_session_or_incident(path: Path) -> tuple[dict[str, Any] | None, IncidentRecord | None]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except FileNotFoundError:
        return None, IncidentRecord("SESSION_MISSING", "warning", "Story session file missing", details={"path": str(path)})
    except json.JSONDecodeError as exc:
        return None, IncidentRecord("SESSION_CORRUPT", "error", "Story session file is corrupt", details={"path": str(path), "error": str(exc)})
