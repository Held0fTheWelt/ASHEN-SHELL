"""Task 2C-2 / Task 2D / Task 2E: shared routing evidence for Runtime, Writers-Room, and Improvement.

Task 2D field semantics (additive):
- requested_* : RoutingRequest workflow_phase and task_kind.
- selected_* : RoutingDecision policy output (adapter name plus provider/model echo).
- executed_adapter_name : adapter actually invoked when known.
- bounded_model_call : True if this stage called generate on a routed adapter; False if skipped.
- policy_execution_aligned : True/False when knowable, None if unknown.
- execution_deviation : dict only when selected and executed names differ.

Task 2E: ``routing_overview`` is a deterministic summary derived from the emitted
``route_reason_code`` (and ``no_eligible_spec_selection``), not independent reasoning.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from app.runtime.model_routing_contracts import RouteReasonCode, RoutingDecision, RoutingRequest


def routing_overview_for_reason_code(
    route_reason_code: str,
    *,
    no_eligible_spec_selection: bool,
) -> dict[str, str]:
    """Map primary route reason to a fixed title, summary, and severity (Task 2E)."""
    code = route_reason_code or ""
    if no_eligible_spec_selection or code == RouteReasonCode.no_eligible_adapter.value:
        return {
            "title": "No eligible spec",
            "summary": "No adapter spec remained eligible after phase, task, and structured-output filters.",
            "severity": "failed_selection",
        }
    mapping: dict[str, tuple[str, str, str]] = {
        RouteReasonCode.role_matrix_primary.value: (
            "Primary role match",
            "Selection follows the task role-family matrix without constraint overrides.",
            "normal",
        ),
        RouteReasonCode.escalation_due_to_complexity.value: (
            "Escalated for quality",
            "High complexity on a synthesis-heavy path changed the selected adapter versus lower complexity.",
            "elevated",
        ),
        RouteReasonCode.escalation_due_to_high_stakes_task.value: (
            "Escalated for risk",
            "High-stakes task kind required an LLM-class route while SLM-class specs remained eligible.",
            "elevated",
        ),
        RouteReasonCode.escalation_due_to_structured_output_gap.value: (
            "Escalated for structure",
            "Structured output eligibility changed the deterministic primary adapter versus the full pre-structured candidate set.",
            "elevated",
        ),
        RouteReasonCode.escalation_due_to_explicit_hint.value: (
            "Escalated for risk",
            "Escalation hints on an escalation-sensitive task steered selection toward an LLM-class route.",
            "elevated",
        ),
        RouteReasonCode.latency_constraint.value: (
            "Constrained by latency",
            "Latency budget changed the winner versus a normal budget on the same candidate pool.",
            "normal",
        ),
        RouteReasonCode.cost_constraint.value: (
            "Constrained by cost",
            "Cost sensitivity changed the winner versus medium sensitivity on the same candidate pool.",
            "normal",
        ),
        RouteReasonCode.fallback_only.value: (
            "Fallback route",
            "Preferred role-family pool was empty; selection used a widened pool.",
            "degraded",
        ),
        RouteReasonCode.structured_output_required.value: (
            "Escalated for structure",
            "Legacy code: structured output constraints shaped the pool.",
            "elevated",
        ),
        RouteReasonCode.escalation_applied.value: (
            "Escalated for risk",
            "Legacy code: escalation-sensitive routing with hints.",
            "elevated",
        ),
    }
    if code in mapping:
        title, summary, severity = mapping[code]
        return {"title": title, "summary": summary, "severity": severity}
    return {
        "title": "Unmapped route reason",
        "summary": "No fixed overview mapping exists for this route_reason_code value.",
        "severity": "degraded",
    }


def _as_request_dict(req: RoutingRequest | Mapping[str, Any]) -> dict[str, Any]:
    if isinstance(req, RoutingRequest):
        return req.model_dump(mode="json")
    return dict(req)


def _as_decision_dict(dec: RoutingDecision | Mapping[str, Any]) -> dict[str, Any]:
    if isinstance(dec, RoutingDecision):
        return dec.model_dump(mode="json")
    return dict(dec)


def _norm_adapter(s: str | None) -> str:
    return (s or "").strip().lower()


def _compute_policy_execution_aligned(
    *,
    selected_name: str,
    executed_name: str | None,
    resolved_via_get_adapter: bool | None,
    fallback_to_passed_adapter: bool | None,
    no_eligible_spec_selection: bool,
) -> bool | None:
    if no_eligible_spec_selection:
        return None
    if not selected_name:
        return None
    if resolved_via_get_adapter is not None:
        return bool(resolved_via_get_adapter)
    ex = _norm_adapter(executed_name)
    if not ex:
        return None
    return _norm_adapter(selected_name) == ex


def _compute_execution_deviation(
    *,
    selected_name: str,
    executed_name: str | None,
    note: str | None,
    no_eligible_spec_selection: bool,
) -> dict[str, Any] | None:
    if no_eligible_spec_selection or not selected_name:
        return None
    ex = _norm_adapter(executed_name)
    if not ex:
        return None
    if _norm_adapter(selected_name) == ex:
        return None
    out: dict[str, Any] = {
        "selected_adapter_name": selected_name.strip(),
        "executed_adapter_name": (executed_name or "").strip(),
    }
    if note:
        out["note"] = note
    return out


def build_routing_evidence(
    *,
    routing_request: RoutingRequest | Mapping[str, Any],
    routing_decision: RoutingDecision | Mapping[str, Any],
    executed_adapter_name: str | None = None,
    passed_adapter_name: str | None = None,
    resolved_via_get_adapter: bool | None = None,
    fallback_to_passed_adapter: bool | None = None,
    bounded_model_call: bool | None = None,
    skip_reason: str | None = None,
    execution_deviation_note: str | None = None,
) -> dict[str, Any]:
    """Stable cross-surface summary; N/A fields are None when not applicable."""
    req = _as_request_dict(routing_request)
    dec = _as_decision_dict(routing_decision)
    sel = (dec.get("selected_adapter_name") or "").strip()
    code = str(dec.get("route_reason_code") or "")
    no_eligible = code == "no_eligible_adapter" or not sel

    aligned = _compute_policy_execution_aligned(
        selected_name=sel,
        executed_name=executed_adapter_name,
        resolved_via_get_adapter=resolved_via_get_adapter,
        fallback_to_passed_adapter=fallback_to_passed_adapter,
        no_eligible_spec_selection=no_eligible,
    )
    deviation = _compute_execution_deviation(
        selected_name=sel,
        executed_name=executed_adapter_name,
        note=execution_deviation_note,
        no_eligible_spec_selection=no_eligible,
    )

    overview = routing_overview_for_reason_code(code, no_eligible_spec_selection=no_eligible)
    decision_factors = dec.get("decision_factors")
    routing_diagnostics: dict[str, Any] = {}
    if isinstance(decision_factors, dict):
        for k in (
            "escalation_trigger",
            "structured_output_gap",
            "explicit_hint_present",
            "preferred_pool_empty",
            "mandatory_llm_pool_applied",
            "counterfactual_latency_changed",
            "counterfactual_cost_changed",
        ):
            if k in decision_factors:
                routing_diagnostics[k] = decision_factors[k]

    return {
        "routing_invoked": True,
        "requested_workflow_phase": req.get("workflow_phase"),
        "requested_task_kind": req.get("task_kind"),
        "selected_adapter_name": sel,
        "selected_provider": dec.get("selected_provider") or "",
        "selected_model": dec.get("selected_model") or "",
        "route_reason_code": code,
        "routing_overview": overview,
        "fallback_chain": list(dec.get("fallback_chain") or []),
        "escalation_applied": bool(dec.get("escalation_applied")),
        "degradation_applied": bool(dec.get("degradation_applied")),
        "routing_diagnostics": routing_diagnostics if routing_diagnostics else None,
        "executed_adapter_name": executed_adapter_name,
        "passed_adapter_name": passed_adapter_name,
        "resolved_via_get_adapter": resolved_via_get_adapter,
        "fallback_to_passed_adapter": fallback_to_passed_adapter,
        "bounded_model_call": bounded_model_call,
        "skip_reason": skip_reason,
        "no_eligible_spec_selection": no_eligible,
        "policy_execution_aligned": aligned,
        "execution_deviation": deviation,
    }


def attach_stage_routing_evidence(
    stage_trace: dict[str, Any],
    routing_request: RoutingRequest,
    *,
    executed_adapter_name: str | None = None,
    bounded_model_call: bool | None = None,
    skip_reason: str | None = None,
    execution_deviation_note: str | None = None,
) -> None:
    """Attach routing_evidence dict; bounded_model_call True means generate was invoked."""
    decision = stage_trace.get("decision")
    if not isinstance(decision, dict):
        return

    bc = bounded_model_call if bounded_model_call is not None else stage_trace.get("bounded_model_call")
    sk = skip_reason
    if sk is None and bc is False:
        sk = stage_trace.get("skip_reason")

    ex = executed_adapter_name
    if ex is None and bc is True:
        raw = stage_trace.get("executed_adapter_name") or stage_trace.get("adapter_key")
        ex = str(raw).strip() if raw else None

    stage_trace["routing_evidence"] = build_routing_evidence(
        routing_request=routing_request,
        routing_decision=decision,
        executed_adapter_name=ex,
        passed_adapter_name=None,
        resolved_via_get_adapter=None,
        fallback_to_passed_adapter=None,
        bounded_model_call=bc if bc is not None else None,
        skip_reason=str(sk) if sk else None,
        execution_deviation_note=execution_deviation_note,
    )
