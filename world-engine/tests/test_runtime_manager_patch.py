from __future__ import annotations

from datetime import timedelta

import pytest

from app.content.backend_loader import BackendContentLoadError
from app.runtime.manager import RuntimeManager


class BrokenWebSocket:
    def __init__(self):
        self.payloads = []

    async def send_json(self, payload):
        self.payloads.append(payload)
        raise RuntimeError("socket gone")


class HealthyWebSocket:
    def __init__(self):
        self.payloads = []

    async def send_json(self, payload):
        self.payloads.append(payload)


@pytest.mark.asyncio
async def test_broadcast_snapshot_removes_broken_connection_but_keeps_healthy_one(tmp_path):
    manager = RuntimeManager(store_root=tmp_path)
    run = manager.create_run("apartment_confrontation_group", account_id="acct:host", display_name="Host")
    guest = manager.find_or_join_run(
        run.id,
        account_id="acct:guest",
        display_name="Guest",
        preferred_role_id="parent_a",
    )

    host = next(participant for participant in run.participants.values() if participant.account_id == "acct:host")
    broken = BrokenWebSocket()
    healthy = HealthyWebSocket()
    manager.connections[run.id][host.id] = broken
    manager.connections[run.id][guest.id] = healthy

    await manager.broadcast_snapshot(run.id)

    assert host.id not in manager.connections[run.id]
    assert guest.id in manager.connections[run.id]
    assert healthy.payloads[-1]["type"] == "snapshot"


def test_find_or_join_run_updates_existing_display_name_and_seat_metadata(tmp_path):
    manager = RuntimeManager(store_root=tmp_path)
    run = manager.create_run("apartment_confrontation_group", account_id="acct:host", display_name="Host")

    original = manager.find_or_join_run(
        run.id,
        account_id="acct:guest",
        character_id="char:guest",
        display_name="Old Name",
        preferred_role_id="parent_a",
    )
    renamed = manager.find_or_join_run(
        run.id,
        account_id="acct:guest",
        character_id="char:guest",
        display_name="New Name",
    )

    seat = run.lobby_seats[original.role_id]

    assert renamed.id == original.id
    assert renamed.display_name == "New Name"
    assert seat.occupant_display_name == "New Name"
    assert seat.reserved_for_display_name == "New Name"


def test_sync_templates_respects_refresh_interval(tmp_path, monkeypatch):
    import app.runtime.manager as manager_module

    calls: list[tuple[str, float]] = []

    def fake_loader(url: str, timeout: float = 10.0):
        calls.append((url, timeout))
        return {}

    monkeypatch.setattr(manager_module, "BACKEND_CONTENT_SYNC_ENABLED", True, raising=False)
    monkeypatch.setattr(manager_module, "BACKEND_CONTENT_FEED_URL", "https://content.example/templates", raising=False)
    monkeypatch.setattr(manager_module, "BACKEND_CONTENT_TIMEOUT_SECONDS", 3.5, raising=False)
    monkeypatch.setattr(manager_module, "BACKEND_CONTENT_SYNC_INTERVAL_SECONDS", 3600.0, raising=False)
    monkeypatch.setattr(manager_module, "load_published_templates", fake_loader)

    manager = manager_module.RuntimeManager(store_root=tmp_path)
    assert calls == [("https://content.example/templates", 3.5)]

    manager.sync_templates()

    assert calls == [("https://content.example/templates", 3.5)]
    assert manager._last_backend_content_sync_at is not None
    assert manager.backend_content_sync_interval == timedelta(seconds=3600.0)


def test_sync_templates_failure_marks_attempt_but_keeps_builtin_template(tmp_path, monkeypatch):
    import app.runtime.manager as manager_module

    def failing_loader(url: str, timeout: float = 10.0):
        raise BackendContentLoadError("upstream offline")

    monkeypatch.setattr(manager_module, "BACKEND_CONTENT_SYNC_ENABLED", True, raising=False)
    monkeypatch.setattr(manager_module, "BACKEND_CONTENT_FEED_URL", "https://content.example/templates", raising=False)
    monkeypatch.setattr(manager_module, "BACKEND_CONTENT_SYNC_INTERVAL_SECONDS", 0.0, raising=False)
    monkeypatch.setattr(manager_module, "load_published_templates", failing_loader)

    manager = manager_module.RuntimeManager(store_root=tmp_path)

    assert manager._last_backend_content_sync_at is not None
    assert manager.get_template("god_of_carnage_solo").title != "upstream offline"
    assert manager.template_sources["god_of_carnage_solo"] == "builtin"
