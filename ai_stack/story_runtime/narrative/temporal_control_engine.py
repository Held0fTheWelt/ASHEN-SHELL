"""Temporal-control derivation and structured validation."""

from __future__ import annotations

from ai_stack.story_runtime.narrative.normalization import as_list as _as_list, bounded_int as _bounded_int, clean_str_list as _clean_str_list, clean_text as _clean_text
from typing import Any

from ai_stack.contracts.temporal_control_contracts import (
    TEMPORAL_CONTROL_FAILURE_BRANCH_STATE_ADOPTION,
    TEMPORAL_CONTROL_FAILURE_CODES,
    TEMPORAL_CONTROL_FAILURE_HISTORY_REWRITE_ATTEMPT,
    TEMPORAL_CONTROL_FAILURE_MISSING_REQUIRED_EVENT,
    TEMPORAL_CONTROL_FAILURE_OPERATION_NOT_ALLOWED,
    TEMPORAL_CONTROL_FAILURE_TARGET_MISMATCH,
    TEMPORAL_CONTROL_FAILURE_UNBOUNDED_JUMP,
    TEMPORAL_CONTROL_FAILURE_UNCOMMITTED_SOURCE,
    TEMPORAL_CONTROL_FAILURE_UNSELECTED_EVENT,
    TEMPORAL_CONTROL_OPERATIONS,
    TEMPORAL_CONTROL_POLICY_VERSION,
    TEMPORAL_CONTROL_SCHEMA_VERSION,
    TemporalControlEvidenceRef,
    TemporalControlState,
    TemporalControlTarget,
    TemporalControlValidation,
    temporal_control_policy_from_module_runtime,
    normalize_temporal_control_policy,
)


def _evidence(source: str, field: str, value: Any) -> TemporalControlEvidenceRef:
    return TemporalControlEvidenceRef(source=source, field=field, value=value)


def _prior_state(
    prior_temporal_control_state: dict[str, Any] | None,
    prior_planner_truth: dict[str, Any] | None,
) -> dict[str, Any]:
    if isinstance(prior_temporal_control_state, dict) and prior_temporal_control_state:
        return prior_temporal_control_state
    prior = prior_planner_truth if isinstance(prior_planner_truth, dict) else {}
    for key in ("temporal_control_state", "temporal_control"):
        value = prior.get(key)
        if isinstance(value, dict) and value:
            return value
    return {}


def _operation_from_prior(prior: dict[str, Any]) -> str | None:
    op = _clean_text(prior.get("current_operation") or prior.get("operation"))
    return op if op in TEMPORAL_CONTROL_OPERATIONS else None


def _cascade_refs(
    prior_consequence_cascade_state: dict[str, Any] | None,
    *,
    max_items: int,
) -> tuple[list[str], list[str], list[TemporalControlEvidenceRef]]:
    state = (
        prior_consequence_cascade_state
        if isinstance(prior_consequence_cascade_state, dict)
        else {}
    )
    items = state.get("items") if isinstance(state.get("items"), list) else []
    turn_ids: list[str] = []
    consequence_ids: list[str] = []
    evidence: list[TemporalControlEvidenceRef] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        turn_id = _clean_text(item.get("source_turn_id"))
        consequence_id = _clean_text(item.get("consequence_id"))
        if turn_id and turn_id not in turn_ids:
            turn_ids.append(turn_id)
        if consequence_id and consequence_id not in consequence_ids:
            consequence_ids.append(consequence_id)
        if turn_id or consequence_id:
            evidence.append(
                _evidence(
                    "prior_consequence_cascade_state",
                    "items",
                    {
                        "source_turn_id": turn_id or None,
                        "source_turn_number": item.get("source_turn_number"),
                        "consequence_id": consequence_id or None,
                        "continuity_class": item.get("continuity_class"),
                        "status": item.get("status"),
                    },
                )
            )
        if len(turn_ids) >= max_items and len(consequence_ids) >= max_items:
            break
    return turn_ids[:max_items], consequence_ids[:max_items], evidence[:max_items]


