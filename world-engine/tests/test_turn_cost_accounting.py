"""Wave 0 characterization + target tests for turn cost accounting."""
from __future__ import annotations

import pytest
from story_runtime_core.adapters import BaseModelAdapter, MockModelAdapter, ModelCallResult
from story_runtime_core.model_call_accounting import (
    CountingModelAdapter,
    HardBudgetExceeded,
    PHASE_MODEL_GENERATION,
    PHASE_SELF_CORRECTION,
    TurnCallLedger,
    bind_turn_call_ledger,
    merge_ledger_into_phase_costs,
    model_call_phase,
    wrap_adapters_with_counting,
)
from ai_stack.telemetry.runtime_cost_attribution import aggregate_phase_costs
from app.story_runtime.governed_runtime_adapters import build_governed_model_adapters


class _CountingProbeAdapter(BaseModelAdapter):
    adapter_name = "probe"

    def __init__(self) -> None:
        self.calls = 0

    def generate(
        self,
        prompt: str,
        *,
        timeout_seconds: float = 10.0,
        retrieval_context: str | None = None,
        model_name: str | None = None,
    ) -> ModelCallResult:
        self.calls += 1
        return ModelCallResult(
            content='{"narrative_response":"ok"}',
            success=True,
            metadata={
                "adapter": self.adapter_name,
                "model": model_name or "probe-model",
                "usage_details": {"input": 10, "output": 5},
            },
        )


def test_characterization_phase_costs_today_center_on_model_generation() -> None:
    """Pre-Wave-0 truth: legacy builder only seeds model_generation from path_summary."""
    from app.story_runtime.manager.model_costs_and_path_core import (
        _build_model_generation_phase_cost,
    )

    graph_state = {
        "generation": {
            "attempted": True,
            "metadata": {
                "adapter": "mock",
                "model": "mock",
                "usage_details": {"input": 0, "output": 0},
            },
        },
        "routing": {"selected_provider": "mock", "selected_model": "mock"},
    }
    phase_cost = _build_model_generation_phase_cost(graph_state)
    assert phase_cost is not None
    assert phase_cost["phase"] == "model_generation"
    # Characterization: no call_count / attempt_index on the legacy builder output.
    assert "attempt_index" not in phase_cost or phase_cost.get("attempt_index") is None


def test_every_model_call_is_ledgered() -> None:
    ledger = TurnCallLedger(soft_budget=10, hard_budget=20)
    adapter = CountingModelAdapter(_CountingProbeAdapter(), ledger=ledger)
    with model_call_phase(PHASE_MODEL_GENERATION, attempt_index=0, trigger="primary"):
        adapter.generate("primary")
    with model_call_phase("output_translation", attempt_index=0, trigger="translate"):
        adapter.generate("translate")
    with model_call_phase(PHASE_SELF_CORRECTION, attempt_index=0, trigger="retry"):
        adapter.generate("retry")

    assert ledger.call_count == 3
    assert ledger.attributed_call_count == 3
    assert ledger.unattributed_call_count == 0
    aggregated = aggregate_phase_costs(merge_ledger_into_phase_costs({}, ledger))
    assert aggregated["call_count"] == 3
    assert aggregated["attributed_call_count"] == 3
    assert aggregated["unattributed_call_count"] == 0


def test_self_correction_attempts_are_separately_costed() -> None:
    ledger = TurnCallLedger()
    adapter = CountingModelAdapter(_CountingProbeAdapter(), ledger=ledger)
    for attempt in range(3):
        with model_call_phase(PHASE_SELF_CORRECTION, attempt_index=attempt, trigger="self_correction"):
            adapter.generate(f"attempt-{attempt}")
    records = ledger.records_for_phase(PHASE_SELF_CORRECTION)
    assert [record.attempt_index for record in records] == [0, 1, 2]


def test_soft_budget_warns_without_aborting() -> None:
    ledger = TurnCallLedger(soft_budget=2, hard_budget=10)
    adapter = CountingModelAdapter(_CountingProbeAdapter(), ledger=ledger)
    with model_call_phase(PHASE_MODEL_GENERATION):
        adapter.generate("1")
        adapter.generate("2")
        adapter.generate("3")  # crosses soft budget
    assert ledger.call_count == 3
    assert ledger.soft_budget_warnings >= 1
    assert ledger.hard_budget_aborts == 0
    assert any(record.budget_warning for record in ledger.records)


def test_hard_budget_aborts() -> None:
    ledger = TurnCallLedger(soft_budget=1, hard_budget=2)
    adapter = CountingModelAdapter(_CountingProbeAdapter(), ledger=ledger)
    with model_call_phase(PHASE_MODEL_GENERATION):
        adapter.generate("1")
        adapter.generate("2")
        with pytest.raises(HardBudgetExceeded):
            adapter.generate("3")
    assert ledger.hard_budget_aborts == 1
    assert ledger.call_count == 3  # includes aborted ledger row


def test_build_governed_adapters_wrap_with_counting() -> None:
    adapters = build_governed_model_adapters({"providers": [{"provider_id": "mock", "provider_type": "mock"}]})
    assert "mock" in adapters
    assert isinstance(adapters["mock"], CountingModelAdapter)
    assert isinstance(adapters["mock"].inner, MockModelAdapter)


def test_bind_ledger_context_records_without_explicit_ledger_ctor() -> None:
    inner = _CountingProbeAdapter()
    adapters = wrap_adapters_with_counting({"probe": inner})
    ledger = TurnCallLedger()
    with bind_turn_call_ledger(ledger):
        with model_call_phase(PHASE_MODEL_GENERATION, attempt_index=0):
            adapters["probe"].generate("hello")
    assert ledger.call_count == 1
    assert ledger.records[0].phase == PHASE_MODEL_GENERATION
