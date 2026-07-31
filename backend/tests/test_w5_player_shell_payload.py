"""Player-shell payload W5 view contract tests (Phase 5A/5B)."""

from __future__ import annotations

from pathlib import Path

from app.api.v1.game_routes import _player_shell_state_view


def test_shell_state_view_omits_w5_player_view_when_runtime_state_is_fallback_only() -> None:
    state = {
        "turn_counter": 3,
        "current_scene_id": "opening",
        "history_count": 1,
        "runtime_world": {"current_room_id": "fallback_salon"},
        "committed_state": {
            "environment_state": {"current_room_id": "fallback_salon"},
            "player_shell_context": {"status": "fallback"},
        },
    }
    shell = _player_shell_state_view(
        state=state,
        run_id="run-1",
        template_id="tpl-1",
        module_id="god_of_carnage",
        runtime_session_id="sess-1",
    )
    assert "w5_player_view" not in shell
    assert "w5_player_view_diagnostics" not in shell
    assert shell["environment_state"]["current_room_id"] == "fallback_salon"


def test_shell_state_view_includes_w5_player_view_and_current_room_source_when_enabled() -> None:
    state = {
        "turn_counter": 3,
        "current_scene_id": "opening",
        "history_count": 1,
        "runtime_world": {"current_room_id": "fallback_salon"},
        "feature_flags": {"W5_AST_FRONTEND_PLAYER_VIEW_ENABLED": True},
        "w5_player_view": {
            "target_consumer": "player_shell",
            "actor_id": "annette",
            "where_summary": {
                "current_visible_location": "salon_w5",
                "scene_location": {"value": "salon_w5"},
            },
            "how_summary": {"facts": {"tone": "strained"}},
            "what_summary": {"facts": {"current_action": "listens"}},
        },
        "w5_player_view_diagnostics": {
            "w5_player_view_used": True,
            "w5_player_view_source": "w5_projection",
            "current_room_source": "w5_player_view",
            "current_room_fallback_value": "fallback_salon",
            "current_room_w5_value": "salon_w5",
            "current_room_mismatch": True,
        },
        "committed_state": {
            "environment_state": {"current_room_id": "fallback_salon"},
            "player_shell_context": {"status": "w5"},
        },
    }
    shell = _player_shell_state_view(
        state=state,
        run_id="run-1",
        template_id="tpl-1",
        module_id="god_of_carnage",
        runtime_session_id="sess-1",
    )
    assert shell["w5_player_view"]["target_consumer"] == "player_shell"
    assert shell["w5_player_view"]["how_summary"]["facts"]["tone"] == "strained"
    assert "tone" not in shell["w5_player_view"]["what_summary"]["facts"]
    assert shell["current_room_id"] == "salon_w5"
    assert shell["current_room_source"] == "w5_player_view"
    assert shell["current_room_fallback_value"] == "fallback_salon"
    assert shell["current_room_w5_value"] == "salon_w5"
    assert shell["current_room_mismatch"] is True
    assert shell["feature_flags"]["W5_AST_FRONTEND_PLAYER_VIEW_ENABLED"] is True
    assert shell["deprecations"]["room_aliases"]["status"] == "deprecated_compatibility_aliases_active"
    assert shell["deprecations"]["room_aliases"]["replacement"] == "w5_player_view"
    assert shell["deprecations"]["room_aliases"]["aliases"] == [
        "viewer_room_id",
        "current_room",
        "current_room_id",
    ]
    assert shell["deprecated_alias_usage"] == {
        "room_aliases_emitted": True,
        "w5_player_view_present": True,
        "w5_player_view_authority": True,
        "aliases": ["viewer_room_id", "current_room", "current_room_id"],
        "phase": "6B-13",
        "removal_blocked_until": "client_readiness_evidence",
    }
    assert "w5_history" not in shell


