"""Runtime phase token/cost attribution helpers.

Phase B tracks cost truth, not forced cost: deterministic and mock paths are
allowed to report zero tokens/cost when the provenance says why.
"""

from __future__ import annotations

from typing import Any


ZERO_COST_PRICING_SOURCE = "no_provider_call"
ESTIMATED_PRICING_SOURCE = "static_pricing_table_v1"


def _non_negative_int(value: Any) -> int:
    try:
        return max(0, int(value or 0))
    except (TypeError, ValueError):
        return 0


def _non_negative_float(value: Any) -> float:
    try:
        return max(0.0, float(value or 0.0))
    except (TypeError, ValueError):
        return 0.0


def calculate_token_cost(
    model: str,
    input_tokens: int,
    output_tokens: int,
    *,
    provider: str | None = None,
) -> tuple[float, str]:
    """Return estimated USD cost and pricing source for known model families."""
    model_key = str(model or "").lower()
    provider_key = str(provider or "").lower()
    input_count = _non_negative_int(input_tokens)
    output_count = _non_negative_int(output_tokens)
    pricing = {
        "claude-3-sonnet": {"input": 0.003, "output": 0.015},
        "claude-3-opus": {"input": 0.015, "output": 0.075},
        "claude-3-haiku": {"input": 0.00025, "output": 0.00125},
        "gpt-4-turbo": {"input": 0.01, "output": 0.03},
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
    }
    for known_model, rates in pricing.items():
        if known_model in model_key:
            cost = ((input_count / 1000.0) * rates["input"]) + ((output_count / 1000.0) * rates["output"])
            return round(cost, 6), ESTIMATED_PRICING_SOURCE
    if provider_key in {"world_engine", "deterministic", "mock"} or (input_count == 0 and output_count == 0):
        return 0.0, ZERO_COST_PRICING_SOURCE
    return 0.0, "pricing_unavailable"


def build_phase_cost(
    *,
    phase: str,
    billing_mode: str,
    token_source: str,
    billable: bool,
    input_tokens: int = 0,
    output_tokens: int = 0,
    cost_usd: float = 0.0,
    provider: str = "",
    model: str = "",
    currency: str = "USD",
    pricing_source: str = "",
    latency_ms: int | None = None,
    **extra: Any,
) -> dict[str, Any]:
    record: dict[str, Any] = {
        "phase": str(phase or "").strip(),
        "billing_mode": str(billing_mode or "").strip(),
        "token_source": str(token_source or "").strip(),
        "billable": bool(billable),
        "input_tokens": _non_negative_int(input_tokens),
        "output_tokens": _non_negative_int(output_tokens),
        "cost_usd": round(_non_negative_float(cost_usd), 6),
        "provider": str(provider or "").strip(),
        "model": str(model or "").strip(),
        "currency": currency or "USD",
        "pricing_source": str(pricing_source or "").strip(),
        "latency_ms": None if latency_ms is None else _non_negative_int(latency_ms),
    }
    record.update({key: value for key, value in extra.items() if value is not None})
    return record


def build_deterministic_phase_cost(
    *,
    phase: str,
    model: str,
    provider: str = "world_engine",
    **extra: Any,
) -> dict[str, Any]:
    return build_phase_cost(
        phase=phase,
        billing_mode="deterministic",
        token_source="deterministic_no_model_call",
        billable=False,
        provider=provider,
        model=model,
        pricing_source=ZERO_COST_PRICING_SOURCE,
        **extra,
    )


def build_mock_phase_cost(
    *,
    phase: str,
    model: str = "mock",
    provider: str = "mock",
    **extra: Any,
) -> dict[str, Any]:
    return build_phase_cost(
        phase=phase,
        billing_mode="mock",
        token_source="mock_no_model_call",
        billable=False,
        provider=provider,
        model=model,
        pricing_source=ZERO_COST_PRICING_SOURCE,
        **extra,
    )


