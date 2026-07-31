"""Turn-level model-call accounting at the adapter seam (Wave 0).

Every productive ``BaseModelAdapter.generate`` call is ledgered here so cost
truth does not depend on instrumenting string-shard call sites. Phase names
come from a context-variable stack; when unset, a conservative stack-frame
fallback maps known executor node methods. Remaining calls stay
``unattributed`` — a visible state, never a silent default.
"""
from __future__ import annotations

import inspect
import time
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field
from typing import Any, Iterator

from story_runtime_core.adapters import BaseModelAdapter, ModelCallResult

# Soft budget: warn into ledger/trace. Hard budget: abort further generates.
# Defaults are intentionally generous (A10) until W0 playthrough measures land.
DEFAULT_TURN_CALL_BUDGET_SOFT = 12
DEFAULT_TURN_CALL_BUDGET_HARD = 24

PHASE_UNATTRIBUTED = "unattributed"
PHASE_MODEL_GENERATION = "model_generation"
PHASE_INPUT_TRANSLATION = "input_translation"
PHASE_OUTPUT_TRANSLATION = "output_translation"
PHASE_SELF_CORRECTION = "self_correction"
PHASE_FALLBACK = "fallback"

# Hard per-turn cap for translation-phase model spend (E6). Generous until measured (A10).
DEFAULT_TRANSLATION_CALL_HARD_CAP = 4

_TRANSLATION_PHASES = frozenset({PHASE_INPUT_TRANSLATION, PHASE_OUTPUT_TRANSLATION})

# Frame names (exec'd shard methods) → phase when context var is unset.
_FRAME_PHASE_HINTS: tuple[tuple[str, str], ...] = (
    ("_translate_input", PHASE_INPUT_TRANSLATION),
    ("_translate_output", PHASE_OUTPUT_TRANSLATION),
    ("_generation_self_correction", PHASE_SELF_CORRECTION),
    ("_self_correct", PHASE_SELF_CORRECTION),
    ("_invoke_fallback", PHASE_FALLBACK),
    ("_fallback_model", PHASE_FALLBACK),
    ("_invoke_model", PHASE_MODEL_GENERATION),
    ("_invoke_primary", PHASE_MODEL_GENERATION),
)


@dataclass(frozen=True, slots=True)
class ModelCallPhaseContext:
    phase: str = PHASE_UNATTRIBUTED
    attempt_index: int = 0
    trigger: str = "unspecified"


_phase_stack: ContextVar[tuple[ModelCallPhaseContext, ...]] = ContextVar(
    "model_call_phase_stack",
    default=(),
)
_active_ledger: ContextVar["TurnCallLedger | None"] = ContextVar(
    "model_call_active_ledger",
    default=None,
)
_translation_cache: ContextVar[dict[str, ModelCallResult] | None] = ContextVar(
    "model_call_translation_cache",
    default=None,
)
_translation_call_count: ContextVar[int] = ContextVar(
    "model_call_translation_count",
    default=0,
)


@contextmanager
def model_call_phase(
    phase: str,
    *,
    attempt_index: int = 0,
    trigger: str = "unspecified",
) -> Iterator[ModelCallPhaseContext]:
    """Push a phase context for nested adapter.generate calls."""
    normalized = str(phase or PHASE_UNATTRIBUTED).strip() or PHASE_UNATTRIBUTED
    ctx = ModelCallPhaseContext(
        phase=normalized,
        attempt_index=max(0, int(attempt_index)),
        trigger=str(trigger or "unspecified"),
    )
    token = _phase_stack.set(_phase_stack.get() + (ctx,))
    try:
        yield ctx
    finally:
        _phase_stack.reset(token)


@contextmanager
def bind_turn_call_ledger(ledger: "TurnCallLedger") -> Iterator["TurnCallLedger"]:
    """Bind a ledger for the current turn (tests and production turn entry)."""
    token = _active_ledger.set(ledger)
    cache_token = _translation_cache.set({})
    count_token = _translation_call_count.set(0)
    try:
        yield ledger
    finally:
        _active_ledger.reset(token)
        _translation_cache.reset(cache_token)
        _translation_call_count.reset(count_token)


def current_model_call_phase() -> ModelCallPhaseContext:
    stack = _phase_stack.get()
    if stack:
        return stack[-1]
    return ModelCallPhaseContext()


def _infer_phase_from_stack() -> ModelCallPhaseContext | None:
    for frame_info in inspect.stack()[2:40]:
        name = frame_info.function
        for needle, phase in _FRAME_PHASE_HINTS:
            if needle in name:
                return ModelCallPhaseContext(
                    phase=phase,
                    attempt_index=0,
                    trigger="stack_frame_hint",
                )
    return None


def resolve_model_call_phase() -> ModelCallPhaseContext:
    current = current_model_call_phase()
    if current.phase != PHASE_UNATTRIBUTED:
        return current
    inferred = _infer_phase_from_stack()
    return inferred or current


