"""Area 2 — compact operator truth derived only from existing facts + explicit counts."""

from __future__ import annotations

from typing import Any

from app.runtime.area2_operational_state import (
    Area2OperationalState,
    classify_area2_operational_state,
    pytest_session_active,
    rollup_no_eligible_discipline_for_bounded_traces,
)
from app.runtime.area2_startup_profiles import resolve_startup_profile
from app.runtime.model_inventory_contract import InventorySurface
from app.runtime.model_inventory_report import validate_surface_coverage
from app.runtime.model_routing_contracts import RouteReasonCode
from app.runtime.operator_audit import primary_concern_code

# Frozen summary aligned with AREA2_AUTHORITY_REGISTRY narrative (no runtime probe).
_CANONICAL_TASK2A_AUTHORITY_SUMMARY = (
    "Authoritative Task 2A policy: app.runtime.model_routing.route_model. "
    "Runtime uses adapter_registry model specs when specs=None; Writers-Room and Improvement "
    "use writers_room_model_routing (story_runtime_core.model_registry rows). "
    "ai_stack LangGraph RoutingPolicy is compatibility-only, not canonical for these HTTP paths."
)


def _derive_route_status(
    *,
    operational_state: Area2OperationalState,
    no_eligible_rollup: dict[str, Any],
    stages_with_no_eligible_adapter: list[str],
) -> str:
    """Single deterministic routing health label derived from classification + trace rollups."""

    worst = "not_applicable"
    if isinstance(no_eligible_rollup, dict):
        w = no_eligible_rollup.get("rollup_worst_case")
        if isinstance(w, str) and w:
            worst = w

    if operational_state is Area2OperationalState.test_isolated:
        return "test_isolated_expected_empty_registry"
    if operational_state is Area2OperationalState.misconfigured:
        return "misconfigured_registry_or_inventory"
    if operational_state is Area2OperationalState.intentionally_degraded:
        return "bootstrap_disabled_intentional_posture"

    if stages_with_no_eligible_adapter:
        if worst == "true_no_eligible_adapter":
            return "no_eligible_on_routed_stage_not_normalized_as_healthy"
        if worst == "intentional_degraded_route":
            return "no_eligible_with_task2e_degrade_on_stage"
        if worst == "bounded_executor_mismatch":
            return "selected_adapter_missing_from_bounded_executor"
        if worst == "test_isolated_empty_registry":
            return "no_eligible_discipline_test_isolated_on_route"
        if worst == "missing_registration_or_specs":
            return "no_eligible_discipline_missing_specs_on_route"
        return "no_eligible_on_routed_stage"

    if worst == "not_applicable":
        return "canonical_route_eligible"
    return f"healthy_process_routing_discipline_{worst}"


def _legibility_startup_profile(bootstrap_enabled: bool | None) -> str | None:
    if bootstrap_enabled is None:
        return None
    return resolve_startup_profile(
        routing_registry_bootstrap=bootstrap_enabled,
        under_pytest=pytest_session_active(),
    ).value


def _selected_executed_summary_runtime(
    traces: list[dict[str, Any]],
    model_routing_trace: dict[str, Any] | None,
) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for t in traces:
        if not isinstance(t, dict):
            continue
        rev = t.get("routing_evidence")
        if not isinstance(rev, dict):
            continue
        sk = str(t.get("stage_id") or "")
        rows.append(
            {
                "stage_key": sk,
                "selected": rev.get("selected_adapter_name"),
                "executed": rev.get("executed_adapter_name"),
                "aligned": rev.get("policy_execution_aligned"),
                "route_reason_code": rev.get("route_reason_code"),
            }
        )
    rollup_code = None
    rollup_sel = None
    rollup_exec = None
    if model_routing_trace and isinstance(model_routing_trace, dict):
        rev2 = model_routing_trace.get("routing_evidence")
        if isinstance(rev2, dict):
            rollup_code = rev2.get("route_reason_code")
            rollup_sel = rev2.get("selected_adapter_name")
            rollup_exec = rev2.get("executed_adapter_name")
    return {
        "per_stage": rows,
        "legacy_roll_up": {
            "route_reason_code": rollup_code,
            "selected_adapter_name": rollup_sel,
            "executed_adapter_name": rollup_exec,
        },
    }


def _selected_executed_summary_bounded(traces: list[dict[str, Any]]) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for t in traces:
        if not isinstance(t, dict):
            continue
        rev = t.get("routing_evidence")
        dec = t.get("decision") if isinstance(t.get("decision"), dict) else {}
        sk = str(t.get("stage_id") or t.get("stage") or "")
        selected = dec.get("selected_adapter_name") if dec else None
        executed = t.get("executed_adapter_name")
        if executed is None and isinstance(rev, dict):
            executed = rev.get("executed_adapter_name")
        aligned = rev.get("policy_execution_aligned") if isinstance(rev, dict) else None
        code = dec.get("route_reason_code") if dec else None
        if code is None and isinstance(rev, dict):
            code = rev.get("route_reason_code")
        rows.append(
            {
                "stage_key": sk,
                "selected": selected,
                "executed": executed,
                "aligned": aligned,
                "route_reason_code": code,
            }
        )
    return {"per_stage": rows}


def _runtime_canonical_coverage(specs: list[Any]) -> tuple[dict[str, bool], bool]:
    r = validate_surface_coverage(specs, InventorySurface.runtime_staged)
    return {InventorySurface.runtime_staged.value: r.all_satisfied}, r.all_satisfied


