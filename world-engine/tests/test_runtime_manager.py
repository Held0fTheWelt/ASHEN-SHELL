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
