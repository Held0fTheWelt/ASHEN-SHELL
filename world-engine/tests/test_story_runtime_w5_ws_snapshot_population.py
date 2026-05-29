"""Phase 6B-11: populate W5 player view in RuntimeSnapshot WS payloads."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import pytest

from app.runtime.manager import RuntimeManager
from app.story_runtime.manager import StorySession


def _fact(
    fact_id: str,
    *,
    actor_id: str,
    dim: str,
    key: str,
    value: Any,
    source: str = "committed_action",
    truth: str = "observed",
    visibility: str = "public",
) -> dict[str, Any]:
    return {
        "schema_version": "w5_fact.v1",
        "fact_id": fact_id,
        "actor_id": actor_id,
        "dimension": dim,
        "key": key,
        "value": value,
        "source": source,
        "source_event_id": "ct_ws_011",
        "truth_level": truth,
        "confidence": 1.0,
        "valid_from_turn": 11,
        "valid_until_turn": None,
        "last_confirmed_turn": 11,
        "visibility": visibility,
        "actor_knowledge_scope": [],
        "status": "active",
        "superseded_by_fact_id": None,
        "contradicted_by_fact_id": None,
    }


def _w5_snapshot(*, malformed: bool = False) -> dict[str, Any]:
    if malformed:
        return {"schema_version": "w5_snapshot.v1", "actors": "not-a-map"}
    return {
        "schema_version": "w5_snapshot.v1",
        "snapshot_id": "w5s_ws_011",
        "story_session_id": "story-ws-1",
        "turn_number": 11,
        "actors": {
            "annette": {
                "actor_id": "annette",
                "actor_type": "human",
                "actor_role_in_scene": "player",
                "involvement_type": "primary",
                "where": [
                    _fact(
                        "w5f_where_annette",
                        actor_id="annette",
                        dim="where",
                        key="scene_location",
                        value="salon_w5",
                        source="participant_state_move",
                    )
                ],
                "what": [
                    _fact(
                        "w5f_what_annette",
                        actor_id="annette",
                        dim="what",
                        key="current_action",
                        value="listens",
                    )
                ],
                "how": [
                    _fact(
                        "w5f_how_annette",
                        actor_id="annette",
                        dim="how",
                        key="tone",
                        value="strained",
                    )
                ],
                "why": [
                    _fact(
                        "w5f_why_annette",
                        actor_id="annette",
                        dim="why",
                        key="motive",
                        value="keep_the_peace",
                        source="character_mind_record",
                        truth="inferred",
                        visibility="private_to_actor",
                    )
                ],
                "freshness_status": "fresh",
                "last_confirmed_turn": 11,
            },
            "michel": {
                "actor_id": "michel",
                "actor_type": "npc",
                "where": [
                    _fact(
                        "w5f_where_michel",
                        actor_id="michel",
                        dim="where",
                        key="scene_location",
                        value="salon_w5",
                    )
                ],
                "what": [],
                "how": [],
                "why": [
                    _fact(
                        "w5f_why_michel",
                        actor_id="michel",
                        dim="why",
                        key="private_motive",
                        value="conceal_the_guest_room_damage",
                        source="character_mind_record",
                        truth="inferred",
                        visibility="private_to_actor",
                    )
                ],
                "freshness_status": "fresh",
                "last_confirmed_turn": 11,
            },
        },
        "conflicts": [],
        "derived_from_event_ids": ["ct_ws_011"],
        "created_at": "w5:turn:11",
    }


def _story_session(
    *,
    run_id: str,
    w5_latest_snapshot: dict[str, Any] | None,
) -> StorySession:
    return StorySession(
        session_id="story-ws-1",
        module_id="god_of_carnage",
        runtime_projection={"human_actor_id": "annette", "selected_player_role": "annette"},
        created_at=datetime(2026, 5, 29, 12, 0, tzinfo=timezone.utc),
        updated_at=datetime(2026, 5, 29, 12, 1, tzinfo=timezone.utc),
        turn_counter=11,
        current_scene_id="opening",
        environment_state={"current_room_id": "hallway"},
        runtime_world={"current_room_id": "hallway"},
        content_provenance={"run_id": run_id},
        w5_latest_snapshot=w5_latest_snapshot,
    )


class _StoryManagerStub:
    def __init__(self, session: StorySession) -> None:
        self.sessions = {session.session_id: session}

    def get_session(self, session_id: str) -> StorySession:
        return self.sessions[session_id]


def _runtime_manager_with_run(tmp_path, *, w5_latest_snapshot: dict[str, Any] | None) -> tuple[RuntimeManager, str, str]:
    manager = RuntimeManager(store_root=tmp_path)
    instance = manager.create_run(
        "god_of_carnage_solo",
        display_name="Annette",
        account_id="acct-annette",
        preferred_role_id="annette",
    )
    session = _story_session(run_id=instance.id, w5_latest_snapshot=w5_latest_snapshot)
    manager.attach_story_manager(_StoryManagerStub(session))
    manager.bind_story_session(instance.id, session.session_id)
    participant = next(p for p in instance.participants.values() if p.role_id == "annette")
    return manager, instance.id, participant.id


def test_ws_runtime_snapshot_populates_w5_player_view_from_bound_story_session(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("W5_AST_FRONTEND_PLAYER_VIEW_ENABLED", raising=False)
    manager, run_id, participant_id = _runtime_manager_with_run(
        tmp_path,
        w5_latest_snapshot=_w5_snapshot(),
    )

    payload = manager.build_snapshot(run_id, participant_id).model_dump(mode="json")

    assert payload["feature_flags"]["W5_AST_FRONTEND_PLAYER_VIEW_ENABLED"] is True
    assert payload["viewer_room_id"] == "hallway"
    assert payload["current_room"]["id"] == "hallway"
    view = payload["w5_player_view"]
    assert view["target_consumer"] == "player_shell"
    assert view["actor_id"] == "annette"
    assert view["where_summary"]["current_visible_location"] == "salon_w5"
    assert view["how_summary"]["facts"]["tone"] == "strained"
    assert view["truth_attribution"]["why_summary.facts.motive"] == "inferred"
    assert "private_motive" not in view.get("why_summary", {}).get("facts", {})
    assert "w5_history" not in payload
    assert "w5_latest_snapshot" not in payload

    diagnostics = payload["metadata"]["w5_player_view_diagnostics"]
    assert diagnostics["w5_player_view_used"] is True
    assert diagnostics["ws_w5_player_view_source"] == "w5_projection"
    assert diagnostics["current_room_source"] == "w5_player_view"
    assert diagnostics["current_room_legacy_value"] == "hallway"
    assert diagnostics["current_room_w5_value"] == "salon_w5"
    assert diagnostics["current_room_mismatch"] is True
    assert diagnostics["ws_current_room_aliases_deprecated"] is True


def test_ws_runtime_snapshot_falls_back_when_w5_snapshot_missing(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("W5_AST_FRONTEND_PLAYER_VIEW_ENABLED", raising=False)
    manager, run_id, participant_id = _runtime_manager_with_run(
        tmp_path,
        w5_latest_snapshot=None,
    )

    payload = manager.build_snapshot(run_id, participant_id).model_dump(mode="json")

    assert payload["w5_player_view"] is None
    assert payload["viewer_room_id"] == "hallway"
    assert payload["current_room"]["id"] == "hallway"
    diagnostics = payload["metadata"]["w5_player_view_diagnostics"]
    assert diagnostics["w5_player_view_used"] is False
    assert diagnostics["ws_w5_player_view_source"] == "missing_w5"
    assert diagnostics["w5_player_view_fallback_reason"] == "missing_w5_latest_snapshot"
    assert diagnostics["current_room_source"] == "fallback_current_room"


def test_ws_runtime_snapshot_falls_back_when_w5_snapshot_malformed(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("W5_AST_FRONTEND_PLAYER_VIEW_ENABLED", raising=False)
    manager, run_id, participant_id = _runtime_manager_with_run(
        tmp_path,
        w5_latest_snapshot=_w5_snapshot(malformed=True),
    )

    payload = manager.build_snapshot(run_id, participant_id).model_dump(mode="json")

    assert payload["w5_player_view"] is None
    diagnostics = payload["metadata"]["w5_player_view_diagnostics"]
    assert diagnostics["w5_player_view_used"] is False
    assert diagnostics["ws_w5_player_view_source"] == "malformed_w5"
    assert diagnostics["current_room_legacy_value"] == "hallway"


def test_ws_runtime_snapshot_can_resolve_story_session_by_run_provenance_without_metadata_binding(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.delenv("W5_AST_FRONTEND_PLAYER_VIEW_ENABLED", raising=False)
    manager = RuntimeManager(store_root=tmp_path)
    instance = manager.create_run(
        "god_of_carnage_solo",
        display_name="Annette",
        account_id="acct-annette",
        preferred_role_id="annette",
    )
    session = _story_session(run_id=instance.id, w5_latest_snapshot=_w5_snapshot())
    manager.attach_story_manager(_StoryManagerStub(session))
    participant = next(p for p in instance.participants.values() if p.role_id == "annette")

    payload = manager.build_snapshot(instance.id, participant.id).model_dump(mode="json")

    assert payload["w5_player_view"]["where_summary"]["current_visible_location"] == "salon_w5"
    assert "world_engine_story_session_id" not in instance.metadata