def _bounded_canonical_coverage(specs: list[Any]) -> tuple[dict[str, bool], bool]:
    wr = validate_surface_coverage(specs, InventorySurface.writers_room)
    imp = validate_surface_coverage(specs, InventorySurface.improvement_bounded)
    m = {
        InventorySurface.writers_room.value: wr.all_satisfied,
        InventorySurface.improvement_bounded.value: imp.all_satisfied,
    }
    return m, wr.all_satisfied and imp.all_satisfied


def build_area2_operator_truth(
    *,
    surface: str,
    authority_source: str,
    bootstrap_enabled: bool | None,
    registry_model_spec_count: int,
    specs_for_coverage: list[Any] | None,
    runtime_stage_traces: list[dict[str, Any]] | None = None,
    model_routing_trace: dict[str, Any] | None = None,
    bounded_traces: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Assemble additive ``area2_operator_truth`` for operator_audit (English keys only)."""

    traces_rt = [t for t in (runtime_stage_traces or []) if isinstance(t, dict)]
    traces_bd = [t for t in (bounded_traces or []) if isinstance(t, dict)]
    active = traces_rt if traces_rt else traces_bd

    coverage_map: dict[str, bool] = {}
    all_sat: bool | None = None
    if specs_for_coverage is not None:
        if surface == "runtime":
            coverage_map, all_sat = _runtime_canonical_coverage(specs_for_coverage)
        elif surface in ("writers_room", "improvement"):
            coverage_map, all_sat = _bounded_canonical_coverage(specs_for_coverage)
        else:
            all_sat = None

    operational_state = classify_area2_operational_state(
        bootstrap_enabled=bootstrap_enabled,
        registry_model_spec_count=registry_model_spec_count,
        canonical_surfaces_all_satisfied=all_sat,
    )

    pcc = primary_concern_code(
        traces=active,
        model_routing_trace=model_routing_trace if surface == "runtime" else None,
    )

    no_eligible_stages = [
        str(t.get("stage_id") or t.get("stage") or "")
        for t in active
        if isinstance(t, dict)
        and (
            (isinstance(t.get("decision"), dict) and t["decision"].get("route_reason_code") == RouteReasonCode.no_eligible_adapter.value)
            or (
                isinstance(t.get("routing_evidence"), dict)
                and t["routing_evidence"].get("route_reason_code") == RouteReasonCode.no_eligible_adapter.value
            )
        )
    ]

    discipline = rollup_no_eligible_discipline_for_bounded_traces(
        active,
        registry_spec_count=registry_model_spec_count,
    )

    if surface == "runtime":
        selected_executed = _selected_executed_summary_runtime(traces_rt, model_routing_trace)
    else:
        selected_executed = _selected_executed_summary_bounded(traces_bd)

    stages_nea = [s for s in no_eligible_stages if s]
    route_status = _derive_route_status(
        operational_state=operational_state,
        no_eligible_rollup=discipline,
        stages_with_no_eligible_adapter=stages_nea,
    )
    legibility = {
        "authority_source": authority_source,
        "operational_state": operational_state.value,
        "route_status": route_status,
        "selected_vs_executed": selected_executed,
        "primary_operational_concern": pcc,
        "startup_profile": _legibility_startup_profile(bootstrap_enabled),
    }

    return {
        "surface": surface,
        "authority_source": authority_source,
        "bootstrap_enabled": bootstrap_enabled,
        "registry_model_spec_count": registry_model_spec_count,
        "route_coverage_state": coverage_map,
        "canonical_surfaces_all_satisfied": all_sat,
        "selected_vs_executed": selected_executed,
        "primary_operational_concern": pcc,
        "operational_state": operational_state.value,
        "no_eligible_discipline": discipline,
        "stages_with_no_eligible_adapter": stages_nea,
        "canonical_authority_summary": _CANONICAL_TASK2A_AUTHORITY_SUMMARY,
        "legibility": legibility,
    }


def merge_area2_operator_truth(audit: dict[str, Any], truth: dict[str, Any]) -> None:
    """Attach truth to an existing operator_audit dict in place."""
    audit["area2_operator_truth"] = truth


def resolve_routing_bootstrap_enabled() -> bool | None:
    """Read ``ROUTING_REGISTRY_BOOTSTRAP`` when a Flask app context exists."""
    try:
        from flask import current_app, has_app_context

        if has_app_context():
            return bool(current_app.config.get("ROUTING_REGISTRY_BOOTSTRAP", True))
    except Exception:
        return None
    return None


def enrich_operator_audit_with_area2_truth(
    audit: dict[str, Any],
    *,
    surface: str,
    authority_source: str,
    bootstrap_enabled: bool | None,
    registry_model_spec_count: int,
    specs_for_coverage: list[Any] | None,
    runtime_stage_traces: list[dict[str, Any]] | None = None,
    model_routing_trace: dict[str, Any] | None = None,
    bounded_traces: list[dict[str, Any]] | None = None,
) -> None:
    """Populate ``area2_operator_truth`` on an existing operator_audit dict."""
    truth = build_area2_operator_truth(
        surface=surface,
        authority_source=authority_source,
        bootstrap_enabled=bootstrap_enabled,
        registry_model_spec_count=registry_model_spec_count,
        specs_for_coverage=specs_for_coverage,
        runtime_stage_traces=runtime_stage_traces,
        model_routing_trace=model_routing_trace,
        bounded_traces=bounded_traces,
    )
    merge_area2_operator_truth(audit, truth)


def bounded_traces_from_task_2a_routing(task_2a_routing: dict[str, Any]) -> list[dict[str, Any]]:
    """Ordered preflight/synthesis trace dicts from a ``task_2a_routing`` map."""
    out: list[dict[str, Any]] = []
    for key in ("preflight", "synthesis"):
        e = task_2a_routing.get(key)
        if isinstance(e, dict):
            out.append(e)
    return out
