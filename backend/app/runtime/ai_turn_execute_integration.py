"""Integration: vollständiger AI-Turn-Pfad (Pre-Adapter → Routing/Gen → Tool-Loop → Parse-Pipeline)."""

from __future__ import annotations

from typing import Any

from app.content.module_models import ContentModule
from app.runtime.ai_adapter import StoryAIAdapter
from app.runtime.ai_turn_execute_integration_phases import (
    run_after_first_response_tail,
    run_routing_and_first_response_phase,
)
from app.runtime.ai_turn_pre_adapter import build_ai_turn_pre_adapter_state
from app.runtime.runtime_models import SessionState
from app.runtime.turn_execution_types import TurnExecutionResult


async def run_execute_turn_with_ai_integration(
    session: SessionState,
    current_turn: int,
    adapter: StoryAIAdapter,
    module: ContentModule,
    *,
    operator_input: str = "",
    recent_events: list[dict[str, Any]] | None = None,
    preview_diagnostics_before_parse: dict[str, Any] | None = None,
) -> TurnExecutionResult:
    pa = build_ai_turn_pre_adapter_state(session)
    routing = run_routing_and_first_response_phase(
        session=session,
        current_turn=current_turn,
        module=module,
        operator_input=operator_input,
        recent_events=recent_events,
        pa=pa,
        adapter=adapter,
        preview_diagnostics_before_parse=preview_diagnostics_before_parse,
    )
    return await run_after_first_response_tail(
        session=session,
        current_turn=current_turn,
        module=module,
        recent_events=recent_events,
        pa=pa,
        routing=routing,
    )