def _callback_refs(
    prior_callback_web_state: dict[str, Any] | None,
    *,
    max_items: int,
) -> tuple[list[str], list[TemporalControlEvidenceRef]]:
    state = prior_callback_web_state if isinstance(prior_callback_web_state, dict) else {}
    turn_ids: list[str] = []
    evidence: list[TemporalControlEvidenceRef] = []
    for key in ("selected_source_turn_ids", "source_turn_ids", "turn_ids"):
        for turn_id in _clean_str_list(state.get(key)):
            if turn_id not in turn_ids:
                turn_ids.append(turn_id)
        if turn_ids:
            evidence.append(_evidence("prior_callback_web_state", key, turn_ids[:max_items]))
            break
    return turn_ids[:max_items], evidence[:max_items]


def _allowed_operation(operation: str, allowed_operations: list[str]) -> str:
    if operation in allowed_operations:
        return operation
    if "resume_present" in allowed_operations:
        return "resume_present"
    return allowed_operations[0] if allowed_operations else "resume_present"


def _temporal_policy_fields(policy: dict[str, Any]) -> tuple[list[str], int, int]:
    allowed_operations = [
        op for op in _clean_str_list(policy.get("allowed_operations")) if op in TEMPORAL_CONTROL_OPERATIONS
    ] or ["resume_present"]
    max_recalled = _bounded_int(policy.get("max_recalled_turns"), 3, minimum=0, maximum=12)
    max_elapsed = _bounded_int(policy.get("max_elapsed_turns"), 4, minimum=0, maximum=24)
    return allowed_operations, max_recalled, max_elapsed


def _temporal_signal_fields(
    *,
    scene_plan_record: dict[str, Any] | None,
    scene_energy_target: dict[str, Any] | None,
    pacing_rhythm_target: dict[str, Any] | None,
    semantic_move_record: dict[str, Any] | None,
) -> dict[str, str]:
    plan = scene_plan_record if isinstance(scene_plan_record, dict) else {}
    energy = scene_energy_target if isinstance(scene_energy_target, dict) else {}
    rhythm = pacing_rhythm_target if isinstance(pacing_rhythm_target, dict) else {}
    semantic = semantic_move_record if isinstance(semantic_move_record, dict) else {}
    return {
        "scene_function": _clean_text(plan.get("selected_scene_function")),
        "transition": _clean_text(energy.get("target_transition")),
        "cadence": _clean_text(rhythm.get("cadence")),
        "move_family": _clean_text(
            semantic.get("move_type")
            or semantic.get("social_move_family")
            or semantic.get("player_input_kind")
        ),
    }


def _temporal_memory_refs(
    *,
    prior_consequence_cascade_state: dict[str, Any] | None,
    prior_callback_web_state: dict[str, Any] | None,
    max_recalled: int,
) -> tuple[list[str], list[str], list[TemporalControlEvidenceRef], list[TemporalControlEvidenceRef]]:
    cascade_turn_ids, cascade_consequence_ids, cascade_evidence = _cascade_refs(
        prior_consequence_cascade_state,
        max_items=max_recalled,
    )
    callback_turn_ids, callback_evidence = _callback_refs(
        prior_callback_web_state,
        max_items=max_recalled,
    )
    recalled_turn_ids = list(dict.fromkeys(cascade_turn_ids + callback_turn_ids))[:max_recalled]
    recalled_consequence_ids = cascade_consequence_ids[:max_recalled]
    return recalled_turn_ids, recalled_consequence_ids, cascade_evidence, callback_evidence


def _temporal_recall_requested(signals: dict[str, str], recalled_turn_ids: list[str]) -> bool:
    return bool(recalled_turn_ids) and (
        signals["scene_function"] in {"redirect_blame", "probe_motive", "reveal_surface", "repair_or_stabilize"}
        or signals["move_family"] in {"question", "probe", "challenge", "accuse", "memory_probe"}
    )


def _temporal_hold_evidence(signals: dict[str, str]) -> list[TemporalControlEvidenceRef]:
    evidence: list[TemporalControlEvidenceRef] = []
    if signals["cadence"]:
        evidence.append(_evidence("pacing_rhythm_target", "cadence", signals["cadence"]))
    if signals["transition"]:
        evidence.append(_evidence("scene_energy_target", "target_transition", signals["transition"]))
    return evidence