def test_shell_state_view_falls_back_to_fallback_current_room_when_w5_unused() -> None:
    state = {
        "turn_counter": 3,
        "current_scene_id": "opening",
        "history_count": 1,
        "runtime_world": {"current_room_id": "fallback_salon"},
        "feature_flags": {"W5_AST_FRONTEND_PLAYER_VIEW_ENABLED": True},
        "w5_player_view": None,
        "w5_player_view_diagnostics": {
            "w5_player_view_used": False,
            "w5_player_view_source": "fallback",
            "w5_player_view_fallback_reason": "missing_w5_latest_snapshot",
            "current_room_source": "fallback_current_room",
            "current_room_fallback_value": "fallback_salon",
            "current_room_w5_value": None,
            "current_room_mismatch": False,
        },
        "committed_state": {
            "environment_state": {"current_room_id": "fallback_salon"},
            "player_shell_context": {"status": "fallback"},
        },
    }
    shell = _player_shell_state_view(
        state=state,
        run_id="run-1",
        template_id="tpl-1",
        module_id="god_of_carnage",
        runtime_session_id="sess-1",
    )
    assert "w5_player_view" not in shell
    assert shell["current_room_id"] == "fallback_salon"
    assert shell["current_room_source"] == "fallback_current_room"
    assert shell["w5_player_view_diagnostics"]["w5_player_view_fallback_reason"] == "missing_w5_latest_snapshot"
    assert shell["current_room_mismatch"] is False
    assert shell["deprecations"]["room_aliases"]["status"] == "deprecated_compatibility_aliases_active"
    assert shell["deprecated_alias_usage"]["room_aliases_emitted"] is True
    assert shell["deprecated_alias_usage"]["w5_player_view_present"] is False
    assert shell["deprecated_alias_usage"]["w5_player_view_authority"] is False
    assert shell["deprecated_alias_usage"]["phase"] == "6B-13"


def test_backend_static_current_room_helper_is_w5_first_with_fallback() -> None:
    source = (Path(__file__).resolve().parents[1] / "app/web/static/app.js").read_text(encoding="utf-8")
    assert "function currentRoomFromSnapshot(snapshot)" in source
    assert "if (w5FrontendPlayerViewEnabled(snapshot))" in source
    assert "const w5Room = roomFromW5PlayerView(snapshot);" in source
    assert "if (w5Room) return w5Room;" in source
    assert "const legacyRoom = snapshot.current_room || null;" in source
    assert "return legacyRoom;" in source
    assert "warnLegacyRoomAliasFallbackOnce(snapshot)" in source
    assert "function currentRoom() {\n  return currentRoomFromSnapshot(state.snapshot);\n}" in source
    assert "if (!where) return null;" in source
    assert "where.scene_location && where.scene_location.value" in source
    assert "why_summary" not in source


def test_live_ws_room_helper_is_w5_first_and_does_not_render_private_why() -> None:
    source = Path("frontend/static/play_live_ws.js").read_text(encoding="utf-8")
    assert "function roomFromSnapshot(snapshot)" in source
    assert "if (w5FrontendPlayerViewEnabled(snapshot))" in source
    assert "const roomId = w5PlayerViewLocation(snapshot);" in source
    assert "const legacyRoom = snapshot.current_room || null;" in source
    assert "return legacyRoom;" in source
    assert "warnLegacyRoomAliasFallbackOnce(snapshot)" in source
    assert "if (!where) return null;" in source
    assert "where.scene_location && where.scene_location.value" in source
    assert "why_summary" not in source


def test_frontend_room_alias_warning_is_fallback_only() -> None:
    source = Path("frontend/static/play_live_ws.js").read_text(encoding="utf-8")
    assert "function warnLegacyRoomAliasFallbackOnce(snapshot)" in source
    assert "if (roomId) {" in source
    assert "if (legacyRoom) warnLegacyRoomAliasFallbackOnce(snapshot);" in source
    assert source.index("if (roomId) {") < source.index("warnLegacyRoomAliasFallbackOnce(snapshot);")


def test_runtime_snapshot_viewer_room_id_has_compatibility_alias_comment() -> None:
    """Phase 6B-9: RuntimeSnapshot.viewer_room_id must be annotated as a compat alias."""
    src = (
        Path(__file__).resolve().parents[2]
        / "world-engine/world_engine/runtime/models.py"
    ).read_text(encoding="utf-8")
    assert "viewer_room_id" in src
    assert "compat alias" in src
    assert "ADR-0069" in src
    assert "w5_player_view" in src


def test_runtime_snapshot_current_room_has_compatibility_alias_comment() -> None:
    """Phase 6B-9: RuntimeSnapshot.current_room must be annotated as a compat alias."""
    src = (
        Path(__file__).resolve().parents[2]
        / "world-engine/world_engine/runtime/models.py"
    ).read_text(encoding="utf-8")
    assert "current_room" in src
    assert "compat alias" in src
    assert "ADR-0069" in src


