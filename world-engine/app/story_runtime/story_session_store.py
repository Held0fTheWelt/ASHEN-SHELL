"""Durable JSON persistence payloads for authored story sessions (audit F-H1).

Stores plain JSON dicts on disk (one file per session id). Serialization of
``StorySession`` lives in ``manager.py`` to avoid circular imports.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class JsonStorySessionStore:
    """Atomic JSON file per session id (same pattern as ``JsonRunStore``)."""

    backend_name = "json"

    def __init__(self, root: Path) -> None:
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)

    def path_for(self, session_id: str) -> Path:
        return self.root / f"{session_id}.json"

    def save(self, session_id: str, payload: dict[str, Any]) -> None:
        destination = self.path_for(session_id)
        temp_path = destination.with_suffix(".json.tmp")
        temp_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        temp_path.replace(destination)

    def load_all_raw(self) -> dict[str, dict[str, Any]]:
        """Load every ``*.json`` snapshot in root (skips corrupt files)."""
        out: dict[str, dict[str, Any]] = {}
        for path in sorted(self.root.glob("*.json")):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(data, dict) and isinstance(data.get("session_id"), str):
                    out[data["session_id"]] = data
            except Exception:
                continue
        return out

    def delete(self, session_id: str) -> None:
        path = self.path_for(session_id)
        if path.exists():
            path.unlink()

    def describe(self) -> dict[str, str]:
        return {"backend": self.backend_name, "root": str(self.root)}
