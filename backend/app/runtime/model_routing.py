"""Task 2A ? Deterministic model routing policy (explicit role matrix).

Selects a registered adapter name from ``AdapterModelSpec`` metadata only (no
provider-only shortcuts). Runtime execution still uses ``get_adapter``; wiring
into ``turn_dispatcher`` is deferred to Task 2B.
"""

from __future__ import annotations

from collections.abc import Sequence

from app.runtime import adapter_registry
from app.runtime.model_routing_contracts import (
    AdapterModelSpec,
    CostClass,
    CostSensitivity,
    LatencyBudget,
    LatencyClass,
    LLMOrSLM,
    RouteReasonCode,
    RoutingDecision,
    RoutingRequest,
    StructuredOutputReliability,
    TaskKind,
    TaskRoutingMode,
    model_tier_rank,
)

TASK_ROUTING_MODE: dict[TaskKind, TaskRoutingMode] = {
    TaskKind.classification: TaskRoutingMode.slm_first,
    TaskKind.trigger_signal_extraction: TaskRoutingMode.slm_first,
    TaskKind.repetition_consistency_check: TaskRoutingMode.slm_first,
    TaskKind.ranking: TaskRoutingMode.slm_first,
    TaskKind.cheap_preflight: TaskRoutingMode.slm_first,
    TaskKind.scene_direction: TaskRoutingMode.llm_first,
    TaskKind.conflict_synthesis: TaskRoutingMode.llm_first,
    TaskKind.narrative_formulation: TaskRoutingMode.llm_first,
    TaskKind.social_narrative_tradeoff: TaskRoutingMode.llm_first,
    TaskKind.revision_synthesis: TaskRoutingMode.llm_first,
    TaskKind.ambiguity_resolution: TaskRoutingMode.escalation_sensitive,
    TaskKind.continuity_judgment: TaskRoutingMode.escalation_sensitive,
    TaskKind.high_stakes_narrative_tradeoff: TaskRoutingMode.escalation_sensitive,
}


def _latency_rank(spec: AdapterModelSpec) -> int:
    return {LatencyClass.low: 0, LatencyClass.medium: 1, LatencyClass.high: 2}[spec.latency_class]


def _cost_rank(spec: AdapterModelSpec) -> int:
    return {CostClass.low: 0, CostClass.medium: 1, CostClass.high: 2}[spec.cost_class]


def _latency_alignment(spec: AdapterModelSpec, budget: LatencyBudget) -> int:
    r = _latency_rank(spec)
    if budget == LatencyBudget.strict:
        return 10 - r
    if budget == LatencyBudget.relaxed:
        return r + 4
    return 7 - r // 2


def _cost_alignment(spec: AdapterModelSpec, sens: CostSensitivity) -> int:
    r = _cost_rank(spec)
    if sens == CostSensitivity.high:
        return 10 - r
    if sens == CostSensitivity.low:
        return r + 4
    return 7 - r // 2


def _filter_eligible(
    specs: Sequence[AdapterModelSpec],
    request: RoutingRequest,
    *,
    require_structured: bool,
) -> list[AdapterModelSpec]:
    out: list[AdapterModelSpec] = []
    for spec in specs:
        if request.workflow_phase not in spec.supported_phases:
            continue
        if request.task_kind not in spec.supported_task_kinds:
            continue
        if require_structured and spec.structured_output_reliability == StructuredOutputReliability.low:
            continue
        out.append(spec)
    return out


def _preferred_pool(
    eligible: list[AdapterModelSpec],
    request: RoutingRequest,
) -> tuple[list[AdapterModelSpec], bool]:
    """Return (pool, widened). widened=True when the preferred model class had no candidates."""
    mode = TASK_ROUTING_MODE[request.task_kind]
    hints = request.escalation_hints

    if mode == TaskRoutingMode.slm_first:
        slms = [s for s in eligible if s.llm_or_slm == LLMOrSLM.slm]
        if slms:
            return slms, False
        return eligible, True

    if mode == TaskRoutingMode.llm_first:
        llms = [s for s in eligible if s.llm_or_slm == LLMOrSLM.llm]
        if llms:
            return llms, False
        return eligible, True

    if hints:
        llms = [s for s in eligible if s.llm_or_slm == LLMOrSLM.llm]
        if llms:
            return llms, False
        return eligible, True

    llms = [s for s in eligible if s.llm_or_slm == LLMOrSLM.llm]
    if llms:
        return llms, False
    return eligible, True


def _pick_slm(request: RoutingRequest, pool: list[AdapterModelSpec]) -> AdapterModelSpec:
    return min(
        pool,
        key=lambda s: (
            model_tier_rank(s.model_tier),
            -_latency_alignment(s, request.latency_budget),
            -_cost_alignment(s, request.cost_sensitivity),
            -s.fallback_priority,
            s.adapter_name.lower(),
        ),
    )


