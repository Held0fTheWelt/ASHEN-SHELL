"""Operator-facing turn history and agency diagnostics service.

Provides dashboards and surfaces that let operators see where actor behavior
survived or degraded through the turn pipeline. Used by the admin UI and
diagnostics endpoints to help operators diagnose WS-1..4 behavior.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any


def build_turn_history_summary_for_session(
    diagnostics: list[dict[str, Any]],
    limit: int = 100,
) -> dict[str, Any]:
    """Build operator-visible turn history summary from session diagnostics.

    Extracts actor-survival telemetry from each turn event and formats it for
    operator dashboards showing where behavior survived/degraded.
    """
    rows = []
    for event in diagnostics[-limit:]:
        if not isinstance(event, dict):
            continue
        row = _format_turn_history_row(event)
        if row:
            rows.append(row)

    return {
        "turn_history_version": "1.0",
        "total_turns": len(rows),
        "rows": rows,
        "agency_statistics": _compute_agency_statistics(rows),
        "degradation_summary": _compute_degradation_summary(rows),
    }


def _format_turn_history_row(event: dict[str, Any]) -> dict[str, Any] | None:
    """Format a single turn event into an operator dashboard row."""
    if not event.get("turn_number"):
        return None

    telemetry = event.get("actor_survival_telemetry") or {}
    actor_survival = telemetry.get("actor_survival") or {}
    hints = telemetry.get("operator_diagnostic_hints") or {}
    bundle = event.get("visible_output_bundle") or {}
    routing = event.get("routing") or {}

    return {
        "turn_number": event.get("turn_number"),
        "turn_kind": event.get("turn_kind"),
        "turn_timestamp": event.get("turn_timestamp_iso"),
        "trace_id": event.get("trace_id"),
        # Actor intent
        "configured_responder": actor_survival.get("configured_primary_responder"),
        "configured_scene_function": actor_survival.get("configured_scene_function"),
        # Pipeline survival
        "generation_ok": actor_survival.get("generation_phase", {}).get("generation_attempted"),
        "fallback_used": actor_survival.get("generation_phase", {}).get("generation_fallback_used"),
        "validation_ok": actor_survival.get("validation_phase", {}).get("validation_approved"),
        "commit_applied": actor_survival.get("commit_phase", {}).get("commit_applied"),
        "spoken_lines_generated": actor_survival.get("generation_phase", {}).get("spoken_lines_generated", 0),
        "spoken_lines_rendered": actor_survival.get("render_phase", {}).get("spoken_lines_rendered", 0),
        # Degradation
        "degradation_markers": actor_survival.get("degradation_markers", {}),
        "agency_level": hints.get("actor_agency_level"),
        "diagnostic_hints": hints.get("hints", []),
        # Rendering
        "output_type": "actor_agency" if bundle.get("responder_trace") else "narration_only",
        "routing_reason": routing.get("route_reason", "unknown"),
    }


def _compute_agency_statistics(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Compute aggregate statistics on actor agency across the turn history."""
    if not rows:
        return {}

    total = len(rows)
    full_agency = sum(1 for r in rows if r.get("agency_level") == "full_actor_agency")
    generation_failed = sum(1 for r in rows if r.get("agency_level") == "generation_failed")
    fallback_active = sum(1 for r in rows if r.get("agency_level") == "fallback_active")
    validation_constrained = sum(1 for r in rows if r.get("agency_level") == "validation_constrained")
    commit_blocked = sum(1 for r in rows if r.get("agency_level") == "commit_blocked")
    narration_only = sum(1 for r in rows if r.get("agency_level") == "narration_only")

    avg_spoken_generated = sum(r.get("spoken_lines_generated", 0) for r in rows) / total if total else 0
    avg_spoken_rendered = sum(r.get("spoken_lines_rendered", 0) for r in rows) / total if total else 0

    return {
        "total_turns": total,
        "full_actor_agency_turns": full_agency,
        "full_agency_percent": round(100 * full_agency / total, 1) if total else 0,
        "generation_failed_turns": generation_failed,
        "fallback_active_turns": fallback_active,
        "validation_constrained_turns": validation_constrained,
        "commit_blocked_turns": commit_blocked,
        "narration_only_turns": narration_only,
        "avg_spoken_lines_generated": round(avg_spoken_generated, 2),
        "avg_spoken_lines_rendered": round(avg_spoken_rendered, 2),
    }


