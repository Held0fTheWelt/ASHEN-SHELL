"""Public compatibility-alias telemetry helpers for W5 player views."""

from __future__ import annotations

from typing import Any


PUBLIC_ROOM_ALIASES: tuple[str, ...] = ("viewer_room_id", "current_room", "current_room_id")


def w5_player_view_has_location_authority(view: dict[str, Any] | None) -> bool:
    """Return True when a player-shell W5 view carries a public location value."""

    if not isinstance(view, dict):
        return False
    where = view.get("where_summary") if isinstance(view.get("where_summary"), dict) else {}
    for key in ("current_visible_location", "current_location"):
        value = str(where.get(key) or "").strip()
        if value:
            return True
    scene_location = where.get("scene_location")
    if isinstance(scene_location, dict):
        value = str(scene_location.get("value") or "").strip()
        if value:
            return True
    facts = where.get("facts") if isinstance(where.get("facts"), dict) else {}
    return bool(str(facts.get("scene_location") or "").strip())


def build_deprecated_public_room_alias_usage(
    *,
    aliases: tuple[str, ...] | list[str] | None = None,
    w5_player_view: dict[str, Any] | None = None,
    w5_player_view_present: bool | None = None,
    w5_player_view_authority: bool | None = None,
) -> dict[str, Any]:
    """Build compact Phase 6B-13 telemetry for deprecated public room aliases."""

    alias_list = list(aliases or PUBLIC_ROOM_ALIASES)
    has_view = isinstance(w5_player_view, dict)
    authority = (
        w5_player_view_has_location_authority(w5_player_view)
        if w5_player_view_authority is None
        else bool(w5_player_view_authority)
    )
    return {
        "room_aliases_emitted": bool(alias_list),
        "w5_player_view_present": has_view if w5_player_view_present is None else bool(w5_player_view_present),
        "w5_player_view_authority": authority,
        "aliases": alias_list,
        "phase": "6B-13",
        "removal_blocked_until": "client_readiness_evidence",
    }


__all__ = [
    "PUBLIC_ROOM_ALIASES",
    "build_deprecated_public_room_alias_usage",
    "w5_player_view_has_location_authority",
]
