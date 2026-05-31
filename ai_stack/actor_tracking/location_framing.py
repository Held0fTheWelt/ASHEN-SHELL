"""W5-first location framing for narrator and sensory consumers.

Phase 6C-1 adapter for ADR-0070. The helper accepts typed W5 projections or
snapshots, coerces persisted dict payloads through the W5 model layer, and
returns a compact location-framing object. It never emits raw W5 history.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from ai_stack.actor_tracking.models import (
    W5Projection,
    W5ProjectionConsumer,
    W5Snapshot,
)
from ai_stack.actor_tracking.projection import build_w5_projection_for_narrator


W5_LOCATION_FRAMING_SCHEMA_VERSION = "w5_location_framing.v1"
LEGACY_AREA_COMPAT_SCHEMA_VERSION = "legacy_area_compat.v1"

_W5_PROJECTION_SOURCE = "w5_projection"
_LEGACY_FALLBACK_SOURCE = "legacy_fallback"
_MISSING_W5_SOURCE = "missing_w5"
_MALFORMED_W5_SOURCE = "malformed_w5"
_W5_AUTHORITY = "w5"
_LEGACY_AUTHORITY = "legacy_fallback"
_W5_TRANSITION_SOURCE = "w5_location_framing"
_LEGACY_TRANSITION_SOURCE = "legacy"
_W5_AREA_COMPAT_SOURCE = "w5_location_framing"
_MALFORMED_AREA_COMPAT_SOURCE = "malformed_w5_fallback"
_OLD_PAYLOAD_AREA_COMPAT_SOURCE = "old_payload_fallback"


def _clean(value: Any) -> str | None:
    text = str(value or "").strip()
    return text or None


def _bool_or_none(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    return None


def _mapping(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def _coerce_snapshot_only(value: Any) -> W5Snapshot | None:
    if isinstance(value, W5Snapshot):
        return value
    if isinstance(value, Mapping):
        return W5Snapshot.from_dict(dict(value))
    return None


def _coerce_projection(
    value: Any,
    *,
    previous_value: Any = None,
    actor_id: str | None = None,
    actor_id_aliases: tuple[str, ...] | None = None,
) -> W5Projection | None:
    if value is None:
        return None
    if isinstance(value, W5Projection):
        return value
    if isinstance(value, W5Snapshot):
        previous_snapshot = _coerce_snapshot_only(previous_value)
        return build_w5_projection_for_narrator(
            value,
            actor_id=actor_id,
            actor_id_aliases=actor_id_aliases,
            previous_snapshot=previous_snapshot,
        )
    if isinstance(value, Mapping):
        raw = dict(value)
        if "target_consumer" in raw:
            return W5Projection.from_dict(raw)
        if "actors" in raw:
            previous_snapshot = _coerce_snapshot_only(previous_value)
            return build_w5_projection_for_narrator(
                W5Snapshot.from_dict(raw),
                actor_id=actor_id,
                actor_id_aliases=actor_id_aliases,
                previous_snapshot=previous_snapshot,
            )
    raise TypeError("unsupported_w5_location_framing_input")


def _projection_location(projection: W5Projection | None) -> str | None:
    if projection is None:
        return None
    where = projection.where_summary if isinstance(projection.where_summary, dict) else {}
    scene_location = where.get("scene_location")
    if isinstance(scene_location, Mapping):
        scene_value = _clean(scene_location.get("value"))
    else:
        scene_value = _clean(scene_location)
    facts = _mapping(where.get("facts"))
    return (
        _clean(where.get("current_location"))
        or _clean(where.get("current_visible_location"))
        or scene_value
        or _clean(facts.get("scene_location"))
    )


def _projection_scene_location(projection: W5Projection) -> str | None:
    where = projection.where_summary if isinstance(projection.where_summary, dict) else {}
    scene_location = where.get("scene_location")
    if isinstance(scene_location, Mapping):
        return _clean(scene_location.get("value"))
    return _clean(scene_location) or _clean(_mapping(where.get("facts")).get("scene_location"))


def _projection_previous_location(
    projection: W5Projection,
    previous_projection: W5Projection | None,
) -> str | None:
    where = projection.where_summary if isinstance(projection.where_summary, dict) else {}
    return _clean(where.get("previous_location")) or _projection_location(previous_projection)


def _has_inferred_why(projection: W5Projection) -> bool:
    truth = projection.truth_attribution if isinstance(projection.truth_attribution, dict) else {}
    return any(
        str(path).startswith("why_summary.") and str(value) == "inferred"
        for path, value in truth.items()
    )


def _fallback_locations(legacy_fallback: Mapping[str, Any] | None) -> tuple[str | None, str | None, str | None, bool]:
    legacy = dict(legacy_fallback or {})
    current = (
        _clean(legacy.get("current_location"))
        or _clean(legacy.get("current_location_id"))
        or _clean(legacy.get("current_area"))
        or _clean(legacy.get("to_location"))
        or _clean(legacy.get("to_location_id"))
        or _clean(legacy.get("to_area"))
    )
    previous = (
        _clean(legacy.get("previous_location"))
        or _clean(legacy.get("previous_location_id"))
        or _clean(legacy.get("previous_area"))
        or _clean(legacy.get("from_location"))
        or _clean(legacy.get("from_location_id"))
        or _clean(legacy.get("from_area"))
    )
    scene_location = _clean(legacy.get("scene_location")) or current
    changed = _bool_or_none(legacy.get("location_changed"))
    if changed is None:
        changed = _bool_or_none(legacy.get("scene_changed"))
    if changed is None:
        changed = bool(previous and current and previous != current)
    return current, previous, scene_location, bool(changed)


def _base_payload(
    *,
    source: str,
    current_location: str | None,
    previous_location: str | None,
    scene_location: str | None,
    location_changed: bool,
    source_attribution: dict[str, str] | None = None,
    truth_attribution: dict[str, str] | None = None,
    has_how: bool = False,
    has_inferred_why: bool = False,
    how_summary: dict[str, Any] | None = None,
    why_summary: dict[str, Any] | None = None,
    target_consumer: str | None = None,
    actor_id: str | None = None,
    warnings: list[str] | None = None,
    fallback_reason: str | None = None,
) -> dict[str, Any]:
    return {
        "schema_version": W5_LOCATION_FRAMING_SCHEMA_VERSION,
        "source": source,
        "target_consumer": target_consumer,
        "actor_id": actor_id,
        "current_location": current_location,
        "previous_location": previous_location,
        "scene_location": scene_location,
        "location_changed": bool(location_changed),
        "scene_changed": bool(location_changed),
        "from_location": previous_location,
        "from_area": previous_location,
        "to_location": current_location,
        "to_area": current_location,
        "current_area": current_location,
        "source_attribution": dict(source_attribution or {}),
        "truth_attribution": dict(truth_attribution or {}),
        "how_summary": dict(how_summary or {}),
        "why_summary": dict(why_summary or {}),
        "has_how": bool(has_how),
        "has_inferred_why": bool(has_inferred_why),
        "warnings": list(warnings or []),
        "fallback_reason": fallback_reason,
    }


def _fallback_payload(
    *,
    reason: str,
    legacy_fallback: Mapping[str, Any] | None,
    warning_detail: str | None = None,
) -> dict[str, Any]:
    current, previous, scene_location, changed = _fallback_locations(legacy_fallback)
    has_legacy_location = bool(current or previous or scene_location)
    source = _LEGACY_FALLBACK_SOURCE if has_legacy_location else reason
    warnings = [reason]
    if warning_detail:
        warnings.append(warning_detail[:160])
    return _base_payload(
        source=source,
        current_location=current,
        previous_location=previous,
        scene_location=scene_location,
        location_changed=changed,
        warnings=warnings,
        fallback_reason=reason,
    )


def _framing_location_value(frame: Mapping[str, Any]) -> str | None:
    return (
        _clean(frame.get("current_location"))
        or _clean(frame.get("current_area"))
        or _clean(frame.get("scene_location"))
        or _clean(frame.get("to_location"))
        or _clean(frame.get("to_area"))
    )


def location_framing_is_valid_w5(framing: Mapping[str, Any] | None) -> bool:
    """Return whether a framing object can be used as W5 location authority."""

    frame = dict(framing or {})
    return frame.get("source") == _W5_PROJECTION_SOURCE and bool(_framing_location_value(frame))


def _legacy_area_values(
    legacy_fields: Mapping[str, Any] | None,
) -> tuple[str | None, str | None, str | None, bool]:
    legacy = dict(legacy_fields or {})
    current = (
        _clean(legacy.get("current_area"))
        or _clean(legacy.get("current_location_id"))
        or _clean(legacy.get("current_location"))
        or _clean(legacy.get("to_area"))
        or _clean(legacy.get("to_location_id"))
        or _clean(legacy.get("to_location"))
    )
    previous = (
        _clean(legacy.get("from_area"))
        or _clean(legacy.get("from_location_id"))
        or _clean(legacy.get("from_location"))
        or _clean(legacy.get("previous_area"))
        or _clean(legacy.get("previous_location_id"))
        or _clean(legacy.get("previous_location"))
    )
    to_location = (
        _clean(legacy.get("to_area"))
        or _clean(legacy.get("to_location_id"))
        or _clean(legacy.get("to_location"))
        or current
    )
    changed = _bool_or_none(legacy.get("location_changed"))
    if changed is None:
        changed = _bool_or_none(legacy.get("scene_changed"))
    if changed is None:
        changed = bool(previous and to_location and previous != to_location)
    return current, previous, to_location, bool(changed)


def _compat_source_for_framing(
    frame: Mapping[str, Any],
    *,
    valid_w5: bool,
    force_legacy_fallback: bool,
) -> tuple[str, str | None]:
    if valid_w5 and not force_legacy_fallback:
        return _W5_AREA_COMPAT_SOURCE, None
    if not frame:
        return _OLD_PAYLOAD_AREA_COMPAT_SOURCE, "old_payload_without_w5_location_framing"
    source = str(frame.get("source") or "").strip()
    reason = str(frame.get("fallback_reason") or "").strip() or None
    if source == _MALFORMED_W5_SOURCE or reason == _MALFORMED_W5_SOURCE:
        return _MALFORMED_AREA_COMPAT_SOURCE, reason or _MALFORMED_W5_SOURCE
    return _LEGACY_FALLBACK_SOURCE, reason


def w5_location_framing_to_legacy_area_fields(
    framing: Mapping[str, Any] | None,
    *,
    legacy_fields: Mapping[str, Any] | None = None,
    force_legacy_fallback: bool = False,
    fallback_reason: str | None = None,
) -> dict[str, Any]:
    """Derive legacy area compatibility fields from W5 location framing.

    W5-native consumers should read ``w5_location_framing`` directly. This shim
    exists only for legacy consumers that still require ``current_area``,
    ``from_area``, or ``to_area`` while the removal-readiness window is open.
    """

    frame = dict(framing or {})
    valid_w5 = location_framing_is_valid_w5(frame)
    source, source_reason = _compat_source_for_framing(
        frame,
        valid_w5=valid_w5,
        force_legacy_fallback=force_legacy_fallback,
    )
    reason = fallback_reason or source_reason

    if source == _W5_AREA_COMPAT_SOURCE:
        current = _clean(frame.get("current_location")) or _clean(frame.get("scene_location"))
        previous = _clean(frame.get("previous_location")) or _clean(frame.get("from_location"))
        to_location = _clean(frame.get("to_location")) or current
        changed = bool(frame.get("location_changed") or frame.get("scene_changed"))
    else:
        current, previous, to_location, changed = _legacy_area_values(legacy_fields)
        if not (current or previous or to_location):
            current, previous, to_location, changed = _legacy_area_values(frame)

    authority = _W5_AUTHORITY if source == _W5_AREA_COMPAT_SOURCE else _LEGACY_AUTHORITY
    transition_source = _W5_TRANSITION_SOURCE if authority == _W5_AUTHORITY else _LEGACY_TRANSITION_SOURCE
    failed = frame.get("source") in {_MISSING_W5_SOURCE, _MALFORMED_W5_SOURCE} or frame.get(
        "fallback_reason"
    ) in {_MISSING_W5_SOURCE, _MALFORMED_W5_SOURCE}
    return {
        "schema_version": LEGACY_AREA_COMPAT_SCHEMA_VERSION,
        "source": source,
        "legacy_area_compat_source": source,
        "legacy_area_compat_reason": reason,
        "current_area": current,
        "from_area": previous,
        "to_area": to_location,
        "current_location_id": current,
        "from_location_id": previous,
        "to_location_id": to_location,
        "location_changed": bool(changed),
        "scene_changed": bool(changed),
        "location_framing_authority": authority,
        "local_context_transition_source": transition_source,
        "w5_location_framing_used": source == _W5_AREA_COMPAT_SOURCE,
        "w5_location_framing_failed": failed,
        "w5_location_framing_source": frame.get("source"),
        "w5_location_framing_fallback_reason": frame.get("fallback_reason"),
        "w5_location_changed": bool(changed),
        "w5_current_location": current,
        "w5_previous_location": previous,
        "has_how": bool(frame.get("has_how")),
        "has_inferred_why": bool(frame.get("has_inferred_why")),
    }


def build_legacy_area_compat_from_w5_location_framing(
    framing: Mapping[str, Any] | None,
    *,
    legacy_fields: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Named rollback shim for ADR-0071 removal-readiness checks."""

    return w5_location_framing_to_legacy_area_fields(
        framing,
        legacy_fields=legacy_fields,
    )