@dataclass
class TurnCallRecord:
    phase: str
    attempt_index: int
    trigger: str
    model_id: str
    provider: str
    input_tokens: int
    output_tokens: int
    duration_ms: int
    success: bool
    budget_warning: bool = False
    aborted_by_hard_budget: bool = False


@dataclass
class TurnCallLedger:
    """Mutable per-turn ledger of adapter generate calls."""

    soft_budget: int = DEFAULT_TURN_CALL_BUDGET_SOFT
    hard_budget: int = DEFAULT_TURN_CALL_BUDGET_HARD
    records: list[TurnCallRecord] = field(default_factory=list)
    soft_budget_warnings: int = 0
    hard_budget_aborts: int = 0

    def __post_init__(self) -> None:
        self.soft_budget = max(1, int(self.soft_budget))
        self.hard_budget = max(self.soft_budget, int(self.hard_budget))

    @property
    def call_count(self) -> int:
        return len(self.records)

    @property
    def attributed_call_count(self) -> int:
        return sum(1 for record in self.records if record.phase != PHASE_UNATTRIBUTED)

    @property
    def unattributed_call_count(self) -> int:
        return sum(1 for record in self.records if record.phase == PHASE_UNATTRIBUTED)

    def would_exceed_hard_budget(self) -> bool:
        return self.call_count >= self.hard_budget

    def soft_budget_exceeded(self) -> bool:
        return self.call_count >= self.soft_budget

    def record(self, entry: TurnCallRecord) -> None:
        self.records.append(entry)
        if entry.budget_warning:
            self.soft_budget_warnings += 1
        if entry.aborted_by_hard_budget:
            self.hard_budget_aborts += 1

    def records_for_phase(self, phase: str) -> list[TurnCallRecord]:
        return [record for record in self.records if record.phase == phase]

    def to_phase_cost_seed(self) -> dict[str, list[dict[str, Any]]]:
        """Group ledger rows by phase for aggregate_phase_costs consumers."""
        grouped: dict[str, list[dict[str, Any]]] = {}
        for record in self.records:
            grouped.setdefault(record.phase, []).append(
                {
                    "phase": record.phase,
                    "attempt_index": record.attempt_index,
                    "trigger": record.trigger,
                    "model": record.model_id,
                    "provider": record.provider,
                    "input_tokens": record.input_tokens,
                    "output_tokens": record.output_tokens,
                    "latency_ms": record.duration_ms,
                    "success": record.success,
                    "budget_warning": record.budget_warning,
                    "aborted_by_hard_budget": record.aborted_by_hard_budget,
                }
            )
        return grouped

    def summary(self) -> dict[str, Any]:
        return {
            "call_count": self.call_count,
            "attributed_call_count": self.attributed_call_count,
            "unattributed_call_count": self.unattributed_call_count,
            "soft_budget": self.soft_budget,
            "hard_budget": self.hard_budget,
            "soft_budget_warnings": self.soft_budget_warnings,
            "hard_budget_aborts": self.hard_budget_aborts,
            "soft_budget_exceeded": self.soft_budget_exceeded(),
            "phases": sorted({record.phase for record in self.records}),
        }


class HardBudgetExceeded(RuntimeError):
    """Raised when a generate would exceed the hard per-turn call budget."""

    def __init__(self, ledger: TurnCallLedger) -> None:
        self.ledger = ledger
        super().__init__(
            f"turn_call_budget_hard exceeded: calls={ledger.call_count} hard={ledger.hard_budget}"
        )


def _tokens_from_metadata(metadata: dict[str, Any] | None) -> tuple[int, int]:
    meta = metadata if isinstance(metadata, dict) else {}
    usage = meta.get("usage_details") if isinstance(meta.get("usage_details"), dict) else {}
    input_tokens = int(usage.get("input") or meta.get("tokens_prompt") or meta.get("input_tokens") or 0)
    output_tokens = int(
        usage.get("output") or meta.get("tokens_completion") or meta.get("output_tokens") or 0
    )
    return max(0, input_tokens), max(0, output_tokens)


