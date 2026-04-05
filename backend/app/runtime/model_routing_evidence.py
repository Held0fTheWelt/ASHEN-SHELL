"""Task 2C-2: shared, honest routing evidence shape for Runtime, Writers-Room, and Improvement.

Exposes only what the caller supplies and what ``RoutingDecision`` actually contains.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from app.runtime.model_routing_contracts import RoutingDecision, RoutingRequest


def _as_request_dict(req: RoutingRequest | Mapping[str, Any]) -> dict[str, Any]:
    if isinstance(req, RoutingRequest):
        return req.model_dump(mode="json")
    return dict(req)


def _as_decision_dict(dec: RoutingDecision | Mapping[str, Any]) -> dict[str, Any]:
    if isinstance(dec, RoutingDecision):
        return dec.model_dump(mode="json")
    return dict(dec)


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
) -> dict[str, Any]:
    """Stable cross-surface summary; N/A fields are ``null`` when not applicable to a path."""
    req = _as_request_dict(routing_request)
    dec = _as_decision_dict(routing_decision)
    sel = (dec.get("selected_adapter_name") or "").strip()
    code = str(dec.get("route_reason_code") or "")
    no_eligible = code == "no_eligible_adapter" or not sel

    return {
        "routing_invoked": True,
        "requested_workflow_phase": req.get("workflow_phase"),
        "requested_task_kind": req.get("task_kind"),
        "selected_adapter_name": sel,
        "selected_provider": dec.get("selected_provider") or "",
        "selected_model": dec.get("selected_model") or "",
        "route_reason_code": code,
        "fallback_chain": list(dec.get("fallback_chain") or []),
        "escalation_applied": bool(dec.get("escalation_applied")),
        "degradation_applied": bool(dec.get("degradation_applied")),
        "executed_adapter_name": executed_adapter_name,
        "passed_adapter_name": passed_adapter_name,
        "resolved_via_get_adapter": resolved_via_get_adapter,
        "fallback_to_passed_adapter": fallback_to_passed_adapter,
        "bounded_model_call": bounded_model_call,
        "skip_reason": skip_reason,
        "no_eligible_spec_selection": no_eligible,
    }


def attach_stage_routing_evidence(
    stage_trace: dict[str, Any],
    routing_request: RoutingRequest,
    *,
    executed_adapter_name: str | None = None,
    bounded_model_call: bool | None = None,
    skip_reason: str | None = None,
) -> None:
    """Augment a Writers-Room / Improvement stage trace (must already contain ``decision`` dict)."""
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
    )
