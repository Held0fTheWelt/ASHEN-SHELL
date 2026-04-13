"""Validation strategy definitions and runtime config contract."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel


class ValidationStrategy(str, Enum):
    """Supported output validator strategies."""

    SCHEMA_ONLY = "schema_only"
    SCHEMA_PLUS_SEMANTIC = "schema_plus_semantic"
    STRICT_RULE_ENGINE = "strict_rule_engine"


class OutputValidatorConfig(BaseModel):
    """Runtime validator config visible to backend and operators."""

    strategy: ValidationStrategy
    semantic_policy_check: bool = False
    strict_rule_engine_url: str | None = None
    enable_corrective_feedback: bool = True
    max_retry_attempts: int = 1
    fast_feedback_mode: bool = True
    emit_runtime_health_events: bool = True
    fallback_alert_threshold: int = 5
