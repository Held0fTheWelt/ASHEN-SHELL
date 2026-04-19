import pytest

from app.runtime.engine import RuntimeEngine
from app.runtime.manager import RuntimeManager


def test_public_open_world_bootstraps(tmp_path):
    manager = RuntimeManager(store_root=tmp_path)
    runs = manager.list_runs()
    assert any(run.template_id == "better_tomorrow_district_alpha" for run in runs)


def test_create_solo_run_and_snapshot(tmp_path):
    manager = RuntimeManager(store_root=tmp_path)
    run = manager.create_run("god_of_carnage_solo", account_id="acct:hollywood", display_name="Hollywood")
    human = next(participant for participant in run.participants.values() if participant.seat_owner_account_id == "acct:hollywood")

    snapshot = manager.build_snapshot(run.id, human.id)
    assert snapshot.template_id == "god_of_carnage_solo"
    assert snapshot.viewer_display_name == "Hollywood"
    assert snapshot.viewer_room_id == "hallway"
    assert snapshot.viewer_account_id == "acct:hollywood"
    assert snapshot.current_room["id"] == "hallway"
    assert any(action["id"] == "steady_breath" for action in snapshot.available_actions)


def test_group_run_accepts_second_human(tmp_path):
    manager = RuntimeManager(store_root=tmp_path)
    run = manager.create_run("apartment_confrontation_group", account_id="acct:host", display_name="Host")
    second = manager.find_or_join_run(run.id, account_id="acct:guest", display_name="Guest", preferred_role_id="parent_a")
    assert second.role_id == "parent_a"


def test_snapshot_hides_other_rooms_and_remote_transcript(tmp_path):
    manager = RuntimeManager(store_root=tmp_path)
    run = manager.create_run("apartment_confrontation_group", account_id="acct:host", display_name="Host")
    second = manager.find_or_join_run(run.id, account_id="acct:guest", display_name="Guest", preferred_role_id="parent_a")

    engine = RuntimeEngine(manager.get_template(run.template_id))
    result = engine.apply_command(run, second.id, {"action": "say", "text": "We should proceed carefully."})
    assert result.accepted

    host = next(participant for participant in run.participants.values() if participant.account_id == "acct:host")
    snapshot = manager.build_snapshot(run.id, host.id)

    assert snapshot.current_room["id"] == "foyer"
    assert snapshot.visible_occupants == [
        {
            "participant_id": host.id,
            "display_name": "Host",
            "role_id": host.role_id,
            "mode": "human",
            "connected": False,
            "is_self": True,
        }
    ]
    assert all(entry.room_id in {None, host.current_room_id} or entry.payload.get("participant_id") == host.id for entry in snapshot.transcript_tail)


def test_identity_rejoin_uses_account_id_not_display_name(tmp_path):
    manager = RuntimeManager(store_root=tmp_path)
    run = manager.create_run("apartment_confrontation_group", account_id="acct:dup-a", display_name="Alex")
    second = manager.find_or_join_run(run.id, account_id="acct:dup-b", display_name="Alex", preferred_role_id="parent_a")
    rejoined = manager.find_or_join_run(run.id, account_id="acct:dup-b", display_name="Someone Else")

    assert second.id == rejoined.id
    assert len([participant for participant in run.participants.values() if participant.mode.value == "human"]) == 2


def test_inspect_rejects_remote_room_targets(tmp_path):
    manager = RuntimeManager(store_root=tmp_path)
    run = manager.create_run("god_of_carnage_solo", account_id="acct:hollywood", display_name="Hollywood")
    human = next(participant for participant in run.participants.values() if participant.account_id == "acct:hollywood")
    result = manager.engines[run.id].apply_command(run, human.id, {"action": "inspect", "target_id": "living_room"})
    assert not result.accepted
    assert result.reason == "That target is not visible from your current room."


