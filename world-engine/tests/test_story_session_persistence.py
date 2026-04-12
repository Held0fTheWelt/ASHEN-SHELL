"""Story session JSON durability (audit F-H1)."""

from __future__ import annotations

from typing import Any

import pytest

from app.story_runtime import StoryRuntimeManager
from app.story_runtime.story_session_store import JsonStorySessionStore


class _FakeTurnGraph:
    def __init__(self, payload: dict[str, Any]) -> None:
        self._payload = payload

    def run(self, **kwargs: Any) -> dict[str, Any]:
        return self._payload


def _envelope(*, interpreted_input: dict[str, Any], generation: dict[str, Any]) -> dict[str, Any]:
    return {
        "interpreted_input": interpreted_input,
        "generation": generation,
        "graph_diagnostics": {"errors": []},
        "retrieval": {"domain": "runtime", "status": "ok"},
        "routing": {"selected_model": "mock"},
    }


def test_story_session_restored_after_new_manager_process(tmp_path) -> None:
    store = JsonStorySessionStore(tmp_path / "story_sessions")
    mgr_a = StoryRuntimeManager(session_store=store)
    mgr_a.turn_graph = _FakeTurnGraph(
        _envelope(
            interpreted_input={"kind": "speech", "confidence": 0.8},
            generation={"success": True, "metadata": {}},
        )
    )
    session = mgr_a.create_session(
        module_id="m",
        runtime_projection={"start_scene_id": "scene_1", "scenes": [{"id": "scene_1"}]},
        content_provenance={"published_revision": "rev-1"},
    )
    sid = session.session_id
    mgr_a.execute_turn(session_id=sid, player_input="hello")
    assert mgr_a.get_session(sid).turn_counter == 1

    mgr_b = StoryRuntimeManager(session_store=store)
    mgr_b.turn_graph = _FakeTurnGraph(
        _envelope(
            interpreted_input={"kind": "speech", "confidence": 0.8},
            generation={"success": True, "metadata": {}},
        )
    )
    restored = mgr_b.get_session(sid)
    assert restored.turn_counter == 1
    assert restored.content_provenance.get("published_revision") == "rev-1"
    assert restored.history
