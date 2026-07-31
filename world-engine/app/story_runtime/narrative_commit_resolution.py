"""Phased resolution for ``resolve_narrative_commit`` (DS-012 split — no Pydantic models here)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class NarrativeCommitWork:
    """Mutable working state for one resolution pass."""

    committed_scene_id: str
    allowed: bool
    commit_reason_code: str
    situation_status: str
    authoritative_reason: str
    committed_consequences: list[str] = field(default_factory=list)


def prepare_open_pressures(interpreted_input: dict[str, Any]) -> list[str]:
    ambiguity = interpreted_input.get("ambiguity")
    if isinstance(ambiguity, str) and ambiguity.strip():
        return [f"interpretation_ambiguity:{ambiguity.strip()}"]
    return []


def build_base_consequences(*, kind: Any, model_raw: str | None) -> list[str]:
    from app.story_runtime.commit_models import _interpretation_kind_tag

    consequences: list[str] = [f"interpretation_kind:{_interpretation_kind_tag(kind)}"]
    if model_raw is not None:
        consequences.append(f"model_proposal_considered:{model_raw}")
    return consequences


def eval_core_transition_rules(
    *,
    proposed_scene_id: str | None,
    prior_scene_id: str,
    known_scene_ids: set[str],
    has_transition_rules: bool,
    transition_map: dict[str, set[str]],
    model_raw: str | None,
    consequences: list[str],
) -> NarrativeCommitWork:
    """Apply proposal / transition / legality branches (mirrors former ``resolve_narrative_commit`` core)."""
    committed_scene_id = prior_scene_id
    allowed = False
    code = "no_scene_proposal"
    situation = "continue"
    auth_reason = "No scene change was proposed; the session remains in the current scene."

    if not proposed_scene_id:
        if model_raw is not None and known_scene_ids and model_raw not in known_scene_ids:
            auth_reason = (
                "The model proposed a scene that is not in the runtime projection; "
                "no scene candidate was selected for progression."
            )
        else:
            auth_reason = "No scene change was proposed; the session remains in the current scene."
        code = "no_scene_proposal"
        situation = "continue"
    elif proposed_scene_id == prior_scene_id:
        code = "already_in_scene"
        situation = "continue"
        auth_reason = "A scene was proposed but it matches the current scene; no transition applies."
        consequences.append(f"scene_continue:{prior_scene_id}")
    elif known_scene_ids and proposed_scene_id not in known_scene_ids:
        # Situationally impossible: target scene does not exist in projection.
        code = "unknown_target_scene"
        situation = "blocked"
        auth_reason = (
            "The proposed target scene is unknown to this runtime projection; "
            "progression is blocked as situatively impossible."
        )
        consequences.append("proposal_blocked:unknown_target_scene")
    elif not has_transition_rules:
        # Free role-play: missing transition card must not freeze the beat (E9 / D31).
        code = "transition_hints_missing"
        situation = "partial"
        allowed = True
        auth_reason = (
            "Transition hints are missing; the action is accepted as a partial state "
            "change without a scene transition."
        )
        consequences.append("proposal_partial:transition_hints_missing")
        consequences.append(f"scene_continue:{prior_scene_id}")
    else:
        allowed_targets = transition_map.get(prior_scene_id, set())
        if proposed_scene_id not in allowed_targets:
            # Not on the authored transition card → partial, not blocked (E9).
            code = "illegal_transition_not_allowed"
            situation = "partial"
            allowed = True
            auth_reason = (
                "The proposed scene transition is not on the authored transition map; "
                "the action is accepted as a partial state change without changing scene."
            )
            consequences.append("proposal_partial:off_transition_map")
            consequences.append(f"scene_continue:{prior_scene_id}")
        else:
            committed_scene_id = proposed_scene_id
            allowed = True
            code = "legal_transition_committed"
            situation = "transitioned"
            auth_reason = f"Legal transition committed from {prior_scene_id!r} to {committed_scene_id!r}."
            consequences.append(f"scene_transition:{prior_scene_id}->{committed_scene_id}")

    return NarrativeCommitWork(
        committed_scene_id=committed_scene_id,
        allowed=allowed,
        commit_reason_code=code,
        situation_status=situation,
        authoritative_reason=auth_reason,
        committed_consequences=consequences,
    )


def overlay_terminal_scene(
    work: NarrativeCommitWork,
    *,
    terminal_ids: set[str],
) -> None:
    """Adjust situation / reason when the committed scene is terminal (non-blocked only)."""
    at_terminal_scene = work.committed_scene_id in terminal_ids
    if at_terminal_scene and work.situation_status not in {"blocked", "prevented"}:
        work.situation_status = "terminal"
        if work.commit_reason_code == "legal_transition_committed":
            work.authoritative_reason = (
                f"Legal transition committed to terminal scene {work.committed_scene_id!r}."
            )
        elif work.commit_reason_code == "already_in_scene":
            work.authoritative_reason = f"The session remains on terminal scene {work.committed_scene_id!r}."
        elif work.commit_reason_code == "no_scene_proposal":
            work.authoritative_reason = (
                f"No scene change proposed; session remains on terminal scene {work.committed_scene_id!r}."
            )
        else:
            work.authoritative_reason = f"The session is at terminal scene {work.committed_scene_id!r}."


def build_interpretation_summary(
    *,
    interpreted_input: dict[str, Any],
    model_raw: str | None,
    selected_source: str | None,
    prior_scene_id: str,
    committed_scene_id: str,
    situation_status: str,
) -> dict[str, Any]:
    kind = interpreted_input.get("kind")
    conf = interpreted_input.get("confidence")
    ambiguity = interpreted_input.get("ambiguity")
    model_considered = model_raw is not None
    state_changed = committed_scene_id != prior_scene_id
    interpretation_influenced = selected_source is not None or str(kind or "").lower() == "explicit_command"
    local_continuation_only = (not state_changed) and situation_status == "continue"

    return {
        "interpreted_kind": kind,
        "interpretation_confidence": conf,
        "interpretation_ambiguity": ambiguity,
        "interpretation_influenced_progression": interpretation_influenced,
        "model_proposal_considered": model_considered,
        "proposal_changed_committed_state": state_changed,
        "local_narrative_continuation_only": local_continuation_only,
        "note": (
            "Bounded interpretation-to-progression linkage only; not a full canonical world-state delta."
        ),
    }
