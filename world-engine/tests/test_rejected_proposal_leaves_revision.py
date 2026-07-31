"""Wave 2 D18 characterization: do rejected/blocked turns bump session.revision?"""
from __future__ import annotations

from typing import Any

import pytest

from app.story_runtime import commit_models
from app.story_runtime.manager import StoryRuntimeManager
from app.story_runtime.persist_outcome import Persisted
from test_story_runtime_narrative_commit import _FakeTurnGraph, _envelope


class _MemorySessionStore:
    def __init__(self) -> None:
        self.payloads: dict[str, dict[str, Any]] = {}

    def save(self, session_id: str, payload: dict[str, Any]) -> None:
        self.payloads[session_id] = dict(payload)


def test_rejected_unknown_target_scene_revision_characterization(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Characterize D18: measure whether a blocked commit persists a new revision.

    Result is documented in DRIFT_SANIERUNG_FORTSCHRITT.md — Wave 3 uses this
    as the baseline for rejection/persist policy.
    """

    def _fake_resolve(**kwargs: Any) -> tuple[str | None, str | None, list[dict[str, Any]], str | None]:
        return (
            "scene_99",
            "player_input_token_scan",
            [{"source": "player_input_token_scan", "scene_id": "scene_99"}],
            None,
        )

    monkeypatch.setattr(commit_models, "_resolve_scene_proposal", _fake_resolve)
    manager = StoryRuntimeManager()
    manager._session_store = _MemorySessionStore()
    manager.turn_graph = _FakeTurnGraph(
        _envelope(
            interpreted_input={"kind": "speech", "confidence": 0.8},
            generation={"success": True, "metadata": {}},
        )
    )
    session = manager.create_session(
        module_id="m",
        runtime_projection={
            "start_scene_id": "scene_1",
            "scenes": [{"id": "scene_1"}, {"id": "scene_2"}],
            "transition_hints": [{"from": "scene_1", "to": "scene_2"}],
        },
    )
    revision_before = int(session.revision or 0)
    turn = manager.execute_turn(session_id=session.session_id, player_input="x")
    session_after = manager.get_session(session.session_id)
    revision_after = int(session_after.revision or 0)
    nc = turn["narrative_commit"]
    assert nc["commit_reason_code"] == "unknown_target_scene"
    assert nc["situation_status"] == "blocked"
    # Characterization: today finalize persists even for blocked situation_status (D18).
    assert revision_after == revision_before + 1, (
        f"D18 characterization changed: before={revision_before} after={revision_after}"
    )
    assert isinstance(
        manager._persist_session(session_after, reason="probe"),
        Persisted,
    )
