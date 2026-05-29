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


def test_backend_static_current_room_helper_is_w5_first_with_fallback() -> None:
    source = (Path(__file__).resolve().parents[1] / "app/web/static/app.js").read_text(encoding="utf-8")
    assert "function currentRoomFromSnapshot(snapshot)" in source
    assert "if (w5FrontendPlayerViewEnabled(snapshot))" in source
    assert "const w5Room = roomFromW5PlayerView(snapshot);" in source
    assert "if (w5Room) return w5Room;" in source
    assert "return snapshot.current_room || null;" in source
    assert "function currentRoom() {\n  return currentRoomFromSnapshot(state.snapshot);\n}" in source
    assert "if (!where) return null;" in source
    assert "where.scene_location && where.scene_location.value" in source
    assert "why_summary" not in source


def test_live_ws_room_helper_is_w5_first_and_does_not_render_private_why() -> None:
    source = Path("frontend/static/play_live_ws.js").read_text(encoding="utf-8")
    assert "function roomFromSnapshot(snapshot)" in source
    assert "if (w5FrontendPlayerViewEnabled(snapshot))" in source
    assert "const roomId = w5PlayerViewLocation(snapshot);" in source
    assert "return snapshot.current_room || null;" in source
    assert "if (!where) return null;" in source
    assert "where.scene_location && where.scene_location.value" in source
    assert "why_summary" not in source


def test_runtime_snapshot_viewer_room_id_has_compatibility_alias_comment() -> None:
    """Phase 6B-9: RuntimeSnapshot.viewer_room_id must be annotated as a compat alias."""
    src = (Path(__file__).resolve().parents[1] / "app/runtime/models.py").read_text(encoding="utf-8")
    assert "viewer_room_id" in src
    assert "compat alias" in src
    assert "ADR-0069" in src
    assert "w5_player_view" in src


def test_runtime_snapshot_current_room_has_compatibility_alias_comment() -> None:
    """Phase 6B-9: RuntimeSnapshot.current_room must be annotated as a compat alias."""
    src = (Path(__file__).resolve().parents[1] / "app/runtime/models.py").read_text(encoding="utf-8")
    assert "current_room" in src
    assert "compat alias" in src
    assert "ADR-0069" in src


def test_world_engine_static_currentroom_is_w5_first_with_fallback() -> None:
    """Phase 6B-9: world-engine standalone UI must follow the same W5-first pattern
    as backend/app/web/static/app.js and frontend/static/play_live_ws.js."""
    source = (
        Path(__file__).resolve().parents[2]
        / "world-engine/app/web/static/app.js"
    ).read_text(encoding="utf-8")
    assert "function w5FrontendPlayerViewEnabled(snapshot)" in source, (
        "world-engine/app/web/static/app.js must declare w5FrontendPlayerViewEnabled()"
    )
    assert "function w5PlayerViewLocation(snapshot)" in source, (
        "world-engine/app/web/static/app.js must declare w5PlayerViewLocation()"
    )
    assert "function currentRoomFromSnapshot(snapshot)" in source, (
        "world-engine/app/web/static/app.js must declare currentRoomFromSnapshot()"
    )
    assert "if (w5FrontendPlayerViewEnabled(snapshot))" in source, (
        "currentRoomFromSnapshot must gate on the feature flag"
    )
    assert "return snapshot.current_room || null;" in source, (
        "legacy fallback must remain present"
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


def test_ws_runtime_snapshot_w5_player_view_gap_is_documented() -> None:
    """Phase 6B-9 gap tracker: the WS RuntimeSnapshot does NOT yet carry a
    w5_player_view field declaration. This test documents the gap explicitly so
    Phase 6B-10 can remove it once RuntimeEngine.build_snapshot() is wired.

    The compat alias comments on viewer_room_id and current_room reference the
    string 'w5_player_view' as the replacement surface — that is expected and
    correct. This test checks for an actual field declaration line, not comments.

    When Phase 6B-10 wires w5_player_view into RuntimeSnapshot, replace this
    test with one that asserts the field IS present and correctly populated.
    """
    import re

    field_pattern = re.compile(r"^\s+w5_player_view\s*:", re.MULTILINE)

    we_models = (
        Path(__file__).resolve().parents[2]
        / "world-engine/app/runtime/models.py"
    ).read_text(encoding="utf-8")
    snapshot_body = we_models.split("class RuntimeSnapshot")[1].split("\nclass ")[0]
    assert not field_pattern.search(snapshot_body), (
        "RuntimeSnapshot (world-engine) now has a w5_player_view field — Phase 6B-10 has landed. "
        "Replace this test with one that asserts w5_player_view is correctly populated."
    )
    be_models = (
        Path(__file__).resolve().parents[1]
        / "app/runtime/models.py"
    ).read_text(encoding="utf-8")
    snapshot_body_be = be_models.split("class RuntimeSnapshot")[1].split("\nclass ")[0]
    assert not field_pattern.search(snapshot_body_be), (
        "RuntimeSnapshot (backend) now has a w5_player_view field — Phase 6B-10 has landed. "
        "Replace this test with one that asserts w5_player_view is correctly populated."
    )
