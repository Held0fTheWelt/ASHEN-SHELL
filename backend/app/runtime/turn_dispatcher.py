"""W2.1-R1 — Canonical Turn Execution Dispatcher

Provides the single authoritative entry point for turn execution, routing to
either mock or AI execution based on session execution_mode.

The dispatcher is the canonical runtime choice point: all turn execution requests
go through dispatch_turn(), which selects the appropriate execution path.

Core function:
- dispatch_turn() — Route turn execution to mock or AI path based on mode
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.content.module_models import ContentModule
    from app.runtime.ai_adapter import StoryAIAdapter
    from app.runtime.turn_executor import TurnExecutionResult
    from app.runtime.w2_models import SessionState


async def dispatch_turn(
    session: SessionState,
    current_turn: int,
    module: ContentModule,
    *,
    mock_decision_provider: callable | None = None,
    ai_adapter: StoryAIAdapter | None = None,
    operator_input: str = "",
) -> TurnExecutionResult:
    """Canonical turn execution dispatcher.

    Routes turn execution to either mock or AI path based on session.execution_mode.

    When execution_mode == "ai":
    - Requires ai_adapter parameter
    - Calls execute_turn_with_ai() with the provided adapter
    - AI path: request → adapter → parse → normalize → validate → execute

    When execution_mode == "mock":
    - Uses provided mock_decision_provider (if given) or MockDecision default
    - Calls execute_turn() with the mock decision
    - Mock path: deterministic decision → validate → execute

    Args:
        session: Current session state
        current_turn: Current turn number
        module: Loaded content module
        mock_decision_provider: Optional callable that returns MockDecision for mock mode
        ai_adapter: Required when execution_mode="ai", optional otherwise
        operator_input: Optional operator context

    Returns:
        TurnExecutionResult with execution_status, deltas, state, and events

    Raises:
        ValueError: If execution_mode=="ai" but no ai_adapter provided
    """
    # Import here to avoid circular imports
    from app.runtime.ai_turn_executor import execute_turn_with_ai
    from app.runtime.turn_executor import MockDecision, execute_turn

    execution_mode = session.execution_mode.lower() if session.execution_mode else "mock"

    if execution_mode == "ai":
        # AI execution path
        if not ai_adapter:
            raise ValueError(
                "AI execution mode selected but no ai_adapter provided to dispatch_turn()"
            )

        return await execute_turn_with_ai(
            session,
            current_turn,
            ai_adapter,
            module,
            operator_input=operator_input,
        )

    else:
        # Mock execution path (default)
        # Use provided mock_decision_provider or default to empty MockDecision
        if mock_decision_provider:
            decision = mock_decision_provider()
        else:
            decision = MockDecision()

        return await execute_turn(session, current_turn, decision, module)