def _select_temporal_operation(
    *,
    signals: dict[str, str],
    recalled_turn_ids: list[str],
    cascade_evidence: list[TemporalControlEvidenceRef],
    callback_evidence: list[TemporalControlEvidenceRef],
) -> tuple[str, list[str], list[TemporalControlEvidenceRef]]:
    if signals["scene_function"] in {"scene_pivot"}:
        return (
            "summarize_gap",
            ["temporal_control_scene_pivot_gap"],
            [_evidence("scene_plan_record", "selected_scene_function", signals["scene_function"])],
        )
    if signals["transition"] in {"pivot"}:
        return (
            "summarize_gap",
            ["temporal_control_energy_pivot_gap"],
            [_evidence("scene_energy_target", "target_transition", signals["transition"])],
        )
    if signals["transition"] in {"release", "deescalate"}:
        return (
            "advance_elapsed_time",
            ["temporal_control_energy_release_elapsed"],
            [_evidence("scene_energy_target", "target_transition", signals["transition"])],
        )
    if _temporal_recall_requested(signals, recalled_turn_ids):
        return (
            "recall_committed_past",
            ["temporal_control_recall_committed_consequence"],
            list(cascade_evidence or callback_evidence),
        )
    if signals["cadence"] in {"breathe", "hold"} or signals["transition"] == "hold":
        return (
            "hold_current_moment",
            ["temporal_control_hold_current_pressure"],
            _temporal_hold_evidence(signals),
        )
    return "resume_present", ["temporal_control_resume_present"], []


def _anchor_turn_fields(turn_id: str | None, turn_number: int | None) -> tuple[str | None, int | None]:
    try:
        anchor_turn_number = int(turn_number) if turn_number is not None else None
    except (TypeError, ValueError):
        anchor_turn_number = None
    return _clean_text(turn_id) or None, anchor_turn_number


def _temporal_control_payload(
    *,
    policy: dict[str, Any],
    prior_operation: str | None,
    selected_operation: str,
    allowed_operations: list[str],
    max_recalled: int,
    max_elapsed: int,
    elapsed_turns: int,
    anchor_turn_id: str | None,
    anchor_turn_number: int | None,
    recalled_turn_ids: list[str],
    recalled_consequence_ids: list[str],
    evidence: list[TemporalControlEvidenceRef],
    rationale: list[str],
) -> dict[str, Any]:
    state = TemporalControlState(
        current_operation=selected_operation,  # type: ignore[arg-type]
        prior_operation=prior_operation,  # type: ignore[arg-type]
        anchor_turn_id=anchor_turn_id,
        anchor_turn_number=anchor_turn_number,
        elapsed_turns=elapsed_turns,
        recalled_turn_ids=recalled_turn_ids,
        recalled_consequence_ids=recalled_consequence_ids,
        source_evidence=evidence,
    )
    target = TemporalControlTarget(
        policy_enabled=bool(policy.get("enabled")),
        operation=selected_operation,  # type: ignore[arg-type]
        allowed_operations=allowed_operations,  # type: ignore[list-item]
        commit_impact=str(policy.get("default_commit_impact") or "recover"),
        require_structured_events=bool(policy.get("require_structured_events")),
        max_recalled_turns=max_recalled,
        max_elapsed_turns=max_elapsed,
        anchor_turn_id=anchor_turn_id,
        anchor_turn_number=anchor_turn_number,
        recalled_turn_ids=recalled_turn_ids,
        recalled_consequence_ids=recalled_consequence_ids,
        source_evidence=evidence,
        rationale_codes=list(dict.fromkeys(rationale)),
    )
    return {
        "schema_version": TEMPORAL_CONTROL_SCHEMA_VERSION,
        "policy": policy,
        "state": state.to_runtime_dict(),
        "target": target.to_runtime_dict(),
        "source_evidence": [row.to_runtime_dict() for row in evidence],
        "rationale_codes": list(dict.fromkeys(rationale)),
    }


