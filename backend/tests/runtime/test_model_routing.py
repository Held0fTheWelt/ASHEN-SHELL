"""Tests for Task 2A model routing core and registry-backed specs."""

import pytest

from app.runtime.adapter_registry import (
    clear_registry,
    get_adapter,
    get_model_spec,
    iter_model_specs,
    register_adapter,
    register_adapter_model,
)
from app.runtime.ai_adapter import AdapterResponse, StoryAIAdapter
from app.runtime.model_routing import TASK_ROUTING_MODE, route_model
from app.runtime.model_routing_contracts import (
    AdapterModelSpec,
    CostClass,
    EscalationHint,
    LLMOrSLM,
    LatencyClass,
    ModelTier,
    RoutingRequest,
    StructuredOutputReliability,
    TaskKind,
    TaskRoutingMode,
    WorkflowPhase,
)


class NamedAdapter(StoryAIAdapter):
    def __init__(self, name: str):
        self._name = name

    @property
    def adapter_name(self) -> str:
        return self._name

    def generate(self, request):
        return AdapterResponse(raw_output="ok")


ALL_PHASES = frozenset(WorkflowPhase)


def _spec(
    *,
    name: str,
    provider: str,
    model: str,
    role: LLMOrSLM,
    tier: ModelTier,
    tasks: frozenset[TaskKind],
    structured: StructuredOutputReliability = StructuredOutputReliability.high,
    degrade: list[str] | None = None,
    cost: CostClass = CostClass.low,
    latency: LatencyClass = LatencyClass.low,
    priority: int = 0,
) -> AdapterModelSpec:
    return AdapterModelSpec(
        adapter_name=name,
        provider_name=provider,
        model_name=model,
        model_tier=tier,
        llm_or_slm=role,
        cost_class=cost,
        latency_class=latency,
        supported_phases=ALL_PHASES,
        supported_task_kinds=tasks,
        structured_output_reliability=structured,
        fallback_priority=priority,
        degrade_targets=degrade or [],
    )


def test_task_routing_mode_covers_all_task_kinds():
    assert set(TaskKind) == set(TASK_ROUTING_MODE.keys())


def test_multiple_specs_same_provider_different_models():
    clear_registry()
    slm = _spec(
        name="acme_small",
        provider="acme",
        model="small-v1",
        role=LLMOrSLM.slm,
        tier=ModelTier.light,
        tasks=frozenset({TaskKind.classification}),
    )
    llm = _spec(
        name="acme_large",
        provider="acme",
        model="large-v2",
        role=LLMOrSLM.llm,
        tier=ModelTier.premium,
        tasks=frozenset({TaskKind.classification}),
    )
    register_adapter_model(slm, NamedAdapter("acme_small"))
    register_adapter_model(llm, NamedAdapter("acme_large"))
    assert len(iter_model_specs()) == 2
    assert get_model_spec("acme_small").model_name == "small-v1"
    assert get_model_spec("acme_large").model_name == "large-v2"


def test_slm_first_selects_slm_when_available():
    clear_registry()
    slm = _spec(
        name="slm_a",
        provider="p",
        model="m1",
        role=LLMOrSLM.slm,
        tier=ModelTier.light,
        tasks=frozenset({TaskKind.classification}),
        priority=1,
    )
    llm = _spec(
        name="llm_a",
        provider="p",
        model="m2",
        role=LLMOrSLM.llm,
        tier=ModelTier.premium,
        tasks=frozenset({TaskKind.classification}),
        priority=99,
    )
    register_adapter_model(slm, NamedAdapter("slm_a"))
    register_adapter_model(llm, NamedAdapter("llm_a"))
    req = RoutingRequest(
        workflow_phase=WorkflowPhase.preflight,
        task_kind=TaskKind.classification,
    )
    d = route_model(req)
    assert d.selected_adapter_name == "slm_a"
    assert d.decision_factors["task_routing_mode"] == TaskRoutingMode.slm_first.value
    assert TASK_ROUTING_MODE[TaskKind.classification] == TaskRoutingMode.slm_first


def test_llm_first_selects_llm_when_available():
    clear_registry()
    slm = _spec(
        name="slm_b",
        provider="p",
        model="m1",
        role=LLMOrSLM.slm,
        tier=ModelTier.light,
        tasks=frozenset({TaskKind.scene_direction}),
    )
    llm = _spec(
        name="llm_b",
        provider="p",
        model="m2",
        role=LLMOrSLM.llm,
        tier=ModelTier.standard,
        tasks=frozenset({TaskKind.scene_direction}),
    )
    register_adapter_model(slm, NamedAdapter("slm_b"))
    register_adapter_model(llm, NamedAdapter("llm_b"))
    d = route_model(
        RoutingRequest(
            workflow_phase=WorkflowPhase.generation,
            task_kind=TaskKind.scene_direction,
        )
    )
    assert d.selected_adapter_name == "llm_b"


def test_escalation_sensitive_with_hints_prefers_llm():
    clear_registry()
    slm = _spec(
        name="slm_c",
        provider="p",
        model="fast",
        role=LLMOrSLM.slm,
        tier=ModelTier.light,
        tasks=frozenset({TaskKind.ambiguity_resolution}),
    )
    llm = _spec(
        name="llm_c",
        provider="p",
        model="smart",
        role=LLMOrSLM.llm,
        tier=ModelTier.standard,
        tasks=frozenset({TaskKind.ambiguity_resolution}),
    )
    register_adapter_model(slm, NamedAdapter("slm_c"))
    register_adapter_model(llm, NamedAdapter("llm_c"))
    d = route_model(
        RoutingRequest(
            workflow_phase=WorkflowPhase.interpretation,
            task_kind=TaskKind.ambiguity_resolution,
            escalation_hints=[EscalationHint.prefer_llm],
        )
    )
    assert d.selected_adapter_name == "llm_c"
    assert d.escalation_applied is True
    assert d.route_reason_code.value == "escalation_applied"