def _pick_llm(request: RoutingRequest, pool: list[AdapterModelSpec]) -> AdapterModelSpec:
    return max(
        pool,
        key=lambda s: (
            model_tier_rank(s.model_tier),
            _latency_alignment(s, request.latency_budget),
            _cost_alignment(s, request.cost_sensitivity),
            s.fallback_priority,
            s.adapter_name.lower(),
        ),
    )


def _pick_primary(pool: list[AdapterModelSpec], request: RoutingRequest) -> AdapterModelSpec:
    mode = TASK_ROUTING_MODE[request.task_kind]
    has_slm = any(s.llm_or_slm == LLMOrSLM.slm for s in pool)
    if mode == TaskRoutingMode.slm_first and has_slm:
        return _pick_slm(request, pool)
    return _pick_llm(request, pool)


def _spec_by_name(specs: Sequence[AdapterModelSpec]) -> dict[str, AdapterModelSpec]:
    return {s.adapter_name.lower(): s for s in specs}


def _build_fallback_chain(
    primary: AdapterModelSpec,
    request: RoutingRequest,
    by_name: dict[str, AdapterModelSpec],
) -> list[str]:
    if not request.allow_fallback:
        return []
    out: list[str] = []
    for target in primary.degrade_targets:
        spec = by_name.get(target.lower())
        if spec is None:
            continue
        if request.workflow_phase not in spec.supported_phases:
            continue
        if request.task_kind not in spec.supported_task_kinds:
            continue
        if request.requires_structured_output and spec.structured_output_reliability == StructuredOutputReliability.low:
            continue
        out.append(spec.adapter_name)
    return out


def _escalation_applied(
    eligible: list[AdapterModelSpec],
    primary: AdapterModelSpec,
    request: RoutingRequest,
) -> bool:
    mode = TASK_ROUTING_MODE[request.task_kind]
    if mode != TaskRoutingMode.escalation_sensitive:
        return False
    if not request.escalation_hints:
        return False
    had_slm = any(s.llm_or_slm == LLMOrSLM.slm for s in eligible)
    return had_slm and primary.llm_or_slm == LLMOrSLM.llm


def route_model(
    request: RoutingRequest,
    *,
    specs: Sequence[AdapterModelSpec] | None = None,
) -> RoutingDecision:
    """Return a deterministic routing decision for ``request``.

    If ``specs`` is None, uses ``adapter_registry.iter_model_specs()``.
    """
    spec_list = list(specs) if specs is not None else adapter_registry.iter_model_specs()
    eligible_all = _filter_eligible(spec_list, request, require_structured=False)
    eligible = _filter_eligible(spec_list, request, require_structured=request.requires_structured_output)

    factors: dict[str, object] = {
        "task_routing_mode": TASK_ROUTING_MODE[request.task_kind].value,
        "candidate_count_after_phase_task": len(eligible_all),
        "candidate_count_after_structured_filter": len(eligible),
        "requires_structured_output": request.requires_structured_output,
    }

    if not eligible:
        factors["failure"] = "no_eligible_adapter"
        return RoutingDecision(
            selected_adapter_name="",
            selected_provider="",
            selected_model="",
            phase=request.workflow_phase,
            task_kind=request.task_kind,
            route_reason_code=RouteReasonCode.no_eligible_adapter,
            decision_factors=factors,
            fallback_chain=[],
            escalation_applied=False,
            degradation_applied=bool(eligible_all),
        )

    pool, widened = _preferred_pool(eligible, request)
    factors["preferred_pool_widened"] = widened
    primary = _pick_primary(pool, request)
    by_name = _spec_by_name(spec_list)
    chain = _build_fallback_chain(primary, request, by_name)

    esc = _escalation_applied(eligible, primary, request)
    structured_shaped = request.requires_structured_output and len(eligible) < len(eligible_all)
    degradation = widened or structured_shaped

    if esc:
        code = RouteReasonCode.escalation_applied
    elif structured_shaped:
        code = RouteReasonCode.structured_output_required
    else:
        code = RouteReasonCode.role_matrix_primary

    factors["selected_llm_or_slm"] = primary.llm_or_slm.value
    factors["escalation_hints"] = [h.value for h in request.escalation_hints]

    return RoutingDecision(
        selected_adapter_name=primary.adapter_name,
        selected_provider=primary.provider_name,
        selected_model=primary.model_name,
        phase=request.workflow_phase,
        task_kind=request.task_kind,
        route_reason_code=code,
        decision_factors=factors,
        fallback_chain=chain,
        escalation_applied=esc,
        degradation_applied=degradation,
    )