def ensure_legacy_area_fields_for_compat(
    payload: Mapping[str, Any] | None,
    *,
    w5_location_framing: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Return ``payload`` with legacy area fields supplied by the compat shim."""

    out = dict(payload or {})
    compat = w5_location_framing_to_legacy_area_fields(
        w5_location_framing,
        legacy_fields=out,
    )
    for key in (
        "current_area",
        "from_area",
        "to_area",
        "current_location_id",
        "from_location_id",
        "to_location_id",
        "location_changed",
        "scene_changed",
    ):
        value = compat.get(key)
        if value is not None:
            out[key] = value
    out["legacy_area_compat_source"] = compat["legacy_area_compat_source"]
    out["legacy_area_compat_reason"] = compat["legacy_area_compat_reason"]
    out["location_framing_authority"] = compat["location_framing_authority"]
    out["local_context_transition_source"] = compat["local_context_transition_source"]
    return out


def build_w5_location_framing(
    w5_value: W5Projection | W5Snapshot | Mapping[str, Any] | None,
    *,
    previous_w5_value: W5Projection | W5Snapshot | Mapping[str, Any] | None = None,
    actor_id: str | None = None,
    actor_id_aliases: tuple[str, ...] | None = None,
    legacy_fallback: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Return compact W5-first location framing for narrator/sensory consumers.

    ``w5_value`` may be a typed ``W5Projection`` / ``W5Snapshot`` or a persisted
    dict for either model. Dict payloads are coerced through the typed model
    helpers before any semantic values are read.
    """

    try:
        projection = _coerce_projection(
            w5_value,
            previous_value=previous_w5_value,
            actor_id=actor_id,
            actor_id_aliases=actor_id_aliases,
        )
        previous_projection = _coerce_projection(
            previous_w5_value,
            actor_id=actor_id,
            actor_id_aliases=actor_id_aliases,
        )
    except Exception as exc:
        return _fallback_payload(
            reason=_MALFORMED_W5_SOURCE,
            legacy_fallback=legacy_fallback,
            warning_detail=str(exc),
        )

    if projection is None:
        return _fallback_payload(
            reason=_MISSING_W5_SOURCE,
            legacy_fallback=legacy_fallback,
        )

    where = projection.where_summary if isinstance(projection.where_summary, dict) else {}
    current_location = _projection_location(projection)
    previous_location = _projection_previous_location(projection, previous_projection)
    scene_location = _projection_scene_location(projection) or current_location
    if not (current_location or scene_location):
        return _fallback_payload(
            reason=_MISSING_W5_SOURCE,
            legacy_fallback=legacy_fallback,
        )
    location_changed = _bool_or_none(where.get("location_changed"))
    if location_changed is None:
        location_changed = bool(
            current_location and previous_location and current_location != previous_location
        )

    target_consumer = (
        projection.target_consumer.value
        if isinstance(projection.target_consumer, W5ProjectionConsumer)
        else str(projection.target_consumer)
    )
    how_summary = projection.how_summary if isinstance(projection.how_summary, dict) else {}
    why_summary = projection.why_summary if isinstance(projection.why_summary, dict) else {}
    return _base_payload(
        source=_W5_PROJECTION_SOURCE,
        current_location=current_location,
        previous_location=previous_location,
        scene_location=scene_location,
        location_changed=bool(location_changed),
        source_attribution=projection.source_attribution,
        truth_attribution=projection.truth_attribution,
        has_how=bool(_mapping(how_summary.get("facts"))),
        has_inferred_why=_has_inferred_why(projection),
        how_summary=how_summary,
        why_summary=why_summary,
        target_consumer=target_consumer,
        actor_id=projection.actor_id,
        warnings=[],
        fallback_reason=None,
    )


def _movement_target_from_legacy_transition(legacy_transition: Mapping[str, Any]) -> str | None:
    transition_type = _clean(legacy_transition.get("transition_type"))
    has_movement_shape = (
        transition_type in {"movement", "move_local", "move_offscreen"}
        or bool(legacy_transition.get("new_area_established"))
        or bool(legacy_transition.get("location_found"))
    )
    if not has_movement_shape:
        return None
    return _clean(legacy_transition.get("to_location_id")) or _clean(legacy_transition.get("to_area"))


def _w5_unsuitable_for_transition_decision(
    *,
    valid_w5: bool,
    changed: bool,
    to_location: str | None,
    current: str | None,
    legacy_transition: Mapping[str, Any],
) -> bool:
    if not valid_w5 or changed:
        return False
    legacy_target = _movement_target_from_legacy_transition(legacy_transition)
    if not legacy_target:
        return False
    w5_target = to_location or current
    return bool(w5_target and legacy_target != w5_target)


def location_framing_to_local_context_transition(
    framing: Mapping[str, Any] | None,
    *,
    legacy_transition: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Overlay W5 location framing onto the legacy LocalContextTransition shape."""

    out = dict(legacy_transition or {})
    frame = dict(framing or {})
    if not frame:
        return out

    current = _clean(frame.get("current_location")) or _clean(frame.get("current_area"))
    previous = _clean(frame.get("previous_location")) or _clean(frame.get("from_location"))
    to_location = _clean(frame.get("to_location")) or current
    from_location = _clean(frame.get("from_location")) or previous
    changed = bool(frame.get("location_changed") or frame.get("scene_changed"))
    valid_w5 = location_framing_is_valid_w5(frame)
    legacy_to = _clean(out.get("to_location_id")) or _clean(out.get("to_area"))
    legacy_current = _clean(out.get("current_location_id")) or _clean(out.get("current_area"))
    w5_unsuitable = _w5_unsuitable_for_transition_decision(
        valid_w5=valid_w5,
        changed=changed,
        to_location=to_location,
        current=current,
        legacy_transition=out,
    )
    authority = _W5_AUTHORITY if valid_w5 and not w5_unsuitable else _LEGACY_AUTHORITY
    transition_source = _W5_TRANSITION_SOURCE if authority == _W5_AUTHORITY else _LEGACY_TRANSITION_SOURCE
    if authority == _LEGACY_AUTHORITY and legacy_to:
        to_location = legacy_to
    elif authority == _LEGACY_AUTHORITY and legacy_current:
        to_location = None
    if authority == _LEGACY_AUTHORITY and legacy_current:
        current = legacy_current

    compat = w5_location_framing_to_legacy_area_fields(
        frame,
        legacy_fields=out,
        force_legacy_fallback=authority == _LEGACY_AUTHORITY,
        fallback_reason="w5_unsuitable_for_transition_decision" if w5_unsuitable else None,
    )
    from_location = _clean(compat.get("from_area")) or from_location
    to_location = _clean(compat.get("to_area")) or to_location
    current = _clean(compat.get("current_area")) or current

    if from_location:
        out["from_location_id"] = from_location
        out["from_area"] = from_location
    if to_location:
        out["to_location_id"] = to_location
        out["to_area"] = to_location
        out["current_location_id"] = to_location
        out["current_area"] = to_location
    elif current:
        out["current_location_id"] = current
        out["current_area"] = current
    legacy_changed = _bool_or_none(out.get("location_changed"))
    if legacy_changed is None:
        legacy_changed = _bool_or_none(out.get("scene_changed"))
    effective_changed = changed if authority == _W5_AUTHORITY or legacy_changed is None else bool(legacy_changed)
    out["location_changed"] = effective_changed
    out["scene_changed"] = effective_changed
    out["location_framing_authority"] = authority
    out["local_context_transition_source"] = transition_source
    out["legacy_area_compat_source"] = compat["legacy_area_compat_source"]
    out["legacy_area_compat_reason"] = compat["legacy_area_compat_reason"]
    failed = frame.get("source") in {_MISSING_W5_SOURCE, _MALFORMED_W5_SOURCE} or frame.get(
        "fallback_reason"
    ) in {_MISSING_W5_SOURCE, _MALFORMED_W5_SOURCE}
    out["w5_location_framing"] = {
        "schema_version": frame.get("schema_version") or W5_LOCATION_FRAMING_SCHEMA_VERSION,
        "source": frame.get("source"),
        "fallback_reason": frame.get("fallback_reason"),
        "w5_location_framing_used": frame.get("source") == _W5_PROJECTION_SOURCE,
        "w5_location_framing_failed": failed,
        "w5_location_framing_source": frame.get("source"),
        "w5_location_framing_fallback_reason": frame.get("fallback_reason"),
        "w5_location_changed": effective_changed,
        "w5_current_location": current,
        "w5_previous_location": previous,
        "location_framing_authority": authority,
        "local_context_transition_source": transition_source,
        "legacy_area_compat_source": compat["legacy_area_compat_source"],
        "legacy_area_compat_reason": compat["legacy_area_compat_reason"],
        "has_how": bool(frame.get("has_how")),
        "has_inferred_why": bool(frame.get("has_inferred_why")),
    }
    return out


__all__ = [
    "LEGACY_AREA_COMPAT_SCHEMA_VERSION",
    "W5_LOCATION_FRAMING_SCHEMA_VERSION",
    "build_legacy_area_compat_from_w5_location_framing",
    "build_w5_location_framing",
    "ensure_legacy_area_fields_for_compat",
    "location_framing_is_valid_w5",
    "location_framing_to_local_context_transition",
    "w5_location_framing_to_legacy_area_fields",
]
