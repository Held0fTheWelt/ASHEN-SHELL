"""Wave 2: PersistOutcome and session.revision contract tests."""
from __future__ import annotations

from types import SimpleNamespace

from world_engine.story_runtime.persist_outcome import (
    NoStoreConfigured,
    Persisted,
    SkippedSimulation,
)
from world_engine.story_runtime.manager.session.session_payloads import (
    StorySession,
    story_session_to_payload,
)
from world_engine.story_runtime.manager.session.session_memory_policies import story_session_from_payload
from world_engine.story_runtime.manager.session.manager_init_and_persistence import (
    _ManagerInitAndPersistenceMixin,
)


class _Store:
    def __init__(self) -> None:
        self.saved: list[tuple[str, dict]] = []

    def save(self, session_id: str, payload: dict) -> None:
        self.saved.append((session_id, payload))


class _Host(_ManagerInitAndPersistenceMixin):
    def __init__(self) -> None:
        self._branching_simulation_session_ids = set()
        self._session_store = _Store()


def test_persist_session_returns_explicit_outcome() -> None:
    host = _Host()
    session = StorySession(session_id="s1", module_id="m", runtime_projection={})
    outcome = host._persist_session(session, reason="session_opened")
    assert isinstance(outcome, Persisted)
    assert outcome.revision == 1
    assert session.revision == 1
    assert host._session_store.saved

    host._branching_simulation_session_ids.add("sim")
    sim = StorySession(session_id="sim", module_id="m", runtime_projection={})
    assert isinstance(host._persist_session(sim), SkippedSimulation)

    host2 = _Host()
    host2._session_store = None
    bare = StorySession(session_id="s2", module_id="m", runtime_projection={})
    assert isinstance(host2._persist_session(bare), NoStoreConfigured)


def test_simulation_session_never_writes() -> None:
    host = _Host()
    host._branching_simulation_session_ids.add("sim")
    session = StorySession(session_id="sim", module_id="m", runtime_projection={})
    host._persist_session(session)
    assert host._session_store.saved == []
    assert session.revision == 0


def test_revision_round_trips_with_legacy_default_zero() -> None:
    session = StorySession(session_id="s1", module_id="m", runtime_projection={}, revision=3)
    payload = story_session_to_payload(session)
    assert payload["revision"] == 3
    legacy = dict(payload)
    legacy.pop("revision")
    restored = story_session_from_payload(legacy)
    assert restored.revision == 0