def derive_temporal_control(
    *,
    scene_plan_record: dict[str, Any] | None = None,
    scene_energy_target: dict[str, Any] | None = None,
    pacing_rhythm_target: dict[str, Any] | None = None,
    semantic_move_record: dict[str, Any] | None = None,
    prior_consequence_cascade_state: dict[str, Any] | None = None,
    prior_callback_web_state: dict[str, Any] | None = None,
    prior_temporal_control_state: dict[str, Any] | None = None,
    prior_planner_truth: dict[str, Any] | None = None,
    turn_id: str | None = None,
    turn_number: int | None = None,
    module_runtime_policy: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Derive a bounded temporal-control state and target from structured inputs."""

    policy = temporal_control_policy_from_module_runtime(module_runtime_policy)
    allowed_operations, max_recalled, max_elapsed = _temporal_policy_fields(policy)
    prior = _prior_state(prior_temporal_control_state, prior_planner_truth)
    prior_operation = _operation_from_prior(prior)
    previous_elapsed = _bounded_int(prior.get("elapsed_turns"), 0, minimum=0, maximum=max_elapsed)
    signals = _temporal_signal_fields(
        scene_plan_record=scene_plan_record,
        scene_energy_target=scene_energy_target,
        pacing_rhythm_target=pacing_rhythm_target,
        semantic_move_record=semantic_move_record,
    )
    recalled_turn_ids, recalled_consequence_ids, cascade_evidence, callback_evidence = _temporal_memory_refs(
        prior_consequence_cascade_state=prior_consequence_cascade_state,
        prior_callback_web_state=prior_callback_web_state,
        max_recalled=max_recalled,
    )
    operation, rationale, evidence = _select_temporal_operation(
        signals=signals,
        recalled_turn_ids=recalled_turn_ids,
        cascade_evidence=cascade_evidence,
        callback_evidence=callback_evidence,
    )

    selected_operation = _allowed_operation(operation, allowed_operations)
    if selected_operation != operation:
        rationale.append("temporal_control_policy_fallback")
    if not bool(policy.get("enabled")):
        selected_operation = "resume_present"
        rationale = ["temporal_control_not_applicable"]

    elapsed_turns = 0
    if selected_operation in {"advance_elapsed_time", "summarize_gap"}:
        elapsed_turns = min(max_elapsed, max(1, previous_elapsed + 1))

    anchor_turn_id, anchor_turn_number = _anchor_turn_fields(turn_id, turn_number)
    return _temporal_control_payload(
        policy=policy,
        prior_operation=prior_operation,
        selected_operation=selected_operation,
        allowed_operations=allowed_operations,
        max_recalled=max_recalled,
        max_elapsed=max_elapsed,
        elapsed_turns=elapsed_turns,
        anchor_turn_id=anchor_turn_id,
        anchor_turn_number=anchor_turn_number,
        recalled_turn_ids=recalled_turn_ids,
        recalled_consequence_ids=recalled_consequence_ids,
        evidence=evidence,
        rationale=rationale,
    )


def compact_temporal_control_context(target: dict[str, Any] | None) -> dict[str, Any]:
    """Return model-visible context without raw prose or hidden planning blobs."""

    src = target if isinstance(target, dict) else {}
    if not src or not src.get("policy_enabled"):
        return {}
    return {
        "schema_version": src.get("schema_version"),
        "operation": src.get("operation"),
        "allowed_operations": src.get("allowed_operations") or [],
        "anchor_turn_id": src.get("anchor_turn_id"),
        "anchor_turn_number": src.get("anchor_turn_number"),
        "recalled_turn_ids": src.get("recalled_turn_ids") or [],
        "recalled_consequence_ids": src.get("recalled_consequence_ids") or [],
        "max_recalled_turns": int(src.get("max_recalled_turns") or 0),
        "max_elapsed_turns": int(src.get("max_elapsed_turns") or 0),
        "require_structured_events": bool(src.get("require_structured_events")),
        "source_evidence": src.get("source_evidence") or [],
    }


def _event_rows(structured_output: dict[str, Any] | None) -> list[dict[str, Any]]:
    structured = structured_output if isinstance(structured_output, dict) else {}
    events = structured.get("temporal_control_events")
    return [row for row in events if isinstance(row, dict)] if isinstance(events, list) else []


def _event_turn_ids(event: dict[str, Any]) -> list[str]:
    return _clean_str_list(
        event.get("source_turn_ids")
        or event.get("recalled_turn_ids")
        or event.get("turn_ids")
    )


def _event_consequence_ids(event: dict[str, Any]) -> list[str]:
    return _clean_str_list(
        event.get("source_consequence_ids")
        or event.get("recalled_consequence_ids")
        or event.get("consequence_ids")
    )


def _temporal_validation_target(
    target_dict: dict[str, Any],
) -> TemporalControlTarget | dict[str, Any]:
    """Return a validated temporal target or a rejection payload."""
    try:
        return TemporalControlTarget.model_validate(target_dict)
    except Exception:
        return TemporalControlValidation(
            status="rejected",
            contract_pass=False,
            failure_codes=[TEMPORAL_CONTROL_FAILURE_TARGET_MISMATCH],
            feedback_code=TEMPORAL_CONTROL_FAILURE_TARGET_MISMATCH,
            target=target_dict,
            actual={"reason": "invalid_temporal_control_target"},
        ).to_runtime_dict()


def _temporal_validation_scope(target: TemporalControlTarget) -> dict[str, Any]:
    """Collect allowed operations and source ids for realization validation."""
    allowed_turn_ids = set(target.recalled_turn_ids or [])
    if target.anchor_turn_id:
        allowed_turn_ids.add(target.anchor_turn_id)
    return {
        "allowed_operations": set(target.allowed_operations or []),
        "allowed_turn_ids": allowed_turn_ids,
        "selected_consequence_ids": set(target.recalled_consequence_ids or []),
    }


def _temporal_event_failures(
    *,
    event: dict[str, Any],
    target: TemporalControlTarget,
    scope: dict[str, Any],
) -> tuple[list[str], dict[str, Any]]:
    """Validate one realized temporal event and return failures plus facts."""
    failure_codes: list[str] = []
    operation = _clean_text(event.get("operation") or event.get("type"))
    allowed_operations = scope["allowed_operations"]
    allowed_turn_ids = scope["allowed_turn_ids"]
    selected_consequence_ids = scope["selected_consequence_ids"]
    if operation and operation != target.operation:
        failure_codes.append(TEMPORAL_CONTROL_FAILURE_UNSELECTED_EVENT)
    if operation and operation not in allowed_operations:
        failure_codes.append(TEMPORAL_CONTROL_FAILURE_OPERATION_NOT_ALLOWED)
    if bool(event.get("rewrites_history") or event.get("history_rewrite")):
        failure_codes.append(TEMPORAL_CONTROL_FAILURE_HISTORY_REWRITE_ATTEMPT)
    if bool(event.get("adopts_branch_state") or event.get("inactive_branch_authoritative") or event.get("branch_state_adopted")):
        failure_codes.append(TEMPORAL_CONTROL_FAILURE_BRANCH_STATE_ADOPTION)
    if bool(event.get("mutates_canonical_state")):
        failure_codes.append(TEMPORAL_CONTROL_FAILURE_UNCOMMITTED_SOURCE)
    event_turn_ids = _event_turn_ids(event)
    event_consequence_ids = _event_consequence_ids(event)
    if event_turn_ids and not set(event_turn_ids).issubset(allowed_turn_ids):
        failure_codes.append(TEMPORAL_CONTROL_FAILURE_UNCOMMITTED_SOURCE)
    if event_consequence_ids and not set(event_consequence_ids).issubset(selected_consequence_ids):
        failure_codes.append(TEMPORAL_CONTROL_FAILURE_UNCOMMITTED_SOURCE)
    elapsed = _bounded_int(
        event.get("elapsed_turns") or event.get("elapsed_time_units"),
        0,
        minimum=0,
        maximum=999,
    )
    if elapsed > target.max_elapsed_turns:
        failure_codes.append(TEMPORAL_CONTROL_FAILURE_UNBOUNDED_JUMP)
    return failure_codes, {
        "operation": operation,
        "turn_ids": event_turn_ids,
        "consequence_ids": event_consequence_ids,
        "elapsed": elapsed,
    }


def _scan_temporal_events(
    *,
    events: list[dict[str, Any]],
    target: TemporalControlTarget,
    scope: dict[str, Any],
) -> dict[str, Any]:
    """Scan realized temporal events and collect validation facts."""
    failure_codes: list[str] = []
    realized_operations: list[str] = []
    realized_turn_ids: list[str] = []
    realized_consequence_ids: list[str] = []
    max_elapsed_observed = 0
    for event in events:
        event_failures, facts = _temporal_event_failures(event=event, target=target, scope=scope)
        failure_codes.extend(event_failures)
        if facts["operation"]:
            realized_operations.append(facts["operation"])
        realized_turn_ids.extend(facts["turn_ids"])
        realized_consequence_ids.extend(facts["consequence_ids"])
        max_elapsed_observed = max(max_elapsed_observed, int(facts["elapsed"] or 0))
    return {
        "failure_codes": failure_codes,
        "realized_operations": realized_operations,
        "realized_turn_ids": realized_turn_ids,
        "realized_consequence_ids": realized_consequence_ids,
        "max_elapsed_observed": max_elapsed_observed,
    }


def _temporal_validation_actual(
    *,
    events: list[dict[str, Any]],
    target: TemporalControlTarget,
    scan: dict[str, Any],
    temporal_control_state: dict[str, Any] | None,
    deduped_failures: list[str],
) -> dict[str, Any]:
    """Build the actual observed temporal-control validation payload."""
    return {
        "structured_events_present": bool(events),
        "event_count": len(events),
        "operation": target.operation,
        "realized_operations": list(dict.fromkeys(scan["realized_operations"])),
        "realized_turn_ids": list(dict.fromkeys(scan["realized_turn_ids"])),
        "realized_consequence_ids": list(dict.fromkeys(scan["realized_consequence_ids"])),
        "elapsed_turns": scan["max_elapsed_observed"]
        or (
            temporal_control_state.get("elapsed_turns")
            if isinstance(temporal_control_state, dict)
            else 0
        ),
        "contract_pass": not deduped_failures,
        "failure_codes": deduped_failures,
    }


def validate_temporal_control_realization(
    *,
    temporal_control_target: dict[str, Any] | None,
    temporal_control_state: dict[str, Any] | None = None,
    structured_output: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Validate temporal-control events using structured output only."""

    target_dict = temporal_control_target if isinstance(temporal_control_target, dict) else {}
    if not target_dict or not bool(target_dict.get("policy_enabled")):
        return TemporalControlValidation(
            status="not_applicable",
            contract_pass=True,
            target=target_dict,
        ).to_runtime_dict()
    target = _temporal_validation_target(target_dict)
    if isinstance(target, dict):
        return target

    events = _event_rows(structured_output)
    scope = _temporal_validation_scope(target)
    failure_codes: list[str] = []

    if target.operation not in scope["allowed_operations"]:
        failure_codes.append(TEMPORAL_CONTROL_FAILURE_OPERATION_NOT_ALLOWED)
    if (
        target.require_structured_events
        and target.operation != "resume_present"
        and not events
    ):
        failure_codes.append(TEMPORAL_CONTROL_FAILURE_MISSING_REQUIRED_EVENT)

    scan = _scan_temporal_events(events=events, target=target, scope=scope)
    failure_codes.extend(scan["failure_codes"])

    if target.require_structured_events and target.operation == "recall_committed_past":
        missing_turn_ids = set(target.recalled_turn_ids or []).difference(scan["realized_turn_ids"])
        if missing_turn_ids:
            failure_codes.append(TEMPORAL_CONTROL_FAILURE_MISSING_REQUIRED_EVENT)

    deduped_failures = [
        code for code in dict.fromkeys(failure_codes) if code in TEMPORAL_CONTROL_FAILURE_CODES
    ]
    commit_impact = _clean_text(target.commit_impact or "recover")
    failed = bool(deduped_failures)
    status = "approved"
    if failed:
        status = "degraded" if commit_impact == "diagnostic" else "rejected"
    actual = _temporal_validation_actual(
        events=events,
        target=target,
        scan=scan,
        temporal_control_state=temporal_control_state,
        deduped_failures=deduped_failures,
    )
    return TemporalControlValidation(
        status=status,  # type: ignore[arg-type]
        contract_pass=not failed,
        failure_codes=deduped_failures,
        feedback_code=deduped_failures[0] if deduped_failures else None,
        target=target.to_runtime_dict(),
        actual=actual,
        source_evidence=[
            TemporalControlEvidenceRef(
                source="structured_output",
                field="temporal_control_events",
                value={"present": bool(events), "event_count": len(events)},
            )
        ],
    ).to_runtime_dict()


def build_temporal_control_aspect_record(
    *,
    target: dict[str, Any] | None,
    state: dict[str, Any] | None = None,
    validation: dict[str, Any] | None = None,
    policy: dict[str, Any] | None = None,
    source: str = "runtime",
) -> dict[str, Any]:
    """Build a RuntimeAspectLedger-compatible temporal-control record."""

    target_dict = target if isinstance(target, dict) else {}
    state_dict = state if isinstance(state, dict) else {}
    validation_dict = validation if isinstance(validation, dict) else {}
    policy_dict = policy if isinstance(policy, dict) else normalize_temporal_control_policy(None)
    failure_codes = [
        code for code in _clean_str_list(validation_dict.get("failure_codes")) if code
    ]
    validation_status = _clean_text(validation_dict.get("status")).lower()
    applicable = bool(target_dict.get("policy_enabled"))
    if not validation_dict:
        aspect_status = "partial" if applicable else "not_applicable"
    elif validation_status == "approved":
        aspect_status = "passed"
    elif validation_status == "not_applicable":
        aspect_status = "not_applicable"
        applicable = False
    elif validation_status == "degraded":
        aspect_status = "partial"
    else:
        aspect_status = "failed"
    actual = (
        dict(validation_dict.get("actual"))
        if isinstance(validation_dict.get("actual"), dict)
        else {}
    )
    actual.update(
        {
            "validation_status": validation_status or None,
            "contract_pass": validation_dict.get("contract_pass"),
            "failure_codes": failure_codes,
        }
    )
    return {
        "applicable": applicable,
        "status": aspect_status,
        "expected": {
            "schema_version": target_dict.get("schema_version")
            or TEMPORAL_CONTROL_SCHEMA_VERSION,
            "policy_version": target_dict.get("policy_version")
            or TEMPORAL_CONTROL_POLICY_VERSION,
            "policy_present": bool(policy_dict.get("enabled") or target_dict),
            "policy_enabled": bool(target_dict.get("policy_enabled")),
            "commit_impact": target_dict.get("commit_impact")
            or policy_dict.get("default_commit_impact"),
            "require_structured_events": bool(target_dict.get("require_structured_events")),
            "allowed_operations": target_dict.get("allowed_operations")
            or policy_dict.get("allowed_operations")
            or [],
            "max_recalled_turns": int(
                target_dict.get("max_recalled_turns")
                if target_dict.get("max_recalled_turns") is not None
                else policy_dict.get("max_recalled_turns") or 0
            ),
            "max_elapsed_turns": int(
                target_dict.get("max_elapsed_turns")
                if target_dict.get("max_elapsed_turns") is not None
                else policy_dict.get("max_elapsed_turns") or 0
            ),
            "validation_uses_structured_events": True,
        },
        "selected": {
            "state": state_dict,
            "target": target_dict,
            "operation": target_dict.get("operation"),
            "anchor_turn_id": target_dict.get("anchor_turn_id"),
            "anchor_turn_number": target_dict.get("anchor_turn_number"),
            "recalled_turn_ids": target_dict.get("recalled_turn_ids") or [],
            "recalled_consequence_ids": target_dict.get("recalled_consequence_ids")
            or [],
            "elapsed_turns": state_dict.get("elapsed_turns"),
            "source_evidence": target_dict.get("source_evidence") or [],
            "rationale_codes": target_dict.get("rationale_codes") or [],
        },
        "actual": actual,
        "reasons": failure_codes
        or (
            ["temporal_control_target_selected"]
            if applicable and target_dict.get("operation") and not validation_dict
            else []
        ),
        "source": source,
        "failure_class": "recoverable_dramatic_failure" if failure_codes else None,
        "failure_reason": failure_codes[0] if failure_codes else None,
    }
