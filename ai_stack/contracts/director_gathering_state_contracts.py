"""Closed-enum contract surface for ``director_gathering_state.v1``.

This module is the PR-C delivery for the NPC Interactivity roadmap. It carries
the per-turn Director-Pause state that gates mandatory-beat consumption when
required actors are not co-present in the gathering.

Authoritative governance:

* :doc:`docs/architecture/components/ai-stack/architecture`
  (defines the contract shape, composition rule, and beat-consumption gate).
* :doc:`docs/architecture/components/ai-stack/architecture`
  (Phase-1 amendment reserves the ``director_gathering_state.v1`` contract).
* :doc:`docs/architecture/components/world-engine/architecture` (composition path
  that the Director state rides on).
* :doc:`docs/implementation_logs/pr_c_director_pause_mode_piv` (PR-C PIV
  artifact).

Vocabulary discipline (ADR-0039 + Phase-1 amendment):

* Closed enums for ``reason``. Semantic capability names only.
* No Pi / Pi-numbered runtime keys.
* No verb / room / actor / locale literal whitelists.
* The ``paused`` decision derives from actor topology and resolver evidence;
  never from verb matching, step-mode switching, or room names.
* ``compute_gathering_state`` is a pure function — no I/O, no mutation,
  no LLM call, no content hardcoding.
"""

from __future__ import annotations

from typing import Any, Final


SCHEMA_VERSION: Final[str] = "director_gathering_state.v1"


PAUSE_REASON_ACTOR_NOT_AT_SCENE: Final[str] = "required_actor_not_at_scene_location"
PAUSE_REASON_PARTICIPATION_BROKEN: Final[str] = "participation_relevance_broken"
PAUSE_REASON_VISIBILITY_LOST: Final[str] = "visibility_audibility_lost"

PAUSE_REASONS: Final[frozenset[str]] = frozenset(
    {
        PAUSE_REASON_ACTOR_NOT_AT_SCENE,
        PAUSE_REASON_PARTICIPATION_BROKEN,
        PAUSE_REASON_VISIBILITY_LOST,
    }
)

PAUSE_SOURCE_RESOLVER_EVIDENCE: Final[str] = "free_player_action_resolution.v1"
PAUSE_SOURCE_TOPOLOGY: Final[str] = "actor_topology_derived"

DIAGNOSTIC_BLOCKER_MISSING_ACTOR_LOCATIONS: Final[str] = "missing_actor_locations"
DIAGNOSTIC_BLOCKER_MISSING_NAMED_CHARACTERS: Final[str] = "missing_named_characters"
DIAGNOSTIC_BLOCKER_MISSING_STEP_SCENE_ID: Final[str] = "missing_step_scene_id"
DIAGNOSTIC_BLOCKER_MISSING_PARTICIPATION_EVIDENCE: Final[str] = "missing_participation_evidence"

PAUSE_SOURCES: Final[frozenset[str]] = frozenset(
    {PAUSE_SOURCE_RESOLVER_EVIDENCE, PAUSE_SOURCE_TOPOLOGY}
)