def test_requires_structured_output_drops_low_reliability():
    clear_registry()
    low = _spec(
        name="cheap_slm",
        provider="p",
        model="x",
        role=LLMOrSLM.slm,
        tier=ModelTier.light,
        tasks=frozenset({TaskKind.ranking}),
        structured=StructuredOutputReliability.low,
        priority=100,
    )
    high = _spec(
        name="good_slm",
        provider="p",
        model="y",
        role=LLMOrSLM.slm,
        tier=ModelTier.light,
        tasks=frozenset({TaskKind.ranking}),
        structured=StructuredOutputReliability.high,
        priority=1,
    )
    register_adapter_model(low, NamedAdapter("cheap_slm"))
    register_adapter_model(high, NamedAdapter("good_slm"))
    d_loose = route_model(
        RoutingRequest(
            workflow_phase=WorkflowPhase.preflight,
            task_kind=TaskKind.ranking,
            requires_structured_output=False,
        )
    )
    d_strict = route_model(
        RoutingRequest(
            workflow_phase=WorkflowPhase.preflight,
            task_kind=TaskKind.ranking,
            requires_structured_output=True,
        )
    )
    assert d_loose.selected_adapter_name == "cheap_slm"
    assert d_strict.selected_adapter_name == "good_slm"
    assert d_strict.route_reason_code.value == "structured_output_required"
    assert d_strict.degradation_applied is True


def test_fallback_chain_filters_missing_and_phase_task():
    clear_registry()
    primary = _spec(
        name="primary_route",
        provider="p",
        model="a",
        role=LLMOrSLM.llm,
        tier=ModelTier.premium,
        tasks=frozenset({TaskKind.narrative_formulation}),
        degrade=["missing", "fallback_ok", "wrong_task"],
        priority=5,
    )
    fb = _spec(
        name="fallback_ok",
        provider="p",
        model="b",
        role=LLMOrSLM.llm,
        tier=ModelTier.light,
        tasks=frozenset({TaskKind.narrative_formulation}),
        priority=0,
    )
    wrong = _spec(
        name="wrong_task",
        provider="p",
        model="c",
        role=LLMOrSLM.llm,
        tier=ModelTier.light,
        tasks=frozenset({TaskKind.classification}),
        priority=0,
    )
    register_adapter_model(primary, NamedAdapter("primary_route"))
    register_adapter_model(fb, NamedAdapter("fallback_ok"))
    register_adapter_model(wrong, NamedAdapter("wrong_task"))
    d = route_model(
        RoutingRequest(
            workflow_phase=WorkflowPhase.generation,
            task_kind=TaskKind.narrative_formulation,
        )
    )
    assert d.fallback_chain == ["fallback_ok"]


def test_allow_fallback_false_clears_chain():
    clear_registry()
    p = _spec(
        name="p_only",
        provider="p",
        model="a",
        role=LLMOrSLM.llm,
        tier=ModelTier.standard,
        tasks=frozenset({TaskKind.revision_synthesis}),
        degrade=["fb"],
    )
    register_adapter_model(
        _spec(
            name="fb",
            provider="p",
            model="b",
            role=LLMOrSLM.slm,
            tier=ModelTier.light,
            tasks=frozenset({TaskKind.revision_synthesis}),
        ),
        NamedAdapter("fb"),
    )
    register_adapter_model(p, NamedAdapter("p_only"))
    d = route_model(
        RoutingRequest(
            workflow_phase=WorkflowPhase.revision,
            task_kind=TaskKind.revision_synthesis,
            allow_fallback=False,
        )
    )
    assert d.fallback_chain == []


def test_legacy_get_adapter_after_register_adapter_model():
    clear_registry()
    spec = _spec(
        name="legacy_check",
        provider="x",
        model="m",
        role=LLMOrSLM.slm,
        tier=ModelTier.light,
        tasks=frozenset({TaskKind.cheap_preflight}),
    )
    ad = NamedAdapter("legacy_check")
    register_adapter_model(spec, ad)
    assert get_adapter("legacy_check") is ad


def test_register_adapter_without_spec_not_in_iter_model_specs():
    clear_registry()
    register_adapter("bare", NamedAdapter("bare"))
    assert get_adapter("bare") is not None
    assert iter_model_specs() == []


def test_clear_registry_clears_specs_and_adapters():
    clear_registry()
    spec = _spec(
        name="tmp",
        provider="p",
        model="m",
        role=LLMOrSLM.slm,
        tier=ModelTier.light,
        tasks=frozenset({TaskKind.cheap_preflight}),
    )
    register_adapter_model(spec, NamedAdapter("tmp"))
    register_adapter("other", NamedAdapter("other"))
    clear_registry()
    assert get_adapter("tmp") is None
    assert get_model_spec("tmp") is None
    assert get_adapter("other") is None


def test_register_adapter_model_rejects_name_mismatch():
    clear_registry()
    spec = _spec(
        name="right",
        provider="p",
        model="m",
        role=LLMOrSLM.slm,
        tier=ModelTier.light,
        tasks=frozenset({TaskKind.cheap_preflight}),
    )
    with pytest.raises(ValueError, match="adapter.adapter_name must match"):
        register_adapter_model(spec, NamedAdapter("wrong"))


def test_no_eligible_adapter_empty_decision():
    clear_registry()
    d = route_model(
        RoutingRequest(
            workflow_phase=WorkflowPhase.qa,
            task_kind=TaskKind.scene_direction,
        )
    )
    assert d.selected_adapter_name == ""
    assert d.route_reason_code.value == "no_eligible_adapter"
