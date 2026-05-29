"""Session-state W5 view helpers.

Builds W5 actor-state views from manager session state for diagnostics and runtime projections.
"""
from __future__ import annotations

import os
from typing import Any

from ai_stack.actor_tracking import build_w5_projection_for_player_shell


def _w5_ast_frontend_player_view_enabled() -> bool:
    # Phase 6B-1: player-shell W5 projection is default-on. Legacy
    # ``current_room`` fallback remains in place. Explicit opt-out via
    # ``0/false/no/off`` keeps the pre-Phase-6B-1 behavior.
    raw = (os.environ.get("W5_AST_FRONTEND_PLAYER_VIEW_ENABLED") or "").strip().lower()
    if raw in {"0", "false", "no", "off"}:
        return False
    return True


def _player_actor_id_from_projection(runtime_projection: dict[str, Any] | None) -> str | None:
    projection = runtime_projection if isinstance(runtime_projection, dict) else {}
    for key in ("human_actor_id", "selected_player_role", "player_actor_id", "viewer_actor_id"):
        value = str(projection.get(key) or "").strip()
        if value:
            return value
    return None


def _w5_player_view_location(view: dict[str, Any] | None) -> str | None:
    if not isinstance(view, dict):
        return None
    where = view.get("where_summary") if isinstance(view.get("where_summary"), dict) else {}
    for key in ("current_visible_location", "current_location"):
        value = str(where.get(key) or "").strip()
        if value:
            return value
    scene_location = where.get("scene_location")
    if isinstance(scene_location, dict):
        value = str(scene_location.get("value") or "").strip()
        if value:
            return value
    facts = where.get("facts") if isinstance(where.get("facts"), dict) else {}
    value = str(facts.get("scene_location") or "").strip()
    return value or None


def _w5_projection_has_inferred_why(view: dict[str, Any] | None) -> bool:
    if not isinstance(view, dict):
        return False
    truth = view.get("truth_attribution")
    if not isinstance(truth, dict):
        return False
    return any(path.startswith("why_summary.") and value == "inferred" for path, value in truth.items())


def _fallback_current_room_id(session: Any) -> str | None:
    runtime_world = session.runtime_world if isinstance(session.runtime_world, dict) else {}
    environment_state = session.environment_state if isinstance(session.environment_state, dict) else {}
    value = str(
        runtime_world.get("current_room_id")
        or environment_state.get("current_room_id")
        or environment_state.get("current_area")
        or ""
    ).strip()
    return value or None


def _player_view_diagnostics(
    *,
    used: bool,
    failed: str | None,
    fallback_reason: str | None,
    snapshot_id: str | None,
    w5_location: str | None,
    fallback_location: str | None,
    has_how: bool,
    has_inferred_why: bool,
    ws_w5_player_view_source: str | None = None,
) -> dict[str, Any]:
    mismatch = bool(w5_location and fallback_location and w5_location != fallback_location)
    source = "w5_projection" if used else "fallback"
    ws_source = ws_w5_player_view_source or ("w5_projection" if used else "legacy_only")
    current_room_source = "w5_player_view" if used else "fallback_current_room"
    diagnostic = {
        "w5_player_view_used": used,
        "w5_player_view_failed": failed,
        "w5_player_view_fallback_reason": fallback_reason,
        "w5_snapshot_id": snapshot_id,
        "w5_player_view_source": source,
        "ws_w5_player_view_source": ws_source,
        "w5_player_view_has_how": has_how,
        "w5_player_view_has_inferred_why": has_inferred_why,
        "current_room_source": current_room_source,
        "current_room_fallback_value": fallback_location,
        "current_room_legacy_value": fallback_location,
        "current_room_w5_value": w5_location,
        "current_room_mismatch": mismatch,
    }
    return diagnostic


def _fallback_source_for_reason(reason: str | None) -> str:
    if reason == "frontend_player_view_disabled":
        return "legacy_only"
    if reason == "missing_w5_latest_snapshot":
        return "missing_w5"
    return "malformed_w5"


def build_w5_player_view_for_session(
    session: Any,
    *,
    player_actor_id: str | None = None,
    fallback_current_room_id: str | None = None,
    include_disabled_diagnostics: bool = True,
) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    if not _w5_ast_frontend_player_view_enabled():
        if not include_disabled_diagnostics:
            return None, None
        legacy_location = fallback_current_room_id or _fallback_current_room_id(session)
        return None, _player_view_diagnostics(
            used=False,
            failed=None,
            fallback_reason="frontend_player_view_disabled",
            snapshot_id=None,
            w5_location=None,
            fallback_location=legacy_location,
            has_how=False,
            has_inferred_why=False,
            ws_w5_player_view_source="legacy_only",
        )
    resolved_player_actor_id = player_actor_id or _player_actor_id_from_projection(
        session.runtime_projection if isinstance(session.runtime_projection, dict) else None
    )
    fallback_location = fallback_current_room_id or _fallback_current_room_id(session)
    try:
        if not isinstance(session.w5_latest_snapshot, dict):
            raise ValueError("missing_w5_latest_snapshot")
        projection = build_w5_projection_for_player_shell(
            session.w5_latest_snapshot,
            player_actor_id=resolved_player_actor_id,
        )
        view = projection.to_dict()
        location = _w5_player_view_location(view)
        used = bool(location)
        failed = None if used else "missing_player_visible_location"
        diagnostics = _player_view_diagnostics(
            used=used,
            failed=failed,
            fallback_reason=None if used else failed,
            snapshot_id=projection.where_summary.get("w5_snapshot_id")
            if isinstance(projection.where_summary, dict)
            else None,
            w5_location=location,
            fallback_location=fallback_location,
            has_how=bool(projection.how_summary.get("facts"))
            if isinstance(projection.how_summary, dict)
            else False,
            has_inferred_why=_w5_projection_has_inferred_why(view),
            ws_w5_player_view_source="w5_projection" if used else _fallback_source_for_reason(failed),
        )
        return view if used else None, diagnostics
    except Exception as exc:
        reason = str(exc)
        return None, _player_view_diagnostics(
            used=False,
            failed=reason,
            fallback_reason=reason,
            snapshot_id=None,
            w5_location=None,
            fallback_location=fallback_location,
            has_how=False,
            has_inferred_why=False,
            ws_w5_player_view_source=_fallback_source_for_reason(reason),
        )


def _maybe_build_w5_player_view_for_session(session: Any) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    return build_w5_player_view_for_session(
        session,
        include_disabled_diagnostics=False,
    )
