"""Contract helpers for durable story environment state.

The functions in this module keep Pi15 environment truth tied to canonical
content and structured runtime state. They intentionally return JSON-safe
dicts so world-engine can persist them without importing UI/runtime models.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ai_stack.contracts.serialization import (
    json_safe as _json_safe,
    strict_list as _strict_list,
)

from ai_stack.module_runtime_policy import load_module_runtime_policy


ENVIRONMENT_MODEL_SCHEMA_VERSION = "environment_model.v1"
ENVIRONMENT_STATE_SCHEMA_VERSION = "environment_state.v1"
ENVIRONMENT_EVENT_SCHEMA_VERSION = "environment_event.v1"
ENVIRONMENT_RENDER_CONTEXT_SCHEMA_VERSION = "environment_render_context.v1"



def _clean_id(value: Any) -> str:
    return str(value or "").strip()


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}



def _actor_ids_from_projection(
    *,
    runtime_projection: dict[str, Any] | None = None,
    actor_lane_context: dict[str, Any] | None = None,
) -> list[str]:
    out: list[str] = []

    def add(value: Any) -> None:
        actor_id = _clean_id(value)
        if actor_id and actor_id not in out:
            out.append(actor_id)

    for src in (_as_dict(runtime_projection), _as_dict(actor_lane_context)):
        add(src.get("human_actor_id"))
        add(src.get("selected_player_role"))
        for actor_id in _strict_list(src.get("npc_actor_ids")):
            add(actor_id)
        lanes = src.get("actor_lanes")
        if isinstance(lanes, dict):
            for actor_id in lanes.keys():
                add(actor_id)
    return out


def build_environment_model(
    *,
    module_id: str,
    runtime_profile_id: str | None = None,
    content_modules_root: Path | str | None = None,
) -> dict[str, Any]:
    """Build a canonical environment model from module runtime policy content."""
    mid = _clean_id(module_id)
    try:
        policy = load_module_runtime_policy(
            mid,
            runtime_profile_id=runtime_profile_id,
            content_modules_root=content_modules_root,
        ).to_dict()
    except Exception as exc:
        return {
            "schema_version": ENVIRONMENT_MODEL_SCHEMA_VERSION,
            "contract": ENVIRONMENT_MODEL_SCHEMA_VERSION,
            "module_id": mid,
            "load_status": "failed",
            "failure_reason": str(exc),
            "locations": {},
            "objects": {},
            "transitions": [],
        }

    location_model = _as_dict(policy.get("location_model"))
    object_model = _as_dict(policy.get("object_model"))
    locations = _as_dict(location_model.get("locations"))
    objects_raw = _as_dict(object_model.get("objects"))
    default_room = _clean_id(object_model.get("default_placement_room_id"))
    anchor_room = (
        _clean_id(location_model.get("narrative_anchor_area_id"))
        or _clean_id(location_model.get("setting_id"))
        or next(iter(locations.keys()), "")
    )

    objects: dict[str, Any] = {}
    for object_id, row in objects_raw.items():
        oid = _clean_id(object_id)
        if not oid or not isinstance(row, dict):
            continue
        obj = dict(row)
        obj.setdefault("id", oid)
        if not _clean_id(obj.get("placement_room_id")) and default_room:
            obj["placement_room_id"] = default_room
        objects[oid] = _json_safe(obj)

    return {
        "schema_version": ENVIRONMENT_MODEL_SCHEMA_VERSION,
        "contract": ENVIRONMENT_MODEL_SCHEMA_VERSION,
        "module_id": mid,
        "runtime_profile_id": policy.get("runtime_profile_id"),
        "setting_id": location_model.get("setting_id"),
        "anchor_room_id": anchor_room,
        "locations": _json_safe(locations),
        "objects": objects,
        "transitions": _json_safe(_strict_list(location_model.get("transitions"))),
        "global_rules": _json_safe(_as_dict(location_model.get("global_rules"))),
        "content_sources": _json_safe(_strict_list(policy.get("content_sources"))),
        "source_policy_schema_version": policy.get("schema_version"),
    }


def normalize_environment_model(model: dict[str, Any] | None) -> dict[str, Any]:
    src = dict(model) if isinstance(model, dict) else {}
    locations = _as_dict(src.get("locations"))
    objects = _as_dict(src.get("objects"))
    anchor = (
        _clean_id(src.get("anchor_room_id"))
        or _clean_id(src.get("current_room_id"))
        or next(iter(locations.keys()), "")
    )
    out = {
        **src,
        "schema_version": str(src.get("schema_version") or ENVIRONMENT_MODEL_SCHEMA_VERSION),
        "contract": str(src.get("contract") or ENVIRONMENT_MODEL_SCHEMA_VERSION),
        "module_id": _clean_id(src.get("module_id")),
        "anchor_room_id": anchor,
        "locations": _json_safe(locations),
        "objects": _json_safe(objects),
        "transitions": _json_safe(_strict_list(src.get("transitions"))),
        "global_rules": _json_safe(_as_dict(src.get("global_rules"))),
    }
    return out


def _visible_room_ids(*, environment_model: dict[str, Any], current_room_id: str) -> list[str]:
    model = normalize_environment_model(environment_model)
    locations = _as_dict(model.get("locations"))
    current = _clean_id(current_room_id) or _clean_id(model.get("anchor_room_id"))
    visible: list[str] = []
    if current:
        visible.append(current)
    room = _as_dict(locations.get(current))
    visibility = _as_dict(room.get("visibility_from_room"))
    for room_id in _strict_list(visibility.get("can_directly_perceive_room_ids")):
        rid = _clean_id(room_id)
        if rid and rid not in visible:
            visible.append(rid)
    return visible


def _object_room_id(obj: dict[str, Any], fallback_room_id: str) -> str:
    return _clean_id(obj.get("placement_room_id") or obj.get("room_id") or fallback_room_id)


def _visible_object_ids(
    *,
    environment_model: dict[str, Any],
    visible_room_ids: list[str],
    held_object_ids: list[str] | None = None,
) -> list[str]:
    model = normalize_environment_model(environment_model)
    objects = _as_dict(model.get("objects"))
    visible_rooms = {_clean_id(rid) for rid in visible_room_ids if _clean_id(rid)}
    held = {_clean_id(oid) for oid in (held_object_ids or []) if _clean_id(oid)}
    out: list[str] = []
    fallback_room = _clean_id(model.get("anchor_room_id"))
    for object_id, row in objects.items():
        if not isinstance(row, dict):
            continue
        oid = _clean_id(row.get("id") or object_id)
        room_id = _object_room_id(row, fallback_room)
        if oid and (room_id in visible_rooms or oid in held):
            out.append(oid)
    return out


def initial_environment_state(
    *,
    module_id: str,
    environment_model: dict[str, Any] | None = None,
    runtime_projection: dict[str, Any] | None = None,
    actor_lane_context: dict[str, Any] | None = None,
    turn_number: int | None = None,
) -> dict[str, Any]:
    model = normalize_environment_model(environment_model)
    mid = _clean_id(module_id) or _clean_id(model.get("module_id"))
    current_room = _clean_id(model.get("anchor_room_id"))
    visible_rooms = _visible_room_ids(environment_model=model, current_room_id=current_room)
    objects = _as_dict(model.get("objects"))
    actor_locations = {
        actor_id: current_room
        for actor_id in _actor_ids_from_projection(
            runtime_projection=runtime_projection,
            actor_lane_context=actor_lane_context,
        )
        if actor_id and current_room
    }
    prop_states: dict[str, Any] = {}
    for object_id, row in objects.items():
        if not isinstance(row, dict):
            continue
        oid = _clean_id(row.get("id") or object_id)
        if not oid:
            continue
        prop_states[oid] = {
            "object_id": oid,
            "room_id": _object_room_id(row, current_room),
            "status": "present",
            "interaction_state": None,
            "held_by_actor_id": None,
            "last_changed_turn": None,
        }
    salient = _visible_object_ids(environment_model=model, visible_room_ids=visible_rooms)
    return {
        "schema_version": ENVIRONMENT_STATE_SCHEMA_VERSION,
        "contract": ENVIRONMENT_STATE_SCHEMA_VERSION,
        "module_id": mid,
        "current_room_id": current_room or None,
        "current_area": current_room or None,
        "previous_room_id": None,
        "previous_area": None,
        "actor_locations": actor_locations,
        "prop_states": prop_states,
        "visible_room_ids": visible_rooms,
        "salient_object_ids": salient,
        "last_environment_events": [],
        "turn_number": int(turn_number or 0),
        "source": "canonical_environment_initial_state",
    }


def normalize_environment_state(
    state: dict[str, Any] | None,
    *,
    module_id: str,
    environment_model: dict[str, Any] | None = None,
    runtime_projection: dict[str, Any] | None = None,
    actor_lane_context: dict[str, Any] | None = None,
    turn_number: int | None = None,
) -> dict[str, Any]:
    model = normalize_environment_model(environment_model)
    base = initial_environment_state(
        module_id=module_id,
        environment_model=model,
        runtime_projection=runtime_projection,
        actor_lane_context=actor_lane_context,
        turn_number=turn_number,
    )
    src = dict(state) if isinstance(state, dict) else {}
    out = {**base, **_json_safe(src)}
    current = _clean_id(
        out.get("current_room_id")
        or out.get("current_location_id")
        or out.get("current_area")
        or model.get("anchor_room_id")
    )
    out["schema_version"] = str(out.get("schema_version") or ENVIRONMENT_STATE_SCHEMA_VERSION)
    out["contract"] = str(out.get("contract") or ENVIRONMENT_STATE_SCHEMA_VERSION)
    out["module_id"] = _clean_id(out.get("module_id")) or _clean_id(module_id)
    out["current_room_id"] = current or None
    out["current_area"] = current or None
    out["previous_room_id"] = _clean_id(out.get("previous_room_id") or out.get("previous_area")) or None
    out["previous_area"] = out["previous_room_id"]
    actor_locations = _as_dict(out.get("actor_locations"))
    for actor_id in _actor_ids_from_projection(
        runtime_projection=runtime_projection,
        actor_lane_context=actor_lane_context,
    ):
        if actor_id and current:
            actor_locations.setdefault(actor_id, current)
    out["actor_locations"] = _json_safe(actor_locations)
    prop_states = _as_dict(out.get("prop_states"))
    for object_id, row in _as_dict(model.get("objects")).items():
        if not isinstance(row, dict):
            continue
        oid = _clean_id(row.get("id") or object_id)
        if not oid:
            continue
        prop_states.setdefault(
            oid,
            {
                "object_id": oid,
                "room_id": _object_room_id(row, current),
                "status": "present",
                "interaction_state": None,
                "held_by_actor_id": None,
                "last_changed_turn": None,
            },
        )
    out["prop_states"] = _json_safe(prop_states)
    visible_rooms = _visible_room_ids(environment_model=model, current_room_id=current)
    out["visible_room_ids"] = visible_rooms
    held_ids = [
        oid
        for oid, prop in prop_states.items()
        if isinstance(prop, dict) and _clean_id(prop.get("held_by_actor_id"))
    ]
    current_salient = [_clean_id(x) for x in _strict_list(out.get("salient_object_ids")) if _clean_id(x)]
    visible_objects = _visible_object_ids(
        environment_model=model,
        visible_room_ids=visible_rooms,
        held_object_ids=held_ids,
    )
    out["salient_object_ids"] = [oid for oid in current_salient + visible_objects if oid]
    # Preserve order while removing duplicates.
    deduped_salient: list[str] = []
    for oid in out["salient_object_ids"]:
        if oid not in deduped_salient:
            deduped_salient.append(oid)
    out["salient_object_ids"] = deduped_salient[:8]
    out["last_environment_events"] = [
        event
        for event in _strict_list(out.get("last_environment_events"))[-8:]
        if isinstance(event, dict)
    ]
    out["turn_number"] = int(turn_number if turn_number is not None else out.get("turn_number") or 0)
    return _json_safe(out)


def environment_state_to_player_local_context(environment_state: dict[str, Any] | None) -> dict[str, Any]:
    state = _as_dict(environment_state)
    current = _clean_id(state.get("current_room_id") or state.get("current_area"))
    previous = _clean_id(state.get("previous_room_id") or state.get("previous_area"))
    out: dict[str, Any] = {}
    if current:
        out["current_area"] = current
        out["current_location_id"] = current
    if previous:
        out["previous_area"] = previous
        out["previous_location_id"] = previous
    affordances = state.get("available_affordances")
    if isinstance(affordances, list):
        out["available_affordances"] = [str(x) for x in affordances if str(x).strip()]
    return out


def scene_affordance_model_with_environment_state(
    scene_affordance_model: dict[str, Any],
    *,
    environment_state: dict[str, Any] | None,
    environment_model: dict[str, Any] | None = None,
) -> dict[str, Any]:
    model = dict(scene_affordance_model or {})
    state = _as_dict(environment_state)
    current = _clean_id(state.get("current_room_id") or state.get("current_area"))
    if current:
        model["current_area"] = current
    if environment_model:
        model["environment_model"] = normalize_environment_model(environment_model)
    if state:
        model["environment_state"] = _json_safe(state)
    return model


def _environment_action_committable(
    *,
    frame: dict[str, Any],
    affordance: dict[str, Any],
) -> tuple[bool, str, str]:
    """Return whether a resolved player action may mutate environment state."""
    policy = _clean_id(affordance.get("action_commit_policy") or frame.get("action_commit_policy")).lower()
    status = _clean_id(affordance.get("affordance_status") or frame.get("affordance_status")).lower()
    return policy == "commit_action" and status in {"allowed", "allowed_offscreen", "partial"}, policy, status


def _environment_action_target(
    *,
    frame: dict[str, Any],
    affordance: dict[str, Any],
) -> tuple[str, str]:
    """Resolve the action target id and type from frame plus affordance result."""
    resolved_target = _as_dict(frame.get("resolved_target"))
    target_id = _clean_id(
        resolved_target.get("target_id")
        or affordance.get("resolved_target_id")
        or frame.get("resolved_target_id")
    )
    target_type = _clean_id(
        resolved_target.get("target_type")
        or affordance.get("resolved_target_type")
        or frame.get("resolved_target_type")
    ).lower()
    return target_id, target_type


def _environment_action_actor(
    *,
    frame: dict[str, Any],
    actor_lane_context: dict[str, Any] | None,
) -> str:
    """Resolve the actor whose committed action changes environment state."""
    lanes = _as_dict(actor_lane_context)
    return _clean_id(
        frame.get("selected_actor_id")
        or frame.get("actor_id")
        or lanes.get("human_actor_id")
        or lanes.get("selected_player_role")
    )


def _apply_environment_movement(
    *,
    state: dict[str, Any],
    target_id: str,
    transition: dict[str, Any],
    actor_id: str,
) -> tuple[str, str, str]:
    """Apply a room movement and return current, previous, event type."""
    previous = _clean_id(state.get("current_room_id") or state.get("current_area"))
    to_room = _clean_id(transition.get("to_location_id") or transition.get("to_area") or target_id)
    if not to_room:
        return previous, previous, "action"
    state["current_room_id"] = to_room
    state["current_area"] = to_room
    state["previous_room_id"] = previous or None
    state["previous_area"] = previous or None
    if actor_id:
        actor_locations = _as_dict(state.get("actor_locations"))
        actor_locations[actor_id] = to_room
        state["actor_locations"] = actor_locations
    return to_room, previous, "movement"


def _apply_environment_object_interaction(
    *,
    state: dict[str, Any],
    target_id: str,
    verb: str,
    action_kind: str,
    actor_id: str,
    current_room_id: str,
    turn_number: int | None,
) -> str:
    """Apply object state changes and return the resulting event type."""
    prop_states = _as_dict(state.get("prop_states"))
    prop = dict(prop_states.get(target_id) if isinstance(prop_states.get(target_id), dict) else {})
    prop.setdefault("object_id", target_id)
    prop.setdefault("room_id", current_room_id)
    if verb in {"activate", "deactivate", "open", "close", "take", "place"}:
        prop["interaction_state"] = verb
        prop["status"] = "changed"
        prop["last_changed_turn"] = int(turn_number or state.get("turn_number") or 0)
        if verb == "take" and actor_id:
            prop["held_by_actor_id"] = actor_id
        elif verb == "place":
            prop["held_by_actor_id"] = None
            prop["room_id"] = current_room_id
    prop_states[target_id] = prop
    state["prop_states"] = prop_states
    salient = [_clean_id(x) for x in _strict_list(state.get("salient_object_ids")) if _clean_id(x)]
    state["salient_object_ids"] = [target_id] + [oid for oid in salient if oid != target_id]
    if verb in {"look_at", "listen_to"} or action_kind == "perception":
        return "perception"
    return "object_interaction"


def _refresh_environment_visibility(
    *,
    state: dict[str, Any],
    model: dict[str, Any],
    current_room_id: str,
) -> None:
    """Recompute visible rooms and salient objects after a committed action."""
    visible_rooms = _visible_room_ids(environment_model=model, current_room_id=current_room_id)
    held_ids = [
        oid
        for oid, prop in _as_dict(state.get("prop_states")).items()
        if isinstance(prop, dict) and _clean_id(prop.get("held_by_actor_id"))
    ]
    visible_objects = _visible_object_ids(
        environment_model=model,
        visible_room_ids=visible_rooms,
        held_object_ids=held_ids,
    )
    salient = [_clean_id(x) for x in _strict_list(state.get("salient_object_ids")) if _clean_id(x)]
    state["visible_room_ids"] = visible_rooms
    deduped_salient: list[str] = []
    for oid in salient + visible_objects:
        if oid and oid not in deduped_salient:
            deduped_salient.append(oid)
    state["salient_object_ids"] = deduped_salient[:8]


def _append_environment_event(
    *,
    state: dict[str, Any],
    event_type: str,
    verb: str,
    action_kind: str,
    actor_id: str,
    target_id: str,
    target_type: str,
    previous_room_id: str,
    current_room_id: str,
    status: str,
    consequence: dict[str, Any],
    turn_number: int | None,
) -> None:
    """Append the bounded environment event for this committed action."""
    event = {
        "schema_version": ENVIRONMENT_EVENT_SCHEMA_VERSION,
        "event_type": event_type,
        "verb": verb or None,
        "action_kind": action_kind or None,
        "actor_id": actor_id or None,
        "target_id": target_id or None,
        "target_type": target_type or None,
        "from_room_id": previous_room_id or None,
        "to_room_id": current_room_id or None,
        "affordance_status": status or None,
        "consequence_type": consequence.get("consequence_type"),
        "turn_number": int(turn_number or state.get("turn_number") or 0),
    }
    state["last_environment_events"] = (_strict_list(state.get("last_environment_events")) + [event])[-8:]


def apply_action_to_environment_state(
    *,
    environment_state: dict[str, Any] | None,
    environment_model: dict[str, Any] | None,
    player_action_frame: dict[str, Any] | None,
    affordance_resolution: dict[str, Any] | None,
    local_context_transition: dict[str, Any] | None = None,
    narrator_consequence_plan: dict[str, Any] | None = None,
    actor_lane_context: dict[str, Any] | None = None,
    turn_number: int | None = None,
) -> dict[str, Any]:
    model = normalize_environment_model(environment_model)
    frame = _as_dict(player_action_frame)
    aff = _as_dict(affordance_resolution)
    state = normalize_environment_state(
        environment_state,
        module_id=_clean_id(model.get("module_id")) or _clean_id(frame.get("module_id")),
        environment_model=model,
        actor_lane_context=actor_lane_context,
        turn_number=turn_number,
    )
    committable, _, status = _environment_action_committable(frame=frame, affordance=aff)
    if not committable:
        return state

    target_id, target_type = _environment_action_target(frame=frame, affordance=aff)
    verb = _clean_id(frame.get("verb")).lower()
    action_kind = _clean_id(frame.get("action_kind")).lower()
    transition = _as_dict(local_context_transition)
    consequence = _as_dict(narrator_consequence_plan)
    actor_id = _environment_action_actor(
        frame=frame,
        actor_lane_context=actor_lane_context,
    )

    current = _clean_id(state.get("current_room_id") or state.get("current_area"))
    previous = current
    event_type = "action"
    if target_type == "location" and (verb == "move_to" or action_kind == "movement"):
        current, previous, event_type = _apply_environment_movement(
            state=state,
            target_id=target_id,
            transition=transition,
            actor_id=actor_id,
        )
    elif target_type == "object" and target_id:
        event_type = _apply_environment_object_interaction(
            state=state,
            target_id=target_id,
            verb=verb,
            action_kind=action_kind,
            actor_id=actor_id,
            current_room_id=current,
            turn_number=turn_number,
        )

    _refresh_environment_visibility(state=state, model=model, current_room_id=current)
    _append_environment_event(
        state=state,
        event_type=event_type,
        verb=verb,
        action_kind=action_kind,
        actor_id=actor_id,
        target_id=target_id,
        target_type=target_type,
        previous_room_id=previous,
        current_room_id=current,
        status=status,
        consequence=consequence,
        turn_number=turn_number,
    )
    state["turn_number"] = int(turn_number or state.get("turn_number") or 0)
    state["source"] = "committed_action_resolution"
    return normalize_environment_state(
        state,
        module_id=_clean_id(model.get("module_id")),
        environment_model=model,
        actor_lane_context=actor_lane_context,
        turn_number=turn_number,
    )


def build_environment_generation_context(
    *,
    environment_state: dict[str, Any] | None,
    environment_model: dict[str, Any] | None,
) -> dict[str, Any]:
    state = normalize_environment_state(
        environment_state,
        module_id=_clean_id(_as_dict(environment_model).get("module_id")),
        environment_model=environment_model,
    )
    model = normalize_environment_model(environment_model)
    current = _clean_id(state.get("current_room_id"))
    current_room = _as_dict(_as_dict(model.get("locations")).get(current))
    prop_states = _as_dict(state.get("prop_states"))
    salient = [_clean_id(x) for x in _strict_list(state.get("salient_object_ids")) if _clean_id(x)]
    prop_summary: list[dict[str, Any]] = []
    for object_id in salient[:8]:
        prop = _as_dict(prop_states.get(object_id))
        if prop:
            prop_summary.append(
                {
                    "object_id": object_id,
                    "room_id": prop.get("room_id"),
                    "status": prop.get("status"),
                    "interaction_state": prop.get("interaction_state"),
                    "held_by_actor_id": prop.get("held_by_actor_id"),
                }
            )
    return {
        "schema_version": ENVIRONMENT_STATE_SCHEMA_VERSION,
        "contract": "environment_generation_context.v1",
        "current_room_id": current or None,
        "previous_room_id": state.get("previous_room_id"),
        "visible_room_ids": state.get("visible_room_ids") or [],
        "salient_object_ids": salient,
        "available_affordances": current_room.get("available_affordances") or [],
        "privacy": current_room.get("privacy"),
        "visibility_from_room": current_room.get("visibility_from_room") or {},
        "actor_locations": state.get("actor_locations") or {},
        "prop_state_summary": prop_summary,
        "last_environment_events": state.get("last_environment_events") or [],
    }


def build_environment_render_context(
    *,
    environment_state: dict[str, Any] | None,
    environment_model: dict[str, Any] | None,
) -> dict[str, Any]:
    generation_context = build_environment_generation_context(
        environment_state=environment_state,
        environment_model=environment_model,
    )
    return {
        "schema_version": ENVIRONMENT_RENDER_CONTEXT_SCHEMA_VERSION,
        "contract": ENVIRONMENT_RENDER_CONTEXT_SCHEMA_VERSION,
        "player_visible": False,
        **generation_context,
    }


def evaluate_environment_state_contract(
    *,
    environment_state: dict[str, Any] | None,
    module_id: str | None = None,
    environment_model: dict[str, Any] | None = None,
    runtime_projection: dict[str, Any] | None = None,
    actor_lane_context: dict[str, Any] | None = None,
    turn_number: int | None = None,
) -> dict[str, Any]:
    """Evaluate environment-state contract using local normalization only."""
    state_src = _as_dict(environment_state)
    mid = _clean_id(module_id) or _clean_id(state_src.get("module_id"))
    if not mid:
        return {
            "validator_id": "environment_state_contract",
            "available": False,
            "passed": False,
            "blocking": True,
            "proof_level": "local_only",
            "live_or_staging_evidence": False,
            "status": "unavailable",
            "reason": "missing_required_context",
        }

    model = environment_model if isinstance(environment_model, dict) else None
    if model is None and not state_src:
        return {
            "validator_id": "environment_state_contract",
            "available": False,
            "passed": False,
            "blocking": True,
            "proof_level": "local_only",
            "live_or_staging_evidence": False,
            "status": "unavailable",
            "reason": "missing_environment_state",
        }

    try:
        normalized = normalize_environment_state(
            state_src or None,
            module_id=mid,
            environment_model=model,
            runtime_projection=runtime_projection,
            actor_lane_context=actor_lane_context,
            turn_number=turn_number,
        )
    except Exception as exc:
        return {
            "validator_id": "environment_state_contract",
            "available": False,
            "passed": False,
            "blocking": True,
            "proof_level": "local_only",
            "live_or_staging_evidence": False,
            "status": "unavailable",
            "reason": f"environment_state_normalization_failed: {exc}",
        }

    current_room = _clean_id(normalized.get("current_room_id"))
    if not current_room:
        return {
            "validator_id": "environment_state_contract",
            "available": True,
            "passed": False,
            "blocking": True,
            "proof_level": "local_only",
            "live_or_staging_evidence": False,
            "status": "rejected",
            "contract_pass": False,
            "reason": "environment_current_room_missing",
            "failure_codes": ["environment_current_room_missing"],
        }

    return {
        "validator_id": "environment_state_contract",
        "available": True,
        "passed": True,
        "blocking": True,
        "proof_level": "local_only",
        "live_or_staging_evidence": False,
        "status": "approved",
        "contract_pass": True,
        "current_room_id": current_room,
        "schema_version": normalized.get("schema_version"),
    }