def test_remote_templates_override_and_load(tmp_path, monkeypatch):
    import importlib
    from app.content.models import ExperienceKind, ExperienceTemplate, JoinPolicy, RoleTemplate, RoomTemplate, BeatTemplate, ParticipantMode

    # Set environment variables to enable backend content sync
    monkeypatch.setenv('BACKEND_CONTENT_SYNC_ENABLED', 'true')
    monkeypatch.setenv('BACKEND_CONTENT_FEED_URL', 'https://content.example.com/api/v1/game-content/templates')
    monkeypatch.setenv('BACKEND_CONTENT_SYNC_INTERVAL_SECONDS', '0.0')

    # Reload config to pick up environment variables
    import app.config
    importlib.reload(app.config)

    remote_template = ExperienceTemplate(
        id="god_of_carnage_solo",
        title="Remote Override",
        kind=ExperienceKind.SOLO_STORY,
        join_policy=JoinPolicy.OWNER_ONLY,
        summary="Remote template wins over builtin when ids match.",
        max_humans=1,
        initial_beat_id="intro",
        roles=[RoleTemplate(id="visitor", display_name="Visitor", description="desc", mode=ParticipantMode.HUMAN, initial_room_id="hallway", can_join=True)],
        rooms=[RoomTemplate(id="hallway", name="Hallway", description="desc")],
        props=[],
        actions=[],
        beats=[BeatTemplate(id="intro", name="Intro", description="desc", summary="sum")],
    )

    # Patch load_published_templates in backend_loader
    backend_loader = importlib.import_module('app.content.backend_loader')
    monkeypatch.setattr(backend_loader, 'load_published_templates', lambda url, timeout=10: {remote_template.id: remote_template})

    # Reload runtime manager to pick up reloaded config
    import app.runtime.manager
    importlib.reload(app.runtime.manager)

    # Now create manager - it will pick up the reloaded config and patched function
    from app.runtime.manager import RuntimeManager
    manager = RuntimeManager(store_root=tmp_path)
    assert manager.get_template('god_of_carnage_solo').title == 'Remote Override'


# --- broadcast, join metadata, backend template sync ---


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
    from datetime import timedelta

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
    from app.content.backend_loader import BackendContentLoadError

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


def test_sync_templates_reverts_catalog_to_builtin_and_preserves_existing_run_activation(tmp_path, monkeypatch):
    import app.runtime.manager as manager_module
    from app.content.models import ExperienceKind, ExperienceTemplate, JoinPolicy, RoleTemplate, RoomTemplate, BeatTemplate, ParticipantMode

    state = {"published": True}

    remote_template = ExperienceTemplate(
        id="god_of_carnage_solo",
        title="God of Carnage - Published Override",
        kind=ExperienceKind.SOLO_STORY,
        join_policy=JoinPolicy.OWNER_ONLY,
        summary="Published authored payload from backend feed.",
        max_humans=1,
        initial_beat_id="intro",
        roles=[RoleTemplate(id="visitor", display_name="Visitor", description="desc", mode=ParticipantMode.HUMAN, initial_room_id="hallway", can_join=True)],
        rooms=[RoomTemplate(id="hallway", name="Hallway", description="desc")],
        props=[],
        actions=[],
        beats=[BeatTemplate(id="intro", name="Intro", description="desc", summary="sum")],
    )

    def fake_loader(url: str, timeout: float = 10.0):
        return {remote_template.id: remote_template} if state["published"] else {}

    monkeypatch.setattr(manager_module, "BACKEND_CONTENT_SYNC_ENABLED", True, raising=False)
    monkeypatch.setattr(manager_module, "BACKEND_CONTENT_FEED_URL", "https://content.example/templates", raising=False)
    monkeypatch.setattr(manager_module, "BACKEND_CONTENT_TIMEOUT_SECONDS", 3.5, raising=False)
    monkeypatch.setattr(manager_module, "BACKEND_CONTENT_SYNC_INTERVAL_SECONDS", 0.0, raising=False)
    monkeypatch.setattr(manager_module, "load_published_templates", fake_loader)

    manager = manager_module.RuntimeManager(store_root=tmp_path)
    existing_run = manager.create_run("god_of_carnage_solo", account_id="acct:published", display_name="Published User")
    published_details = manager.get_run_details(existing_run.id)

    assert manager.get_template("god_of_carnage_solo").title == "God of Carnage - Published Override"
    assert published_details["template_source"] == "backend_published"
    assert published_details["template"]["title"] == "God of Carnage - Published Override"

    state["published"] = False
    manager.sync_templates(force=True)

    assert manager.get_template("god_of_carnage_solo").title == manager.builtin_templates["god_of_carnage_solo"].title

    existing_details_after_unpublish = manager.get_run_details(existing_run.id)
    assert existing_details_after_unpublish["template_source"] == "backend_published"
    assert existing_details_after_unpublish["template"]["title"] == "God of Carnage - Published Override"

    fallback_run = manager.create_run("god_of_carnage_solo", account_id="acct:builtin", display_name="Builtin User")
    fallback_details = manager.get_run_details(fallback_run.id)
    assert fallback_details["template_source"] == "builtin"
    assert fallback_details["template"]["title"] == manager.builtin_templates["god_of_carnage_solo"].title
