"""Preview session isolation registry for narrative governance."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4


@dataclass(slots=True)
class PreviewSession:
    """Isolated preview execution session."""

    preview_session_id: str
    module_id: str
    preview_id: str
    namespace: str


class PreviewIsolationRegistry:
    """In-memory preview session registry enforcing isolation invariants."""

    def __init__(self) -> None:
        self._loaded_previews: dict[str, str] = {}
        self._sessions: dict[str, PreviewSession] = {}

    def load_preview(self, *, module_id: str, preview_id: str) -> None:
        key = f"{module_id}:{preview_id}"
        if key in self._loaded_previews:
            raise ValueError("preview_already_loaded")
        self._loaded_previews[key] = "loaded"

    def unload_preview(self, *, module_id: str, preview_id: str) -> None:
        key = f"{module_id}:{preview_id}"
        if key not in self._loaded_previews:
            raise KeyError("preview_not_loaded")
        self._loaded_previews.pop(key, None)
        for session_id, session in list(self._sessions.items()):
            if session.module_id == module_id and session.preview_id == preview_id:
                self._sessions.pop(session_id, None)

    def start_session(self, *, module_id: str, preview_id: str, session_seed: str) -> PreviewSession:
        key = f"{module_id}:{preview_id}"
        if key not in self._loaded_previews:
            raise KeyError("preview_not_loaded")
        namespace = f"preview:{module_id}:{preview_id}:{session_seed}"
        if any(item.namespace == namespace for item in self._sessions.values()):
            raise ValueError("preview_session_collision")
        session = PreviewSession(
            preview_session_id=f"prev_sess_{uuid4().hex[:10]}",
            module_id=module_id,
            preview_id=preview_id,
            namespace=namespace,
        )
        self._sessions[session.preview_session_id] = session
        return session

    def end_session(self, preview_session_id: str) -> None:
        if preview_session_id not in self._sessions:
            raise KeyError("preview_session_not_found")
        self._sessions.pop(preview_session_id, None)

    def describe(self) -> dict[str, object]:
        """Return operator-visible preview isolation state."""
        return {
            "loaded_previews": sorted(self._loaded_previews.keys()),
            "preview_session_count": len(self._sessions),
            "preview_sessions": [
                {
                    "preview_session_id": item.preview_session_id,
                    "module_id": item.module_id,
                    "preview_id": item.preview_id,
                    "namespace": item.namespace,
                }
                for item in self._sessions.values()
            ],
        }