class CountingModelAdapter(BaseModelAdapter):
    """Transparent generate wrapper that writes every call into the active ledger."""

    def __init__(self, inner: BaseModelAdapter, *, ledger: TurnCallLedger | None = None) -> None:
        self._inner = inner
        self._ledger = ledger
        self.adapter_name = getattr(inner, "adapter_name", type(inner).__name__)

    @property
    def inner(self) -> BaseModelAdapter:
        return self._inner

    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)

    def _resolve_ledger(self) -> TurnCallLedger | None:
        return self._ledger if self._ledger is not None else _active_ledger.get()

    def generate(
        self,
        prompt: str,
        *,
        timeout_seconds: float = 10.0,
        retrieval_context: str | None = None,
        model_name: str | None = None,
    ) -> ModelCallResult:
        ledger = self._resolve_ledger()
        phase_ctx = resolve_model_call_phase()
        budget_warning = False
        cache = _translation_cache.get()
        is_translation = phase_ctx.phase in _TRANSLATION_PHASES

        # Identical translation prompts reuse the in-turn cache (E6) before budgets.
        if is_translation and isinstance(cache, dict) and prompt in cache:
            return cache[prompt]

        if ledger is not None:
            if ledger.would_exceed_hard_budget():
                aborted = TurnCallRecord(
                    phase=phase_ctx.phase,
                    attempt_index=phase_ctx.attempt_index,
                    trigger=phase_ctx.trigger,
                    model_id=str(model_name or getattr(self._inner, "model_name", "") or ""),
                    provider=str(getattr(self._inner, "adapter_name", self.adapter_name) or ""),
                    input_tokens=0,
                    output_tokens=0,
                    duration_ms=0,
                    success=False,
                    budget_warning=ledger.soft_budget_exceeded(),
                    aborted_by_hard_budget=True,
                )
                ledger.record(aborted)
                raise HardBudgetExceeded(ledger)
            if ledger.call_count + 1 > ledger.soft_budget:
                budget_warning = True

        if is_translation:
            used = int(_translation_call_count.get() or 0)
            if used >= DEFAULT_TRANSLATION_CALL_HARD_CAP:
                raise HardBudgetExceeded(ledger or TurnCallLedger(soft_budget=1, hard_budget=1))

        started = time.perf_counter()
        result = self._inner.generate(
            prompt,
            timeout_seconds=timeout_seconds,
            retrieval_context=retrieval_context,
            model_name=model_name,
        )
        duration_ms = int((time.perf_counter() - started) * 1000)
        if is_translation and isinstance(cache, dict):
            cache[prompt] = result
            _translation_call_count.set(int(_translation_call_count.get() or 0) + 1)
        if ledger is None:
            return result

        meta = result.metadata if isinstance(result.metadata, dict) else {}
        input_tokens, output_tokens = _tokens_from_metadata(meta)
        model_id = str(
            model_name
            or meta.get("model")
            or meta.get("model_name")
            or getattr(self._inner, "model_name", "")
            or ""
        )
        provider = str(
            meta.get("provider")
            or meta.get("adapter")
            or getattr(self._inner, "adapter_name", self.adapter_name)
            or ""
        )
        ledger.record(
            TurnCallRecord(
                phase=phase_ctx.phase,
                attempt_index=phase_ctx.attempt_index,
                trigger=phase_ctx.trigger,
                model_id=model_id,
                provider=provider,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                duration_ms=duration_ms,
                success=bool(result.success),
                budget_warning=budget_warning,
            )
        )
        return result


def wrap_adapters_with_counting(
    adapters: dict[str, BaseModelAdapter],
    *,
    ledger: TurnCallLedger | None = None,
) -> dict[str, BaseModelAdapter]:
    """Wrap each adapter once; already-wrapped adapters are left unchanged."""
    wrapped: dict[str, BaseModelAdapter] = {}
    for key, adapter in adapters.items():
        if isinstance(adapter, CountingModelAdapter):
            wrapped[key] = adapter
        else:
            wrapped[key] = CountingModelAdapter(adapter, ledger=ledger)
    return wrapped


def merge_ledger_into_phase_costs(
    phase_costs: dict[str, Any] | None,
    ledger: TurnCallLedger | None,
) -> dict[str, Any]:
    """Merge ledger rows into phase_costs without dropping legacy model_generation."""
    merged: dict[str, Any] = dict(phase_costs or {})
    if ledger is None:
        return merged
    for phase, rows in ledger.to_phase_cost_seed().items():
        if phase == PHASE_UNATTRIBUTED:
            merged.setdefault(PHASE_UNATTRIBUTED, {"phase": PHASE_UNATTRIBUTED, "calls": rows})
            continue
        if len(rows) == 1:
            row = dict(rows[0])
            existing = merged.get(phase) if isinstance(merged.get(phase), dict) else {}
            merged[phase] = {**existing, **row, "call_count": 1}
        else:
            merged[phase] = {
                "phase": phase,
                "call_count": len(rows),
                "attempt_indexes": [row["attempt_index"] for row in rows],
                "calls": rows,
                "input_tokens": sum(int(row["input_tokens"]) for row in rows),
                "output_tokens": sum(int(row["output_tokens"]) for row in rows),
            }
    merged["_ledger_summary"] = ledger.summary()
    return merged


__all__ = [
    "DEFAULT_TURN_CALL_BUDGET_HARD",
    "DEFAULT_TURN_CALL_BUDGET_SOFT",
    "CountingModelAdapter",
    "HardBudgetExceeded",
    "PHASE_FALLBACK",
    "PHASE_INPUT_TRANSLATION",
    "PHASE_MODEL_GENERATION",
    "PHASE_OUTPUT_TRANSLATION",
    "PHASE_SELF_CORRECTION",
    "PHASE_UNATTRIBUTED",
    "TurnCallLedger",
    "TurnCallRecord",
    "bind_turn_call_ledger",
    "current_model_call_phase",
    "merge_ledger_into_phase_costs",
    "model_call_phase",
    "resolve_model_call_phase",
    "wrap_adapters_with_counting",
]
