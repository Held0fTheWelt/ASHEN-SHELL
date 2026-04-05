"""Task 2C-2: shared routing_evidence helper."""

from app.runtime.model_routing_contracts import (
    RouteReasonCode,
    RoutingDecision,
    RoutingRequest,
    TaskKind,
    WorkflowPhase,
)
from app.runtime.model_routing_evidence import build_routing_evidence


def test_build_routing_evidence_marks_no_eligible_when_code_says_so():
    req = RoutingRequest(workflow_phase=WorkflowPhase.generation, task_kind=TaskKind.narrative_formulation)
    dec = RoutingDecision(
        selected_adapter_name="",
        selected_provider="",
        selected_model="",
        phase=WorkflowPhase.generation,
        task_kind=TaskKind.narrative_formulation,
        route_reason_code=RouteReasonCode.no_eligible_adapter,
    )
    ev = build_routing_evidence(
        routing_request=req,
        routing_decision=dec,
        executed_adapter_name="passed_only",
        passed_adapter_name="passed_only",
        resolved_via_get_adapter=False,
        fallback_to_passed_adapter=True,
        bounded_model_call=None,
        skip_reason=None,
    )
    assert ev["no_eligible_spec_selection"] is True
    assert ev["fallback_to_passed_adapter"] is True
    assert ev["route_reason_code"] == "no_eligible_adapter"
