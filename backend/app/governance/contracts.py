"""Typed contracts used by governance APIs and services."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field


class SuccessEnvelope(BaseModel):
    """Standard success envelope for governance APIs."""

    ok: bool = True
    data: dict[str, Any]


class ErrorEnvelopeDetail(BaseModel):
    """Domain specific error payload."""

    code: str
    message: str
    details: dict[str, Any] = Field(default_factory=dict)


class ErrorEnvelope(BaseModel):
    """Standard error envelope for governance APIs."""

    ok: bool = False
    error: ErrorEnvelopeDetail


class RuntimeModesUpdatePayload(BaseModel):
    """Payload for runtime mode updates."""

    generation_execution_mode: str
    retrieval_execution_mode: str
    validation_execution_mode: str
    provider_selection_mode: str
    runtime_profile: str


class UsageEventInput(BaseModel):
    """Input contract for usage event ingestion."""

    provider_id: str | None = None
    model_id: str | None = None
    task_kind: str
    workflow_scope: str
    request_id: str
    success: bool = True
    latency_ms: int | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None
    provider_reported_cost: Decimal | None = None
    estimated_cost: Decimal | None = None
    cost_method_used: str
    degraded_mode_used: bool = False
    retry_used: bool = False
    fallback_used: bool = False


class ProviderHealthTestResult(BaseModel):
    """Normalized result contract for provider health tests."""

    provider_id: str
    health_status: str
    latency_ms: int | None = None
    tested_at: datetime
    error_code: str | None = None
    error_message: str | None = None
