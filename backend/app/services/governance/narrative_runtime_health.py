"""Runtime health rollup helpers for narrative governance."""

from __future__ import annotations

from datetime import datetime
import json

from app.models import NarrativeRuntimeHealthEvent, NarrativeRuntimeHealthRollup, SiteSetting
from app.models.world_engine.narrative_enums import NarrativeEventType


def build_runtime_health_event(
    *,
    event_id: str,
    module_id: str,
    event_type: str,
    severity: str,
    scene_id: str | None,
    turn_number: int | None,
    failure_types: list[str],
    payload: dict[str, object],
    occurred_at: datetime,
) -> NarrativeRuntimeHealthEvent:
    return NarrativeRuntimeHealthEvent(
        event_id=event_id,
        module_id=module_id,
        scene_id=scene_id,
        turn_number=turn_number,
        event_type=event_type,
        severity=severity,
        failure_types_json=failure_types,
        payload_json=payload,
        occurred_at=occurred_at,
    )


def runtime_health_counts(module_id: str, window_start: datetime) -> dict[str, int]:
    base_query = NarrativeRuntimeHealthEvent.query.filter(
        NarrativeRuntimeHealthEvent.module_id == module_id,
        NarrativeRuntimeHealthEvent.occurred_at >= window_start,
    )
    fallback = base_query.filter(
        NarrativeRuntimeHealthEvent.event_type == NarrativeEventType.SAFE_FALLBACK_USED.value
    ).count()
    retry = base_query.filter(
        NarrativeRuntimeHealthEvent.event_type == NarrativeEventType.CORRECTIVE_RETRY_USED.value
    ).count()
    return {"total": base_query.count(), "fallback": fallback, "retry": retry}


def build_runtime_health_rollup(
    *,
    module_id: str,
    window_start: datetime,
    window_end: datetime,
    counts: dict[str, int],
    failure_types: list[str],
) -> NarrativeRuntimeHealthRollup:
    total = counts["total"]
    fallback = counts["fallback"]
    retry = counts["retry"]
    success = max(total - fallback - retry, 0)
    return NarrativeRuntimeHealthRollup(
        module_id=module_id,
        window_key="last_hour",
        window_start=window_start,
        window_end=window_end,
        total_turns=total,
        first_pass_success_rate=(success / total) if total else 0.0,
        corrective_retry_rate=(retry / total) if total else 0.0,
        safe_fallback_rate=(fallback / total) if total else 0.0,
        top_failure_types_json=failure_types[:5],
        created_at=window_end,
    )


def fallback_alert_settings() -> tuple[bool, int]:
    config: dict[str, object] = {}
    row_cfg = SiteSetting.query.filter_by(key="narrative_runtime_config").first()
    if row_cfg and row_cfg.value:
        try:
            parsed = json.loads(row_cfg.value)
            if isinstance(parsed, dict):
                config = parsed
        except json.JSONDecodeError:
            config = {}
    fallback_cfg = config.get("fallback") if isinstance(config.get("fallback"), dict) else {}
    return (
        bool(fallback_cfg.get("alert_on_frequent_fallbacks", True)),
        int(fallback_cfg.get("fallback_alert_threshold", 5) or 5),
    )


def should_emit_fallback_threshold_alert(*, event_type: str, fallback_count: int, threshold: int, enabled: bool) -> bool:
    return (
        enabled
        and fallback_count >= threshold
        and event_type == NarrativeEventType.SAFE_FALLBACK_USED.value
    )