def build_provider_usage_phase_cost(
    *,
    phase: str,
    provider: str,
    model: str,
    input_tokens: int,
    output_tokens: int,
    cost_usd: float | None = None,
    pricing_source: str | None = None,
    **extra: Any,
) -> dict[str, Any]:
    if cost_usd is None:
        calculated_cost, calculated_source = calculate_token_cost(
            model,
            input_tokens,
            output_tokens,
            provider=provider,
        )
        cost_usd = calculated_cost
        pricing_source = pricing_source or calculated_source
    return build_phase_cost(
        phase=phase,
        billing_mode="provider_usage",
        token_source="provider_usage",
        billable=True,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cost_usd=cost_usd,
        provider=provider,
        model=model,
        pricing_source=pricing_source or "provider_usage",
        **extra,
    )


def build_unavailable_phase_cost(
    *,
    phase: str,
    provider: str = "",
    model: str = "",
    reason: str = "usage_unavailable",
    **extra: Any,
) -> dict[str, Any]:
    return build_phase_cost(
        phase=phase,
        billing_mode="unavailable",
        token_source="unavailable",
        billable=False,
        provider=provider,
        model=model,
        pricing_source="unavailable",
        reason=reason,
        **extra,
    )


def aggregate_phase_costs(phase_costs: dict[str, Any] | None) -> dict[str, Any]:
    """Aggregate phase cost records while preserving detailed cost truth.

    Wave 0 extensions: ``call_count``, ``attributed_call_count``,
    ``unattributed_call_count``. Ledger summaries under ``_ledger_summary``
    are preferred when present.
    """
    normalized: dict[str, dict[str, Any]] = {}
    total_input_tokens = 0
    total_output_tokens = 0
    total_cost_usd = 0.0
    cost_breakdown: dict[str, float] = {}
    call_count = 0
    attributed_call_count = 0
    unattributed_call_count = 0
    ledger_summary = None

    for phase_name, raw_record in (phase_costs or {}).items():
        if phase_name == "_ledger_summary" and isinstance(raw_record, dict):
            ledger_summary = dict(raw_record)
            continue
        if not isinstance(raw_record, dict):
            continue
        phase_key = str(raw_record.get("phase") or phase_name)
        record = dict(raw_record)
        record["phase"] = phase_key
        record["input_tokens"] = _non_negative_int(record.get("input_tokens"))
        record["output_tokens"] = _non_negative_int(record.get("output_tokens"))
        record["cost_usd"] = round(_non_negative_float(record.get("cost_usd")), 6)
        phase_calls = _non_negative_int(record.get("call_count"))
        if phase_calls <= 0:
            nested = record.get("calls")
            if isinstance(nested, list) and nested:
                phase_calls = len(nested)
            else:
                phase_calls = 1
        record["call_count"] = phase_calls
        if "attempt_index" in record:
            record["attempt_index"] = _non_negative_int(record.get("attempt_index"))
        if record.get("trigger") is not None:
            record["trigger"] = str(record.get("trigger") or "")
        normalized[phase_key] = record
        total_input_tokens += record["input_tokens"]
        total_output_tokens += record["output_tokens"]
        total_cost_usd += record["cost_usd"]
        cost_breakdown[phase_key] = record["cost_usd"]
        call_count += phase_calls
        if phase_key == "unattributed":
            unattributed_call_count += phase_calls
        else:
            attributed_call_count += phase_calls

    if isinstance(ledger_summary, dict):
        call_count = _non_negative_int(ledger_summary.get("call_count", call_count))
        attributed_call_count = _non_negative_int(
            ledger_summary.get("attributed_call_count", attributed_call_count)
        )
        unattributed_call_count = _non_negative_int(
            ledger_summary.get("unattributed_call_count", unattributed_call_count)
        )

    return {
        "input_tokens": total_input_tokens,
        "output_tokens": total_output_tokens,
        "cost_usd": round(total_cost_usd, 6),
        "cost_breakdown": cost_breakdown,
        "phase_costs": normalized,
        "call_count": call_count,
        "attributed_call_count": attributed_call_count,
        "unattributed_call_count": unattributed_call_count,
        "ledger_summary": ledger_summary,
    }