def test_world_engine_static_currentroom_is_w5_first_with_fallback() -> None:
    """Phase 6B-9: world-engine standalone UI must follow the same W5-first pattern
    as backend/app/web/static/app.js and frontend/static/play_live_ws.js."""
    source = (
        Path(__file__).resolve().parents[2]
        / "world-engine/world_engine/web/static/app.js"
    ).read_text(encoding="utf-8")
    assert "function w5FrontendPlayerViewEnabled(snapshot)" in source, (
        "world-engine static app.js must declare w5FrontendPlayerViewEnabled()"
    )
    assert "function w5PlayerViewLocation(snapshot)" in source, (
        "world-engine static app.js must declare w5PlayerViewLocation()"
    )
    assert "function currentRoomFromSnapshot(snapshot)" in source, (
        "world-engine static app.js must declare currentRoomFromSnapshot()"
    )
    assert "if (w5FrontendPlayerViewEnabled(snapshot))" in source, (
        "currentRoomFromSnapshot must gate on the feature flag"
    )
    assert "const legacyRoom = snapshot.current_room || null;" in source, (
        "legacy fallback must remain present"
    )
    assert "return legacyRoom;" in source, (
        "legacy fallback must remain present"
    )
    assert "warnLegacyRoomAliasFallbackOnce(snapshot)" in source, (
        "legacy fallback must emit the one-time deprecation warning hook"
    )
    assert "if (!where) return null;" in source, (
        "w5PlayerViewLocation must guard against missing where_summary"
    )
    assert "where.scene_location && where.scene_location.value" in source, (
        "w5PlayerViewLocation must cascade through scene_location.value"
    )
    assert "why_summary" not in source, (
        "world-engine static UI must not render why_summary"
    )


def test_ws_runtime_snapshot_carries_w5_player_view_when_enabled() -> None:
    """Phase 6B-10: RuntimeSnapshot carries w5_player_view and feature_flags and
    model_dump (the WS serialization path) exposes them to connected clients.
    """
    from world_engine.content.models import ExperienceKind, JoinPolicy
    from world_engine.runtime.models import RuntimeSnapshot, RunStatus

    w5_view = {
        "target_consumer": "player_shell",
        "actor_id": "annette",
        "where_summary": {
            "current_visible_location": "salon_w5",
            "scene_location": {"value": "salon_w5"},
        },
        "how_summary": {"facts": {"tone": "strained"}},
        "what_summary": {"facts": {"current_action": "listens"}},
    }
    flags = {"W5_AST_FRONTEND_PLAYER_VIEW_ENABLED": True}

    snap = RuntimeSnapshot(
        run_id="run-ws-1",
        template_id="goc",
        template_title="God of Carnage",
        kind=ExperienceKind.SOLO_STORY,
        join_policy=JoinPolicy.OWNER_ONLY,
        status=RunStatus.RUNNING,
        beat_id="opening",
        tension=0,
        viewer_participant_id="p-1",
        viewer_room_id="salon_w5",
        viewer_role_id="annette",
        viewer_display_name="Annette",
        available_actions=[],
        transcript_tail=[],
        metadata={},
        w5_player_view=w5_view,
        feature_flags=flags,
    )
    payload = snap.model_dump(mode="json")  # what broadcast_snapshot sends over WS
    assert payload["w5_player_view"]["target_consumer"] == "player_shell"
    assert payload["w5_player_view"]["where_summary"]["current_visible_location"] == "salon_w5"
    assert payload["w5_player_view"]["how_summary"]["facts"]["tone"] == "strained"
    assert "why_summary" not in payload["w5_player_view"]
    assert payload["feature_flags"]["W5_AST_FRONTEND_PLAYER_VIEW_ENABLED"] is True


def test_ws_runtime_snapshot_preserves_current_room_aliases() -> None:
    """Phase 6B-10: WS RuntimeSnapshot retains viewer_room_id and current_room
    as compatibility aliases even when w5_player_view is also present (ADR-0069).
    """
    from world_engine.content.models import ExperienceKind, JoinPolicy
    from world_engine.runtime.models import RuntimeSnapshot, RunStatus

    snap = RuntimeSnapshot(
        run_id="run-ws-2",
        template_id="goc",
        template_title="God of Carnage",
        kind=ExperienceKind.SOLO_STORY,
        join_policy=JoinPolicy.OWNER_ONLY,
        status=RunStatus.RUNNING,
        beat_id="opening",
        tension=0,
        viewer_participant_id="p-1",
        viewer_room_id="legacy_salon",
        viewer_role_id="annette",
        viewer_display_name="Annette",
        current_room={"id": "legacy_salon", "name": "Salon"},
        available_actions=[],
        transcript_tail=[],
        metadata={},
        w5_player_view={"target_consumer": "player_shell", "where_summary": {"current_visible_location": "salon_w5"}},
        feature_flags={"W5_AST_FRONTEND_PLAYER_VIEW_ENABLED": True},
    )
    payload = snap.model_dump(mode="json")
    # compat aliases must survive alongside w5_player_view — ADR-0069 phase: no removal
    assert payload["viewer_room_id"] == "legacy_salon"
    assert payload["current_room"]["id"] == "legacy_salon"
    # w5_player_view is also present
    assert payload["w5_player_view"]["where_summary"]["current_visible_location"] == "salon_w5"


