"""Prefer ``register_adapter_model`` in routing-sensitive tests (Task 2A+)."""

from __future__ import annotations

from app.model_governance.adapter_registry import register_adapter_model
from app.model_governance.ai_adapter import StoryAIAdapter
from app.model_governance.model_routing_contracts import AdapterModelSpec


def register_routing_adapter(spec: AdapterModelSpec, adapter: StoryAIAdapter) -> None:
    """Register adapter + spec together (routing-visible)."""
    register_adapter_model(spec, adapter)