def _compute_degradation_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Identify and summarize degradation patterns in the turn history."""
    degradations = []
    degradation_counts = {}

    for row in rows:
        markers = row.get("degradation_markers") or {}
        if any(markers.values()):
            for key, val in markers.items():
                if val:
                    degradation_counts[key] = degradation_counts.get(key, 0) + 1
            hints = row.get("diagnostic_hints", [])
            if hints:
                degradations.append(
                    {
                        "turn_number": row.get("turn_number"),
                        "hints": hints,
                        "agency_level": row.get("agency_level"),
                    }
                )

    return {
        "total_degraded_turns": len(degradations),
        "degradation_types": degradation_counts,
        "most_recent_degradations": degradations[-5:] if degradations else [],
    }


def operator_diagnostics_surface(
    session_diagnostics: list[dict[str, Any]],
    fallback_marker_check: bool = True,
) -> dict[str, Any]:
    """Build full operator diagnostic surface for agency troubleshooting.

    Surfaces actor-survival telemetry, degradation patterns, and hints so
    operators can identify where behavior survived or failed through the
    pipeline.
    """
    history_summary = build_turn_history_summary_for_session(session_diagnostics)
    rows = history_summary.get("rows", [])

    # Identify fallback/degraded turns for highlight
    fallback_turns = [r for r in rows if r.get("fallback_used")]
    failed_turns = [r for r in rows if not r.get("generation_ok")]
    failed_validation = [r for r in rows if not r.get("validation_ok")]
    failed_commit = [r for r in rows if not r.get("commit_applied")]

    return {
        "diagnostics_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "turn_history": history_summary,
        "critical_issues": {
            "fallback_turns": len(fallback_turns),
            "generation_failures": len(failed_turns),
            "validation_failures": len(failed_validation),
            "commit_failures": len(failed_commit),
        },
        "operator_actions": _suggest_operator_actions(
            fallback_turns, failed_turns, failed_validation, failed_commit
        ),
        "documented_capabilities": {
            "full_actor_agency": "Responder speaks and acts; output generated, validated, committed, rendered.",
            "fallback_active": "Generation used fallback model; agency may be reduced.",
            "validation_constrained": "Validation restricted actor behavior; original intent was constrained.",
            "commit_blocked": "Turn was not committed; story state may not reflect intent.",
            "narration_only": "No spoken lines in output; responder may have been silent or narrator-only.",
            "generation_failed": "Generation failed entirely; no actor output available.",
        },
    }


def _suggest_operator_actions(
    fallback_turns: list[dict[str, Any]],
    failed_turns: list[dict[str, Any]],
    failed_validation: list[dict[str, Any]],
    failed_commit: list[dict[str, Any]],
) -> list[str]:
    """Suggest operator actions based on observed degradation patterns."""
    actions = []

    if failed_turns:
        actions.append(
            f"⚠️ Generation failed on {len(failed_turns)} turns. "
            "Check model availability and routing configuration."
        )

    if fallback_turns:
        actions.append(
            f"⚠️ {len(fallback_turns)} turns used fallback model. "
            "Primary model may be unavailable; check provider health."
        )

    if failed_validation:
        actions.append(
            f"⚠️ {len(failed_validation)} turns failed validation. "
            "Actor legality or continuity constraints may be too strict."
        )

    if failed_commit:
        actions.append(
            f"⚠️ {len(failed_commit)} turns failed commit. "
            "Story state or transaction issues; check world-engine logs."
        )

    if not (failed_turns or fallback_turns or failed_validation or failed_commit):
        actions.append("✅ All turns completed with full actor agency.")

    return actions


__all__ = [
    "build_turn_history_summary_for_session",
    "operator_diagnostics_surface",
]