def test_ws_payload_current_room_helper_uses_w5_player_view_first() -> None:
    """Phase 6B-10: when the WS payload carries w5_player_view with a location
    and feature_flags enables the W5 path, the JS roomFromSnapshot() helper
    returns the W5 location (not the legacy current_room value).
    This test verifies the payload carries the necessary keys for the
    frontend helper to make the right choice without additional logic changes.
    """
    from world_engine.content.models import ExperienceKind, JoinPolicy
    from world_engine.runtime.models import RuntimeSnapshot, RunStatus

    snap = RuntimeSnapshot(
        run_id="run-ws-3",
        template_id="goc",
        template_title="God of Carnage",
        kind=ExperienceKind.SOLO_STORY,
        join_policy=JoinPolicy.OWNER_ONLY,
        status=RunStatus.RUNNING,
        beat_id="opening",
        tension=0,
        viewer_participant_id="p-1",
        viewer_room_id="fallback_salon",
        viewer_role_id="annette",
        viewer_display_name="Annette",
        current_room={"id": "fallback_salon", "name": "Salon (legacy)"},
        available_actions=[],
        transcript_tail=[],
        metadata={},
        w5_player_view={
            "target_consumer": "player_shell",
            "where_summary": {
                "current_visible_location": "salon_w5",
                "scene_location": {"value": "salon_w5"},
            },
        },
        feature_flags={"W5_AST_FRONTEND_PLAYER_VIEW_ENABLED": True},
    )
    payload = snap.model_dump(mode="json")
    # Frontend helper reads: if w5FrontendPlayerViewEnabled(payload) → w5PlayerViewLocation(payload)
    # Verify payload has all required keys for that branch
    assert payload["feature_flags"]["W5_AST_FRONTEND_PLAYER_VIEW_ENABLED"] is True
    w5 = payload["w5_player_view"]
    assert w5 is not None
    where = w5.get("where_summary", {})
    w5_location = (
        where.get("current_visible_location")
        or where.get("current_location")
        or (where.get("scene_location") or {}).get("value")
    )
    assert w5_location == "salon_w5", "Frontend helper can extract W5 location from WS payload"
    # Legacy path still present as fallback — the helper prefers W5 but can fall back
    assert payload["current_room"]["id"] == "fallback_salon"


def test_ws_payload_falls_back_to_legacy_when_w5_missing() -> None:
    """Phase 6B-10: when w5_player_view is None the WS payload still carries
    viewer_room_id and current_room so legacy frontend logic continues to work.
    """
    from world_engine.content.models import ExperienceKind, JoinPolicy
    from world_engine.runtime.models import RuntimeSnapshot, RunStatus

    snap = RuntimeSnapshot(
        run_id="run-ws-4",
        template_id="goc",
        template_title="God of Carnage",
        kind=ExperienceKind.SOLO_STORY,
        join_policy=JoinPolicy.OWNER_ONLY,
        status=RunStatus.RUNNING,
        beat_id="opening",
        tension=0,
        viewer_participant_id="p-1",
        viewer_room_id="fallback_salon",
        viewer_role_id="annette",
        viewer_display_name="Annette",
        current_room={"id": "fallback_salon", "name": "Salon"},
        available_actions=[],
        transcript_tail=[],
        metadata={},
        w5_player_view=None,
        feature_flags={"W5_AST_FRONTEND_PLAYER_VIEW_ENABLED": True},
    )
    payload = snap.model_dump(mode="json")
    assert payload["w5_player_view"] is None
    # legacy aliases still present for frontend fallback path
    assert payload["viewer_room_id"] == "fallback_salon"
    assert payload["current_room"]["id"] == "fallback_salon"
    # feature flag is still advertised even when W5 view is absent
    assert payload["feature_flags"]["W5_AST_FRONTEND_PLAYER_VIEW_ENABLED"] is True