def _coerce_string(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _named_character_ids(current_step_named_characters: list[str] | None) -> list[str]:
    return (
        [str(c).strip() for c in current_step_named_characters if str(c).strip()]
        if current_step_named_characters
        else []
    )


def _diagnostic_gathering_state(
    *,
    reason: str,
    named_characters: list[str],
    evidence_status: dict[str, bool] | None = None,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "paused": False,
        "missing_actor_ids": [],
        "presence_required_for_step": named_characters,
        "diagnostic_blocker": True,
        "reason": reason,
    }
    if evidence_status is not None:
        result["evidence_status"] = evidence_status
    return result


def _missing_actors_from_presence(
    *,
    named_characters: list[str],
    locations: dict[str, str | None],
    scene_id: str,
) -> tuple[list[str], list[str]]:
    missing_actor_ids: list[str] = []
    reasons: list[str] = []
    for actor_id in named_characters:
        actor_loc = _coerce_string(locations.get(actor_id))
        if actor_loc is None or actor_loc != scene_id:
            if actor_id not in missing_actor_ids:
                missing_actor_ids.append(actor_id)
            if PAUSE_REASON_ACTOR_NOT_AT_SCENE not in reasons:
                reasons.append(PAUSE_REASON_ACTOR_NOT_AT_SCENE)
    return missing_actor_ids, reasons


def _append_subject_pause_reason(
    *,
    missing_actor_ids: list[str],
    reasons: list[str],
    subject: str | None,
    reason: str,
) -> None:
    if subject and subject not in missing_actor_ids:
        if reason not in reasons:
            reasons.append(reason)
        missing_actor_ids.append(subject)
    elif not subject and reason not in reasons:
        reasons.append(reason)


def _apply_participation_pause(
    *,
    missing_actor_ids: list[str],
    reasons: list[str],
    subject: str | None,
    participation_text: str | None,
) -> None:
    if participation_text and participation_text.lower() in (
        "broken",
        "not_participating",
        "disengaged",
        "absent",
    ):
        _append_subject_pause_reason(
            missing_actor_ids=missing_actor_ids,
            reasons=reasons,
            subject=subject,
            reason=PAUSE_REASON_PARTICIPATION_BROKEN,
        )


def _apply_visibility_pause(
    *,
    missing_actor_ids: list[str],
    reasons: list[str],
    subject: str | None,
    visibility_text: str | None,
) -> None:
    if visibility_text and visibility_text.lower() in (
        "not_visible",
        "not_audible",
        "hidden",
        "out_of_sight",
        "inaudible",
    ):
        _append_subject_pause_reason(
            missing_actor_ids=missing_actor_ids,
            reasons=reasons,
            subject=subject,
            reason=PAUSE_REASON_VISIBILITY_LOST,
        )


def _paused_since_turn(
    *,
    previous_state: dict[str, Any],
    current_turn_number: int | None,
) -> int | None:
    if not bool(previous_state.get("paused")):
        return current_turn_number
    prev_since_turn = previous_state.get("since_turn")
    if prev_since_turn is None:
        return current_turn_number
    try:
        return int(prev_since_turn)
    except (TypeError, ValueError):
        return current_turn_number


def _paused_gathering_state(
    *,
    named_characters: list[str],
    scene_id: str,
    missing_actor_ids: list[str],
    reasons: list[str],
    participation_text: str | None,
    visibility_text: str | None,
    current_turn_number: int | None,
    previous_state: dict[str, Any],
) -> dict[str, Any]:
    prev_step_id = _coerce_string(previous_state.get("step_id")) if bool(previous_state.get("paused")) else None
    source = (
        PAUSE_SOURCE_RESOLVER_EVIDENCE
        if participation_text or visibility_text
        else PAUSE_SOURCE_TOPOLOGY
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "paused": True,
        "step_id": prev_step_id or scene_id,
        "missing_actor_ids": missing_actor_ids,
        "since_turn": _paused_since_turn(
            previous_state=previous_state,
            current_turn_number=current_turn_number,
        ),
        "presence_required_for_step": named_characters,
        "reason": reasons[0] if reasons else PAUSE_REASON_ACTOR_NOT_AT_SCENE,
        "source": source,
    }


def compute_gathering_state(
    *,
    actor_locations: dict[str, str | None] | None,
    current_step_named_characters: list[str] | None,
    current_step_scene_id: str | None,
    participation_relevance: str | None = None,
    visibility_audibility: str | None = None,
    subject_actor_id: str | None = None,
    participation_evidence_required: bool = False,
    current_turn_number: int | None = None,
    previous_state: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Compute the pure ``director_gathering_state.v1`` pause snapshot."""
    named_characters = _named_character_ids(current_step_named_characters)
    scene_id = _coerce_string(current_step_scene_id)
    locations = actor_locations if isinstance(actor_locations, dict) else {}
    prev = previous_state if isinstance(previous_state, dict) else {}
    subject = _coerce_string(subject_actor_id)

    if not named_characters:
        return _diagnostic_gathering_state(
            reason=DIAGNOSTIC_BLOCKER_MISSING_NAMED_CHARACTERS,
            named_characters=named_characters,
        )
    if not scene_id:
        return _diagnostic_gathering_state(
            reason=DIAGNOSTIC_BLOCKER_MISSING_STEP_SCENE_ID,
            named_characters=named_characters,
        )
    if actor_locations is None or not isinstance(actor_locations, dict) or not locations:
        return _diagnostic_gathering_state(
            reason=DIAGNOSTIC_BLOCKER_MISSING_ACTOR_LOCATIONS,
            named_characters=named_characters,
        )

    missing_actor_ids, reasons = _missing_actors_from_presence(
        named_characters=named_characters,
        locations=locations,
        scene_id=scene_id,
    )
    participation_text = _coerce_string(participation_relevance)
    visibility_text = _coerce_string(visibility_audibility)
    if participation_evidence_required and (participation_text is None or visibility_text is None):
        return _diagnostic_gathering_state(
            reason=DIAGNOSTIC_BLOCKER_MISSING_PARTICIPATION_EVIDENCE,
            named_characters=named_characters,
            evidence_status={
                "participation_relevance_present": participation_text is not None,
                "visibility_audibility_present": visibility_text is not None,
            },
        )
    _apply_participation_pause(
        missing_actor_ids=missing_actor_ids,
        reasons=reasons,
        subject=subject,
        participation_text=participation_text,
    )
    _apply_visibility_pause(
        missing_actor_ids=missing_actor_ids,
        reasons=reasons,
        subject=subject,
        visibility_text=visibility_text,
    )

    missing_actor_ids.sort()
    paused = len(missing_actor_ids) > 0 or len(reasons) > 0

    if not paused:
        return {
            "schema_version": SCHEMA_VERSION,
            "paused": False,
            "missing_actor_ids": [],
            "presence_required_for_step": named_characters,
        }

    return _paused_gathering_state(
        named_characters=named_characters,
        scene_id=scene_id,
        missing_actor_ids=missing_actor_ids,
        reasons=reasons,
        participation_text=participation_text,
        visibility_text=visibility_text,
        current_turn_number=current_turn_number,
        previous_state=prev,
    )


def should_suppress_mandatory_beat_consumption(
    director_gathering_state: dict[str, Any] | None,
) -> bool:
    """Return True when mandatory-beat consumption must be suppressed.

    This is the beat-consumption gate described in ADR-0061 §5. When the
    Director-Pause is active, mandatory beats must not be consumed, but the
    player remains free and narrator local consequences are not blocked.
    """
    if not isinstance(director_gathering_state, dict):
        return False
    return bool(director_gathering_state.get("paused"))


def gathering_pause_is_transition(
    *,
    previous_state: dict[str, Any] | None,
    current_state: dict[str, Any] | None,
) -> str | None:
    """Detect a pause transition and return its direction.

    Returns:
        ``"entered"`` for ``paused: false → true``.
        ``"cleared"`` for ``paused: true → false``.
        ``None`` when no transition occurred.
    """
    prev = previous_state if isinstance(previous_state, dict) else {}
    curr = current_state if isinstance(current_state, dict) else {}
    was_paused = bool(prev.get("paused"))
    is_paused = bool(curr.get("paused"))
    if not was_paused and is_paused:
        return "entered"
    if was_paused and not is_paused:
        return "cleared"
    return None


__all__ = [
    "SCHEMA_VERSION",
    "PAUSE_REASON_ACTOR_NOT_AT_SCENE",
    "PAUSE_REASON_PARTICIPATION_BROKEN",
    "PAUSE_REASON_VISIBILITY_LOST",
    "PAUSE_REASONS",
    "PAUSE_SOURCE_RESOLVER_EVIDENCE",
    "PAUSE_SOURCE_TOPOLOGY",
    "PAUSE_SOURCES",
    "DIAGNOSTIC_BLOCKER_MISSING_ACTOR_LOCATIONS",
    "DIAGNOSTIC_BLOCKER_MISSING_NAMED_CHARACTERS",
    "DIAGNOSTIC_BLOCKER_MISSING_STEP_SCENE_ID",
    "DIAGNOSTIC_BLOCKER_MISSING_PARTICIPATION_EVIDENCE",
    "compute_gathering_state",
    "should_suppress_mandatory_beat_consumption",
    "gathering_pause_is_transition",
]
