"""Task 1 — Multi-stage Runtime AI orchestration (SLM-first, conditional LLM synthesis).

Bounded stage contracts, deterministic packaging into the canonical structured story
shape, and inspectable per-stage routing evidence. Authority remains in ``execute_turn``;
this module only prepares ``AdapterResponse`` for ``process_adapter_response``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable

from pydantic import BaseModel, Field, field_validator

from app.runtime.ai_failure_recovery import AIFailureClass, RetryPolicy
from app.runtime.ai_adapter import AdapterRequest, AdapterResponse, StoryAIAdapter, generate_with_timeout
from app.runtime.adapter_registry import get_adapter
from app.runtime.model_routing import route_model
from app.runtime.model_routing_contracts import (
    Complexity,
    EscalationHint,
    LatencyBudget,
    CostSensitivity,
    RoutingDecision,
    RoutingRequest,
    TaskKind,
    WorkflowPhase,
)
from app.runtime.model_routing_evidence import attach_stage_routing_evidence, build_routing_evidence
from app.runtime.operator_audit import build_runtime_operator_audit, runtime_additive_orchestration_fields
from app.runtime.runtime_models import DegradedMarker, SessionState


RUNTIME_STAGE_SCHEMA_VERSION = "1"
RUNTIME_STAGE_META_KEY = "runtime_stage"
RUNTIME_STAGE_SCHEMA_META_KEY = "runtime_stage_schema_version"


class RuntimeStageId(str, Enum):
    """Canonical Runtime pipeline stage identifiers (cross-model orchestration)."""

    preflight = "preflight"
    signal_consistency = "signal_consistency"
    synthesis = "synthesis"
    packaging = "packaging"


class OrchestrationFinalPath(str, Enum):
    """High-level outcome of the staged pipeline (inspectable, deterministic)."""

    slm_then_llm = "slm_then_llm"
    slm_only = "slm_only"
    degraded_early_skip_then_synthesis = "degraded_early_skip_then_synthesis"
    degraded_parse_forced_synthesis = "degraded_parse_forced_synthesis"


class PreflightStageOutput(BaseModel):
    """Structured output expected in ``structured_payload`` for preflight stage calls."""

    runtime_stage: str = "preflight"
    ambiguity_score: float = Field(ge=0.0, le=1.0, default=0.0)
    trigger_signals: list[str] = Field(default_factory=list, max_length=32)
    repetition_risk: str = "low"
    classification_label: str = ""
    preflight_ok: bool = True

    @field_validator("trigger_signals")
    @classmethod
    def cap_triggers(cls, v: list[str]) -> list[str]:
        return list(v)[:32]


class SignalStageOutput(BaseModel):
    """Structured output for signal / consistency stage (escalation recommendation)."""

    runtime_stage: str = "signal_consistency"
    needs_llm_synthesis: bool = True
    skip_synthesis_reason: str | None = None
    narrative_summary: str = ""
    consistency_notes: str = ""
    consistency_flags: list[str] = Field(default_factory=list, max_length=16)

    @field_validator("consistency_flags")
    @classmethod
    def cap_flags(cls, v: list[str]) -> list[str]:
        return list(v)[:16]


def _session_complexity(session: SessionState) -> Complexity:
    meta = session.metadata if isinstance(session.metadata, dict) else {}
    raw = meta.get("routing_complexity")
    if isinstance(raw, str):
        try:
            return Complexity(raw)
        except ValueError:
            pass
    return Complexity.medium


def _session_latency_cost(session: SessionState) -> tuple[LatencyBudget, CostSensitivity]:
    meta = session.metadata if isinstance(session.metadata, dict) else {}
    latency_budget = LatencyBudget.normal
    cost_sensitivity = CostSensitivity.medium
    lb = meta.get("routing_latency_budget")
    if isinstance(lb, str):
        try:
            latency_budget = LatencyBudget(lb)
        except ValueError:
            pass
    cs = meta.get("routing_cost_sensitivity")
    if isinstance(cs, str):
        try:
            cost_sensitivity = CostSensitivity(cs)
        except ValueError:
            pass
    return latency_budget, cost_sensitivity


def _session_base_escalation_hints(session: SessionState) -> list[EscalationHint]:
    hints: list[EscalationHint] = []
    markers = session.degraded_state.active_markers
    if DegradedMarker.FALLBACK_ACTIVE in markers or DegradedMarker.RETRY_EXHAUSTED in markers:
        hints.append(EscalationHint.continuity_risk)
    return hints


def build_preflight_routing_request(session: SessionState) -> RoutingRequest:
    """Stage routing: cheap SLM-oriented preflight."""
    latency_budget, cost_sensitivity = _session_latency_cost(session)
    return RoutingRequest(
        workflow_phase=WorkflowPhase.preflight,
        task_kind=TaskKind.cheap_preflight,
        complexity=_session_complexity(session),
        latency_budget=latency_budget,
        cost_sensitivity=cost_sensitivity,
        requires_structured_output=True,
        escalation_hints=list(_session_base_escalation_hints(session)),
    )


def build_signal_routing_request(
    session: SessionState,
    *,
    extra_hints: list[EscalationHint],
) -> RoutingRequest:
    """Stage routing: signal / repetition-consistency (SLM-first task kind)."""
    latency_budget, cost_sensitivity = _session_latency_cost(session)
    merged = list(_session_base_escalation_hints(session))
    merged.extend(extra_hints)
    return RoutingRequest(
        workflow_phase=WorkflowPhase.interpretation,
        task_kind=TaskKind.repetition_consistency_check,
        complexity=_session_complexity(session),
        latency_budget=latency_budget,
        cost_sensitivity=cost_sensitivity,
        requires_structured_output=True,
        escalation_hints=merged,
    )


def build_synthesis_routing_request(session: SessionState) -> RoutingRequest:
    """Stage routing: LLM-heavy narrative synthesis (same semantics as legacy runtime request)."""
    meta = session.metadata if isinstance(session.metadata, dict) else {}
    task_kind = TaskKind.narrative_formulation
    raw_tk = meta.get("routing_task_kind")
    if isinstance(raw_tk, str):
        try:
            task_kind = TaskKind(raw_tk)
        except ValueError:
            pass
    latency_budget, cost_sensitivity = _session_latency_cost(session)
    hints = list(_session_base_escalation_hints(session))
    return RoutingRequest(
        workflow_phase=WorkflowPhase.generation,
        task_kind=task_kind,
        complexity=_session_complexity(session),
        latency_budget=latency_budget,
        cost_sensitivity=cost_sensitivity,
        requires_structured_output=True,
        escalation_hints=hints,
    )


def escalation_hints_from_preflight(preflight: PreflightStageOutput | None) -> list[EscalationHint]:
    """Deterministic mapping from preflight output to routing hints (not model authority)."""
    if preflight is None:
        return []
    out: list[EscalationHint] = []
    if preflight.repetition_risk in ("high", "medium"):
        out.append(EscalationHint.continuity_risk)
    if preflight.ambiguity_score >= 0.55:
        out.append(EscalationHint.ambiguity_high)
    return out


def parse_preflight_payload(payload: dict[str, Any] | None) -> tuple[PreflightStageOutput | None, list[str]]:
    if not payload or not isinstance(payload, dict):
        return None, ["preflight: missing structured_payload"]
    try:
        return PreflightStageOutput.model_validate(payload), []
    except Exception as exc:
        return None, [f"preflight: validate failed: {exc}"]


def parse_signal_payload(payload: dict[str, Any] | None) -> tuple[SignalStageOutput | None, list[str]]:
    if not payload or not isinstance(payload, dict):
        return None, ["signal: missing structured_payload"]
    try:
        return SignalStageOutput.model_validate(payload), []
    except Exception as exc:
        return None, [f"signal: validate failed: {exc}"]


def compute_needs_llm_synthesis(
    *,
    signal: SignalStageOutput | None,
    signal_parse_ok: bool,
    preflight_parse_ok: bool,
) -> tuple[bool, str]:
    """Deterministic synthesis gate; parse failures force synthesis for safe degradation."""
    if not signal_parse_ok or signal is None:
        return True, "degraded_signal_parse_or_missing_forcing_synthesis"
    if not preflight_parse_ok:
        return True, "degraded_preflight_parse_forcing_synthesis"
    if signal.needs_llm_synthesis:
        return True, "signal_requested_synthesis"
    reason = (signal.skip_synthesis_reason or "slm_sufficient").strip() or "slm_sufficient"
    return False, reason


def build_slm_only_structured_payload(
    *,
    preflight: PreflightStageOutput | None,
    signal: SignalStageOutput,
) -> dict[str, Any]:
    """Deterministic packaging: canonical story JSON for ``process_adapter_response`` (advisory only)."""
    scene = (signal.narrative_summary or "").strip() or "[staged-runtime/slm_only] Continuity packaged without LLM synthesis."
    trig = list(preflight.trigger_signals if preflight else [])[:32]
    rationale = (
        f"[staged-runtime/slm_only] {signal.skip_synthesis_reason or 'slm_sufficient'}; "
        f"consistency_notes={signal.consistency_notes[:500]}"
    )
    return {
        "scene_interpretation": scene[:8000],
        "detected_triggers": trig,
        "proposed_state_deltas": [],
        "rationale": rationale[:8000],
        "proposed_scene_id": None,
        "dialogue_impulses": [],
        "conflict_vector": None,
        "confidence": None,
    }


def _resolve_routed_adapter(
    routing_decision: RoutingDecision,
    passed_adapter: StoryAIAdapter,
) -> tuple[StoryAIAdapter, Any]:
    resolved = None
    if routing_decision.selected_adapter_name:
        resolved = get_adapter(routing_decision.selected_adapter_name)
    execution = resolved if resolved is not None else passed_adapter
    return execution, resolved


def _trace_dict_for_stage(
    *,
    stage_id: RuntimeStageId,
    routing_request: RoutingRequest,
    routing_decision: RoutingDecision,
    passed_adapter: StoryAIAdapter,
    execution_adapter: StoryAIAdapter,
    resolved_via_registry: bool,
    bounded_model_call: bool,
    skip_reason: str | None,
    output_summary: dict[str, Any],
    errors: list[str],
) -> dict[str, Any]:
    trace: dict[str, Any] = {
        "stage_id": stage_id.value,
        "stage_kind": "routed_model_stage",
        "bounded_model_call": bounded_model_call,
        "skip_reason": skip_reason,
        "request": routing_request.model_dump(mode="json"),
        "decision": routing_decision.model_dump(mode="json"),
        "passed_adapter_name": passed_adapter.adapter_name,
        "executed_adapter_name": execution_adapter.adapter_name if bounded_model_call else None,
        "selected_adapter_name": routing_decision.selected_adapter_name,
        "resolved_via_get_adapter": resolved_via_registry,
        "fallback_to_passed_adapter": not resolved_via_registry,
        "output_summary": output_summary,
        "errors": errors,
    }
    attach_stage_routing_evidence(
        trace,
        routing_request,
        executed_adapter_name=execution_adapter.adapter_name if bounded_model_call else None,
        bounded_model_call=bounded_model_call,
        skip_reason=skip_reason,
        execution_deviation_note=None,
    )
    return trace


def build_legacy_model_routing_rollup(
    *,
    synthesis_ran: bool,
    synthesis_request: RoutingRequest | None,
    synthesis_decision: RoutingDecision | None,
    synthesis_execution_adapter: StoryAIAdapter | None,
    synthesis_resolved_via_registry: bool | None,
    passed_adapter: StoryAIAdapter,
    signal_request: RoutingRequest,
    signal_decision: RoutingDecision,
    signal_execution_adapter: StoryAIAdapter,
    signal_resolved: bool,
    final_path: OrchestrationFinalPath,
) -> dict[str, Any]:
    """Legacy-shaped trace for ``last_model_routing_trace`` / ``AIDecisionLog.model_routing_trace``."""
    if synthesis_ran and synthesis_request and synthesis_decision and synthesis_execution_adapter:
        return {
            "routing_invoked": True,
            "rollup_mode": "synthesis_stage",
            "final_path": final_path.value,
            "request": synthesis_request.model_dump(mode="json"),
            "decision": synthesis_decision.model_dump(mode="json"),
            "passed_adapter_name": passed_adapter.adapter_name,
            "executed_adapter_name": synthesis_execution_adapter.adapter_name,
            "selected_adapter_name": synthesis_decision.selected_adapter_name,
            "selected_model": synthesis_decision.selected_model,
            "resolved_via_get_adapter": bool(synthesis_resolved_via_registry),
            "fallback_to_passed_adapter": not bool(synthesis_resolved_via_registry),
            "escalation_applied": synthesis_decision.escalation_applied,
            "degradation_applied": synthesis_decision.degradation_applied,
            "routing_evidence": build_routing_evidence(
                routing_request=synthesis_request,
                routing_decision=synthesis_decision,
                executed_adapter_name=synthesis_execution_adapter.adapter_name,
                passed_adapter_name=passed_adapter.adapter_name,
                resolved_via_get_adapter=bool(synthesis_resolved_via_registry),
                fallback_to_passed_adapter=not bool(synthesis_resolved_via_registry),
                bounded_model_call=True,
                skip_reason=None,
            ),
        }
    return {
        "routing_invoked": True,
        "rollup_mode": "slm_only_signal_stage",
        "final_path": final_path.value,
        "synthesis_skipped": True,
        "request": signal_request.model_dump(mode="json"),
        "decision": signal_decision.model_dump(mode="json"),
        "passed_adapter_name": passed_adapter.adapter_name,
        "executed_adapter_name": signal_execution_adapter.adapter_name if signal_resolved else passed_adapter.adapter_name,
        "selected_adapter_name": signal_decision.selected_adapter_name,
        "selected_model": signal_decision.selected_model,
        "resolved_via_get_adapter": signal_resolved,
        "fallback_to_passed_adapter": not signal_resolved,
        "escalation_applied": signal_decision.escalation_applied,
        "degradation_applied": signal_decision.degradation_applied,
        "routing_evidence": build_routing_evidence(
            routing_request=signal_request,
            routing_decision=signal_decision,
            executed_adapter_name=signal_execution_adapter.adapter_name,
            passed_adapter_name=passed_adapter.adapter_name,
            resolved_via_get_adapter=signal_resolved,
            fallback_to_passed_adapter=not signal_resolved,
            bounded_model_call=True,
            skip_reason=None,
        ),
    }


@dataclass
class StagedGenerationResult:
    """Outcome of ``run_runtime_staged_generation`` for the AI turn executor."""

    response: AdapterResponse
    runtime_stage_traces: list[dict[str, Any]] = field(default_factory=list)
    runtime_orchestration_summary: dict[str, Any] = field(default_factory=dict)
    model_routing_trace: dict[str, Any] = field(default_factory=dict)
    operator_audit: dict[str, Any] = field(default_factory=dict)
    synthesis_skipped: bool = False
    final_path: OrchestrationFinalPath = OrchestrationFinalPath.slm_then_llm
    synthesis_attempt_count: int = 0
    final_execution_adapter: StoryAIAdapter | None = None


def _annotate_request_for_stage(
    base: AdapterRequest,
    stage_id: RuntimeStageId,
    *,
    request_role_structured_output: bool,
) -> AdapterRequest:
    meta = dict(base.metadata or {})
    meta[RUNTIME_STAGE_META_KEY] = stage_id.value
    meta[RUNTIME_STAGE_SCHEMA_META_KEY] = RUNTIME_STAGE_SCHEMA_VERSION
    cloned = base.model_copy(
        update={
            "metadata": meta,
            "request_role_structured_output": request_role_structured_output,
        }
    )
    return cloned


def run_runtime_staged_generation(
    *,
    session: SessionState,
    passed_adapter: StoryAIAdapter,
    adapter_generate_timeout_ms: int,
    build_adapter_request_fn: Callable[[int], AdapterRequest],
    enrich_request_fn: Callable[[AdapterRequest], None],
    mark_retry_context_fn: Callable[[], None] | None = None,
) -> StagedGenerationResult:
    """Execute preflight → signal → optional synthesis, or deterministic SLM-only packaging.

    Each stage uses a distinct ``RoutingRequest`` (meaningful phase/task_kind).
    """
    traces: list[dict[str, Any]] = []
    packaging_notes: list[str] = []

    # --- Preflight ---
    preflight_rr = build_preflight_routing_request(session)
    preflight_dec = route_model(preflight_rr)
    preflight_adapter, preflight_resolved = _resolve_routed_adapter(preflight_dec, passed_adapter)
    preflight_out: PreflightStageOutput | None = None
    preflight_errors: list[str] = []
    preflight_skipped = not bool(preflight_dec.selected_adapter_name)

    if preflight_skipped:
        sr = "no_eligible_adapter_for_preflight_stage"
        traces.append(
            _trace_dict_for_stage(
                stage_id=RuntimeStageId.preflight,
                routing_request=preflight_rr,
                routing_decision=preflight_dec,
                passed_adapter=passed_adapter,
                execution_adapter=preflight_adapter,
                resolved_via_registry=preflight_resolved is not None,
                bounded_model_call=False,
                skip_reason=sr,
                output_summary={"skipped": True},
                errors=[sr],
            )
        )
        packaging_notes.append(sr)
    else:
        base_pf = build_adapter_request_fn(1)
        enrich_request_fn(base_pf)
        req_pf = _annotate_request_for_stage(
            base_pf, RuntimeStageId.preflight, request_role_structured_output=False
        )
        resp_pf = generate_with_timeout(
            adapter=preflight_adapter,
            request=req_pf,
            timeout_ms=adapter_generate_timeout_ms,
        )
        preflight_out, preflight_errors = parse_preflight_payload(resp_pf.structured_payload)
        if resp_pf.error or not resp_pf.structured_payload:
            preflight_errors = preflight_errors or ["preflight: adapter error or empty payload"]
            preflight_out = None
        traces.append(
            _trace_dict_for_stage(
                stage_id=RuntimeStageId.preflight,
                routing_request=preflight_rr,
                routing_decision=preflight_dec,
                passed_adapter=passed_adapter,
                execution_adapter=preflight_adapter,
                resolved_via_registry=preflight_resolved is not None,
                bounded_model_call=True,
                skip_reason=None if not resp_pf.error else "preflight_adapter_error",
                output_summary=(
                    preflight_out.model_dump(mode="json") if preflight_out else {"parse_failed": True}
                ),
                errors=preflight_errors,
            )
        )

    preflight_parse_ok = preflight_out is not None and not preflight_errors

    # --- Signal ---
    extra_hints = escalation_hints_from_preflight(preflight_out)
    signal_rr = build_signal_routing_request(session, extra_hints=extra_hints)
    signal_dec = route_model(signal_rr)
    signal_adapter, signal_resolved = _resolve_routed_adapter(signal_dec, passed_adapter)
    signal_out: SignalStageOutput | None = None
    signal_errors: list[str] = []
    signal_skipped = not bool(signal_dec.selected_adapter_name)

    if signal_skipped:
        sr = "no_eligible_adapter_for_signal_stage"
        traces.append(
            _trace_dict_for_stage(
                stage_id=RuntimeStageId.signal_consistency,
                routing_request=signal_rr,
                routing_decision=signal_dec,
                passed_adapter=passed_adapter,
                execution_adapter=signal_adapter,
                resolved_via_registry=signal_resolved is not None,
                bounded_model_call=False,
                skip_reason=sr,
                output_summary={"skipped": True},
                errors=[sr],
            )
        )
        packaging_notes.append(sr)
    else:
        base_sg = build_adapter_request_fn(1)
        enrich_request_fn(base_sg)
        req_sg = _annotate_request_for_stage(
            base_sg, RuntimeStageId.signal_consistency, request_role_structured_output=False
        )
        resp_sg = generate_with_timeout(
            adapter=signal_adapter,
            request=req_sg,
            timeout_ms=adapter_generate_timeout_ms,
        )
        signal_out, signal_errors = parse_signal_payload(resp_sg.structured_payload)
        if resp_sg.error or not resp_sg.structured_payload:
            signal_errors = signal_errors or ["signal: adapter error or empty payload"]
            signal_out = None
        traces.append(
            _trace_dict_for_stage(
                stage_id=RuntimeStageId.signal_consistency,
                routing_request=signal_rr,
                routing_decision=signal_dec,
                passed_adapter=passed_adapter,
                execution_adapter=signal_adapter,
                resolved_via_registry=signal_resolved is not None,
                bounded_model_call=True,
                skip_reason=None if not resp_sg.error else "signal_adapter_error",
                output_summary=(
                    signal_out.model_dump(mode="json") if signal_out else {"parse_failed": True}
                ),
                errors=signal_errors,
            )
        )

    signal_parse_ok = signal_out is not None and not signal_errors

    needs_llm, synth_gate_reason = compute_needs_llm_synthesis(
        signal=signal_out,
        signal_parse_ok=signal_parse_ok,
        preflight_parse_ok=preflight_parse_ok,
    )

    final_path = OrchestrationFinalPath.slm_then_llm
    if preflight_skipped and signal_skipped:
        final_path = OrchestrationFinalPath.degraded_early_skip_then_synthesis
    elif needs_llm and synth_gate_reason.startswith("degraded"):
        final_path = OrchestrationFinalPath.degraded_parse_forced_synthesis

    synthesis_rr: RoutingRequest | None = None
    synthesis_dec: RoutingDecision | None = None
    synthesis_adapter: StoryAIAdapter | None = None
    synthesis_resolved: bool | None = None

    if needs_llm:
        synthesis_rr = build_synthesis_routing_request(session)
        synthesis_dec = route_model(synthesis_rr)
        synthesis_adapter, syn_resolved = _resolve_routed_adapter(synthesis_dec, passed_adapter)
        synthesis_resolved = syn_resolved is not None
        retry_policy = RetryPolicy()
        resp_syn: AdapterResponse | None = None
        syn_attempt = 1
        while syn_attempt <= retry_policy.MAX_RETRIES:
            if syn_attempt > 1 and mark_retry_context_fn is not None:
                mark_retry_context_fn()
            base_syn = build_adapter_request_fn(syn_attempt)
            enrich_request_fn(base_syn)
            req_syn = _annotate_request_for_stage(
                base_syn, RuntimeStageId.synthesis, request_role_structured_output=True
            )
            resp_syn = generate_with_timeout(
                adapter=synthesis_adapter,
                request=req_syn,
                timeout_ms=adapter_generate_timeout_ms,
            )
            has_error = resp_syn.error is not None
            is_empty = not resp_syn.raw_output or not resp_syn.raw_output.strip()
            if has_error or is_empty:
                failure_class = AIFailureClass.ADAPTER_ERROR
                if has_error and isinstance(resp_syn.error, str) and resp_syn.error.startswith(
                    "adapter_generate_timeout:"
                ):
                    failure_class = AIFailureClass.TIMEOUT_OR_EMPTY_RESPONSE
                if (
                    retry_policy.is_retryable_failure(failure_class)
                    and syn_attempt < retry_policy.MAX_RETRIES
                ):
                    syn_attempt += 1
                    continue
            break
        assert resp_syn is not None
        traces.append(
            _trace_dict_for_stage(
                stage_id=RuntimeStageId.synthesis,
                routing_request=synthesis_rr,
                routing_decision=synthesis_dec,
                passed_adapter=passed_adapter,
                execution_adapter=synthesis_adapter,
                resolved_via_registry=synthesis_resolved,
                bounded_model_call=True,
                skip_reason=None if not resp_syn.error else "synthesis_adapter_error",
                output_summary={
                    "raw_output_len": len(resp_syn.raw_output or ""),
                    "synthesis_attempts": syn_attempt,
                },
                errors=[resp_syn.error] if resp_syn.error else [],
            )
        )
        traces.append(
            {
                "stage_id": RuntimeStageId.packaging.value,
                "stage_kind": "packaging",
                "orchestration_role": "passthrough_synthesis_response",
                "bounded_model_call": False,
                "skip_reason": None,
                "output_summary": {"mode": "passthrough_synthesis_response"},
                "errors": [],
            }
        )
        rollup = build_legacy_model_routing_rollup(
            synthesis_ran=True,
            synthesis_request=synthesis_rr,
            synthesis_decision=synthesis_dec,
            synthesis_execution_adapter=synthesis_adapter,
            synthesis_resolved_via_registry=synthesis_resolved,
            passed_adapter=passed_adapter,
            signal_request=signal_rr,
            signal_decision=signal_dec,
            signal_execution_adapter=signal_adapter,
            signal_resolved=signal_resolved is not None,
            final_path=final_path,
        )
        summary = {
            "stages_executed": [t["stage_id"] for t in traces],
            "stages_skipped": [t["stage_id"] for t in traces if not t.get("bounded_model_call")],
            "synthesis_skipped": False,
            "synthesis_gate_reason": synth_gate_reason,
            "final_path": final_path.value,
            "packaging_notes": packaging_notes,
            "staged_pipeline_preempted": None,
        }
        summary.update(runtime_additive_orchestration_fields(traces))
        operator_audit = build_runtime_operator_audit(
            runtime_stage_traces=traces,
            runtime_orchestration_summary=summary,
            model_routing_trace=rollup,
        )
        return StagedGenerationResult(
            response=resp_syn,
            runtime_stage_traces=traces,
            runtime_orchestration_summary=summary,
            model_routing_trace=rollup,
            operator_audit=operator_audit,
            synthesis_skipped=False,
            final_path=final_path,
            synthesis_attempt_count=syn_attempt,
            final_execution_adapter=synthesis_adapter,
        )

    # SLM-only path: synthetic response; signal must be present (forced synthesis if not)
    assert signal_out is not None  # guarded by needs_llm False
    final_path = OrchestrationFinalPath.slm_only
    payload = build_slm_only_structured_payload(preflight=preflight_out, signal=signal_out)
    raw = f"[staged-runtime/slm_only] gate={synth_gate_reason}"
    resp = AdapterResponse(
        raw_output=raw,
        structured_payload=payload,
        backend_metadata={
            "staged_runtime": True,
            "slm_only": True,
            "synthesis_gate_reason": synth_gate_reason,
        },
        error=None,
    )
    traces.append(
        {
            "stage_id": RuntimeStageId.packaging.value,
            "stage_kind": "packaging",
            "orchestration_role": "deterministic_slm_only_structured_payload",
            "bounded_model_call": False,
            "skip_reason": None,
            "output_summary": {"mode": "deterministic_slm_only_structured_payload"},
            "errors": [],
        }
    )
    rollup = build_legacy_model_routing_rollup(
        synthesis_ran=False,
        synthesis_request=None,
        synthesis_decision=None,
        synthesis_execution_adapter=None,
        synthesis_resolved_via_registry=None,
        passed_adapter=passed_adapter,
        signal_request=signal_rr,
        signal_decision=signal_dec,
        signal_execution_adapter=signal_adapter,
        signal_resolved=signal_resolved is not None,
        final_path=final_path,
    )
    summary = {
        "stages_executed": [t["stage_id"] for t in traces],
        "stages_skipped": [t["stage_id"] for t in traces if not t.get("bounded_model_call")],
        "synthesis_skipped": True,
        "synthesis_skip_reason": synth_gate_reason,
        "synthesis_gate_reason": synth_gate_reason,
        "final_path": final_path.value,
        "packaging_notes": packaging_notes,
        "staged_pipeline_preempted": None,
    }
    summary.update(runtime_additive_orchestration_fields(traces))
    operator_audit = build_runtime_operator_audit(
        runtime_stage_traces=traces,
        runtime_orchestration_summary=summary,
        model_routing_trace=rollup,
    )
    return StagedGenerationResult(
        response=resp,
        runtime_stage_traces=traces,
        runtime_orchestration_summary=summary,
        model_routing_trace=rollup,
        operator_audit=operator_audit,
        synthesis_skipped=True,
        final_path=final_path,
        synthesis_attempt_count=0,
        final_execution_adapter=passed_adapter,
    )
