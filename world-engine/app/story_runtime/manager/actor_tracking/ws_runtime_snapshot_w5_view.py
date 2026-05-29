"""W5 player-view bridge for RuntimeSnapshot WebSocket payloads."""

from __future__ import annotations

from typing import Any

from .session_state_w5_view import build_w5_player_view_for_session


def _metadata_story_session_id(instance: Any) -> str | None:
    metadata = instance.metadata if isinstance(getattr(instance, "metadata", None), dict) else {}
    for key in ("world_engine_story_session_id", "runtime_session_id", "story_session_id"):
        value = str(metadata.get(key) or "").strip()
        if value:
            return value
    return None


def _session_run_id(session: Any) -> str | None:
    provenance = session.content_provenance if isinstance(getattr(session, "content_provenance", None), dict) else {}
    for key in ("run_id", "play_run_id", "runtime_run_id"):
        value = str(provenance.get(key) or "").strip()
        if value:
            return value
    projection = session.runtime_projection if isinstance(getattr(session, "runtime_projection", None), dict) else {}
    for key in ("run_id", "play_run_id", "runtime_run_id"):
        value = str(projection.get(key) or "").strip()
        if value:
            return value
    return None


def _story_session_for_runtime_instance(story_manager: Any | None, instance: Any) -> Any | None:
    if story_manager is None:
        return None

    explicit_session_id = _metadata_story_session_id(instance)
    if explicit_session_id:
        get_session = getattr(story_manager, "get_session", None)
        if callable(get_session):
            try:
                return get_session(explicit_session_id)
            except Exception:
                return None
        sessions = getattr(story_manager, "sessions", None)
        if isinstance(sessions, dict):
            return sessions.get(explicit_session_id)

    sessions = getattr(story_manager, "sessions", None)
    if not isinstance(sessions, dict):
        return None
    run_id = str(getattr(instance, "id", "") or "").strip()
    if not run_id:
        return None
    for session in sessions.values():
        if _session_run_id(session) == run_id:
            return session
    return None


def _legacy_location_from_viewer(viewer: Any) -> str | None:
    value = str(getattr(viewer, "current_room_id", "") or "").strip()
    return value or None


def _legacy_only_diagnostics(*, fallback_location: str | None, reason: str) -> dict[str, Any]:
    return {
        "w5_player_view_used": False,
        "w5_player_view_failed": None,
        "w5_player_view_fallback_reason": reason,
        "w5_snapshot_id": None,
        "w5_player_view_source": "fallback",
        "ws_w5_player_view_source": "legacy_only",
        "w5_player_view_has_how": False,
        "w5_player_view_has_inferred_why": False,
        "current_room_source": "fallback_current_room",
        "current_room_fallback_value": fallback_location,
        "current_room_legacy_value": fallback_location,
        "current_room_w5_value": None,
        "current_room_mismatch": False,
    }


def _with_ws_alias_deprecation_diagnostics(diagnostics: dict[str, Any] | None) -> dict[str, Any] | None:
    if diagnostics is None:
        return None
    out = dict(diagnostics)
    out.update(
        {
            "ws_current_room_aliases_deprecated": True,
            "ws_current_room_aliases": ["viewer_room_id", "current_room", "current_room_id"],
            "ws_current_room_aliases_deprecation_phase": "6B-12",
            "ws_current_room_aliases_replacement": "w5_player_view",
            "ws_current_room_aliases_removal_phase": "future_adr_after_client_readiness",
        }
    )
    return out


def build_ws_runtime_snapshot_w5_player_view(
    *,
    story_manager: Any | None,
    instance: Any,
    viewer: Any,
) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    """Build the per-viewer W5 player view for a RuntimeSnapshot.

    The primary bridge is the story-session binding stored on RuntimeInstance
    metadata. The content_provenance.run_id lookup is retained as a safe fallback
    for already-created sessions that predate the binding.
    """

    fallback_location = _legacy_location_from_viewer(viewer)
    session = _story_session_for_runtime_instance(story_manager, instance)
    if session is None:
        return None, _with_ws_alias_deprecation_diagnostics(
            _legacy_only_diagnostics(
                fallback_location=fallback_location,
                reason="story_session_not_bound",
            )
        )

    player_actor_id = str(getattr(viewer, "role_id", "") or "").strip() or None
    view, diagnostics = build_w5_player_view_for_session(
        session,
        player_actor_id=player_actor_id,
        fallback_current_room_id=fallback_location,
        include_disabled_diagnostics=True,
    )
    return view, _with_ws_alias_deprecation_diagnostics(diagnostics)


__all__ = ["build_ws_runtime_snapshot_w5_player_view"]
