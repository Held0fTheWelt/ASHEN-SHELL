"""Real RuntimeManager / RuntimeEngine coverage (JsonRunStore, lobby, commands)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.content.builtins import load_builtin_templates
from app.content.models import ExperienceKind, ParticipantMode
from app.runtime.engine import RuntimeEngine
from app.runtime.manager import RuntimeManager
from app.runtime.models import LobbySeatState, ParticipantState, PropState, RunStatus, RuntimeInstance
from app.runtime.store import JsonRunStore


def _solo_instance(template_id: str = "god_of_carnage_solo") -> RuntimeInstance:
    template = load_builtin_templates()[template_id]
    humans = [r for r in template.roles if r.mode == ParticipantMode.HUMAN]
    human_role = humans[0]
    inst = RuntimeInstance(
        id=f"run-{template_id}",
        template_id=template.id,
        template_title=template.title,
        kind=template.kind,
        join_policy=template.join_policy,
        beat_id=template.initial_beat_id,
        status=RunStatus.RUNNING,
        persistent=template.persistent,
        owner_player_name="Owner",
        owner_account_id="owner-1",
    )
    p = ParticipantState(
        id="human-1",
        display_name="Owner",
        role_id=human_role.id,
        mode=ParticipantMode.HUMAN,
        current_room_id=human_role.initial_room_id,
        account_id="owner-1",
        character_id="char-1",
    )
    inst.participants[p.id] = p
    for prop in template.props:
        room_id = next(room.id for room in template.rooms if prop.id in room.prop_ids)
        inst.props[prop.id] = PropState(
            id=prop.id,
            name=prop.name,
            room_id=room_id,
            description=prop.description,
            state=prop.initial_state,
        )
    return inst


def test_manager_skips_persisted_run_with_unknown_template(tmp_path: Path):
    solo = _solo_instance()
    data = json.loads(solo.model_dump_json())
    data["template_id"] = "unknown_template_xyz"
    data["id"] = "orphan-run"
    (tmp_path / "orphan-run.json").write_text(json.dumps(data), encoding="utf-8")

    mgr = RuntimeManager(tmp_path)
    assert "orphan-run" not in mgr.instances


def test_manager_ensures_public_persistent_open_world(tmp_path: Path):
    mgr = RuntimeManager(tmp_path)
    public_ids = [rid for rid in mgr.instances if rid.startswith("public-")]
    assert public_ids
    assert any("better_tomorrow" in rid for rid in public_ids)


def test_manager_normalize_instance_restores_lobby_seats(tmp_path: Path):
    template = load_builtin_templates()["apartment_confrontation_group"]
    raw = _solo_instance("apartment_confrontation_group")
    raw.status = RunStatus.LOBBY
    raw.lobby_seats = {}
    JsonRunStore(tmp_path).save(raw)

    mgr = RuntimeManager(tmp_path)
    loaded = mgr.instances[raw.id]
    assert loaded.lobby_seats
    human_seat_ids = {r.id for r in template.roles if r.mode == ParticipantMode.HUMAN and r.can_join}
    assert human_seat_ids.issubset(set(loaded.lobby_seats.keys()))


def test_manager_find_or_join_returns_existing_participant(tmp_path: Path):
    mgr = RuntimeManager(tmp_path)
    run = mgr.create_run("god_of_carnage_solo", "Alice", account_id="acc-1", character_id="c1")
    rid = run.id
    p1 = mgr.find_or_join_run(rid, "Alice Renamed", account_id="acc-1", character_id="c1")
    p2 = mgr.find_or_join_run(rid, "Alice Renamed", account_id="acc-1", character_id="c1")
    assert p1.id == p2.id


def test_engine_group_lobby_payload_and_move_blocked_in_lobby():
    template = load_builtin_templates()["apartment_confrontation_group"]
    engine = RuntimeEngine(template)
    inst = _solo_instance("apartment_confrontation_group")
    inst.status = RunStatus.LOBBY
    human = next(p for p in inst.participants.values() if p.mode == ParticipantMode.HUMAN)
    lobby = engine.build_lobby_payload(inst)
    assert lobby is not None
    assert "seats" in lobby

    res = engine.apply_command(inst, human.id, {"action": "move", "target_room_id": "parlor"})
    assert res.accepted is False
    assert "lobby" in (res.reason or "").lower()


def test_engine_solo_say_emote_and_unknown_command():
    template = load_builtin_templates()["god_of_carnage_solo"]
    engine = RuntimeEngine(template)
    inst = _solo_instance()
    human = next(p for p in inst.participants.values() if p.mode == ParticipantMode.HUMAN)

    bad_say = engine.apply_command(inst, human.id, {"action": "say", "text": ""})
    assert bad_say.accepted is False

    bad_emote = engine.apply_command(inst, human.id, {"action": "emote", "text": "  "})
    assert bad_emote.accepted is False

    ok_say = engine.apply_command(inst, human.id, {"action": "say", "text": "hello"})
    assert ok_say.accepted is True

    unknown = engine.apply_command(inst, human.id, {"action": "nope", "x": 1})
    assert unknown.accepted is False
    assert "Unknown" in (unknown.reason or "")


def test_engine_move_invalid_exit():
    template = load_builtin_templates()["god_of_carnage_solo"]
    engine = RuntimeEngine(template)
    inst = _solo_instance()
    human = next(p for p in inst.participants.values() if p.mode == ParticipantMode.HUMAN)
    res = engine.apply_command(inst, human.id, {"action": "move", "target_room_id": "nowhere"})
    assert res.accepted is False


def test_engine_set_ready_rejected_for_solo():
    template = load_builtin_templates()["god_of_carnage_solo"]
    engine = RuntimeEngine(template)
    inst = _solo_instance()
    human = next(p for p in inst.participants.values() if p.mode == ParticipantMode.HUMAN)
    res = engine.apply_command(inst, human.id, {"action": "set_ready", "ready": True})
    assert res.accepted is False
