"""Section builders for committed dramatic-context summaries."""
from __future__ import annotations

from ._deps import *
from .prior_narrative_context import _compact_context_list, _compact_context_str


def _dict_field(source: dict[str, Any], key: str, fallback: Any = None) -> dict[str, Any]:
    value = source.get(key)
    if isinstance(value, dict):
        return value
    return fallback if isinstance(fallback, dict) else {}


def _validation_status(
    planner: dict[str, Any],
    key: str,
    fallback: dict[str, Any] | None = None,
) -> Any:
    value = planner.get(key)
    if isinstance(value, dict):
        return value.get("status")
    return (fallback or {}).get("validation_status")


def responder_context(planner: dict[str, Any], base: dict[str, Any]) -> dict[str, Any]:
    return {
        "responder_id": planner.get("responder_id")
        or planner.get("primary_responder_id")
        or base.get("responder_id"),
        "responder_scope": _compact_context_list(
            planner.get("responder_scope") or base.get("responder_scope")
        ),
        "secondary_responder_ids": _compact_context_list(planner.get("secondary_responder_ids")),
    }


def pacing_context(planner: dict[str, Any], base: dict[str, Any]) -> dict[str, Any]:
    return {
        "pacing_mode": planner.get("pacing_mode") or base.get("pacing_mode"),
        "silence_mode": planner.get("silence_mode") or base.get("silence_mode"),
    }


def scene_energy_context(planner: dict[str, Any], base: dict[str, Any]) -> dict[str, Any]:
    return {
        "target": _dict_field(planner, "scene_energy_target", base.get("target") or {}),
        "transition": _dict_field(planner, "scene_energy_transition", base.get("transition") or {}),
        "validation_status": _validation_status(planner, "scene_energy_validation", base),
    }


def state_target_context(
    planner: dict[str, Any],
    stem: str,
    base: dict[str, Any] | None = None,
) -> dict[str, Any]:
    fallback = base or {}
    return {
        "state": _dict_field(planner, f"{stem}_state", fallback.get("state") or {}),
        "target": _dict_field(planner, f"{stem}_target", fallback.get("target") or {}),
        "validation_status": _validation_status(planner, f"{stem}_validation", fallback),
    }


def scene_assessment_context(scene_assessment: dict[str, Any], base: dict[str, Any]) -> dict[str, Any]:
    return {
        "pressure_state": scene_assessment.get("pressure_state") or base.get("pressure_state"),
        "thread_pressure_state": scene_assessment.get("thread_pressure_state")
        or base.get("thread_pressure_state"),
        "assessment_summary": _compact_context_str(
            scene_assessment.get("assessment_summary") or base.get("assessment_summary")
        ),
    }


def social_state_context(social_summary: dict[str, Any]) -> dict[str, Any]:
    return {
        "fingerprint": social_summary.get("fingerprint"),
        "social_risk_band": social_summary.get("social_risk_band"),
        "responder_asymmetry_code": social_summary.get("responder_asymmetry_code"),
        "social_continuity_status": social_summary.get("social_continuity_status"),
        "prior_social_state_fingerprint": social_summary.get("prior_social_state_fingerprint"),
    }


def dramatic_outcome_context(planner: dict[str, Any]) -> dict[str, Any]:
    return {
        "social_outcome": planner.get("social_outcome"),
        "dramatic_direction": planner.get("dramatic_direction"),
        "continuity_classes": _compact_context_list(
            [
                item.get("class") or item.get("continuity_class")
                for item in (planner.get("continuity_impacts") or [])
                if isinstance(item, dict)
            ]
        ),
        "spoken_line_count": planner.get("spoken_line_count"),
        "action_line_count": planner.get("action_line_count"),
        "initiative_summary": planner.get("initiative_summary")
        if isinstance(planner.get("initiative_summary"), dict)
        else {},
        "last_actor_outcome_summary": planner.get("last_actor_outcome_summary"),
    }


def beat_context(beat: dict[str, Any]) -> dict[str, Any]:
    return {
        "beat_id": beat.get("beat_id"),
        "beat_slot": beat.get("beat_slot"),
        "advanced": beat.get("advanced"),
        "advancement_reason": beat.get("advancement_reason"),
        "pressure_state": beat.get("pressure_state"),
    }


def narrative_thread_context(thread_metrics: dict[str, Any]) -> dict[str, Any]:
    return {
        "thread_count": thread_metrics.get("thread_count", 0),
        "dominant_thread_kind": thread_metrics.get("dominant_thread_kind"),
        "thread_pressure_level": thread_metrics.get("thread_pressure_level", 0),
    }


def retrieval_context(retrieval: dict[str, Any], continuity_query: dict[str, Any]) -> dict[str, Any]:
    return {
        "continuity_query_attached": bool(continuity_query.get("attached")),
        "continuity_query_sources": _compact_context_list(continuity_query.get("sources")),
        "retrieval_status": retrieval.get("status"),
        "retrieval_route": retrieval.get("retrieval_route"),
    }


__all__ = [
    "beat_context",
    "dramatic_outcome_context",
    "narrative_thread_context",
    "pacing_context",
    "responder_context",
    "retrieval_context",
    "scene_assessment_context",
    "scene_energy_context",
    "social_state_context",
    "state_target_context",
]
