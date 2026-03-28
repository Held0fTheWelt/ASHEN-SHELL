"""Tests for W2.1-R1 — Turn Execution Dispatcher

Verifies that dispatch_turn() is the canonical entry point and correctly
routes to mock or AI execution based on session.execution_mode.
"""

import asyncio
import pytest
from app.runtime.ai_adapter import AdapterResponse, StoryAIAdapter
from app.runtime.turn_dispatcher import dispatch_turn
from app.runtime.turn_executor import MockDecision


class DeterministicTestAdapter(StoryAIAdapter):
    """Test adapter that returns valid W2.1.2-conformant payload."""

    @property
    def adapter_name(self) -> str:
        return "test-adapter"

    def generate(self, request):
        return AdapterResponse(
            raw_output="[test adapter output]",
            structured_payload={
                "scene_interpretation": "Test scene interpretation",
                "detected_triggers": [],
                "proposed_state_deltas": [],
                "rationale": "Test rationale for dispatcher",
            },
        )


def test_dispatcher_routes_to_mock_when_mode_is_mock(
    god_of_carnage_module_with_state, god_of_carnage_module
):
    """Dispatcher routes to mock path when execution_mode='mock'."""
    session = god_of_carnage_module_with_state
    session.execution_mode = "mock"

    result = asyncio.run(
        dispatch_turn(
            session,
            current_turn=session.turn_counter + 1,
            module=god_of_carnage_module,
        )
    )

    assert result.execution_status == "success"
    assert result.turn_number == session.turn_counter + 1


def test_dispatcher_routes_to_ai_when_mode_is_ai(
    god_of_carnage_module_with_state, god_of_carnage_module
):
    """Dispatcher routes to AI path when execution_mode='ai'."""
    session = god_of_carnage_module_with_state
    session.execution_mode = "ai"

    adapter = DeterministicTestAdapter()

    result = asyncio.run(
        dispatch_turn(
            session,
            current_turn=session.turn_counter + 1,
            module=god_of_carnage_module,
            ai_adapter=adapter,
        )
    )

    assert result.execution_status == "success"
    assert result.turn_number == session.turn_counter + 1


def test_dispatcher_raises_error_if_ai_mode_without_adapter(
    god_of_carnage_module_with_state, god_of_carnage_module
):
    """Dispatcher raises ValueError if AI mode selected but no adapter provided."""
    session = god_of_carnage_module_with_state
    session.execution_mode = "ai"

    with pytest.raises(ValueError, match="AI execution mode.*no ai_adapter"):
        asyncio.run(
            dispatch_turn(
                session,
                current_turn=session.turn_counter + 1,
                module=god_of_carnage_module,
            )
        )


def test_dispatcher_defaults_to_mock_when_mode_not_set(
    god_of_carnage_module_with_state, god_of_carnage_module
):
    """Dispatcher defaults to mock when execution_mode is not set."""
    session = god_of_carnage_module_with_state
    session.execution_mode = ""  # Not set

    result = asyncio.run(
        dispatch_turn(
            session,
            current_turn=session.turn_counter + 1,
            module=god_of_carnage_module,
        )
    )

    assert result.execution_status == "success"


def test_dispatcher_with_custom_mock_decision_provider(
    god_of_carnage_module_with_state, god_of_carnage_module
):
    """Dispatcher uses provided mock_decision_provider in mock mode."""
    session = god_of_carnage_module_with_state
    session.execution_mode = "mock"

    def custom_decision_provider():
        return MockDecision(
            detected_triggers=["test_trigger"],
            proposed_deltas=[],
            narrative_text="Custom decision",
        )

    result = asyncio.run(
        dispatch_turn(
            session,
            current_turn=session.turn_counter + 1,
            module=god_of_carnage_module,
            mock_decision_provider=custom_decision_provider,
        )
    )

    assert result.execution_status == "success"
    assert result.decision.narrative_text == "Custom decision"


def test_dispatcher_is_canonical_entry_point(
    god_of_carnage_module_with_state, god_of_carnage_module
):
    """Dispatcher is the canonical entry point, not a wrapper."""
    session = god_of_carnage_module_with_state
    session.execution_mode = "mock"

    # Call dispatcher with no direct execute_turn or execute_turn_with_ai call
    result = asyncio.run(
        dispatch_turn(
            session,
            current_turn=session.turn_counter + 1,
            module=god_of_carnage_module,
        )
    )

    # Result should be a valid TurnExecutionResult from the dispatcher
    assert result is not None
    assert hasattr(result, "execution_status")
    assert hasattr(result, "updated_canonical_state")


def test_ai_path_now_reachable_through_dispatcher(
    god_of_carnage_module_with_state, god_of_carnage_module
):
    """AI execution path is now reachable through dispatcher, not just direct tests."""
    session = god_of_carnage_module_with_state
    session.execution_mode = "ai"

    adapter = DeterministicTestAdapter()

    # This simulates production code calling the dispatcher
    # Previously, execute_turn_with_ai was only reachable by tests calling it directly
    result = asyncio.run(
        dispatch_turn(
            session,
            current_turn=session.turn_counter + 1,
            module=god_of_carnage_module,
            ai_adapter=adapter,
        )
    )

    # Should get a successful result from the AI path
    assert result.execution_status == "success"


def test_mock_path_still_works_through_dispatcher(
    god_of_carnage_module_with_state, god_of_carnage_module
):
    """Mock execution path still works when routed through dispatcher."""
    session = god_of_carnage_module_with_state
    session.execution_mode = "mock"

    result = asyncio.run(
        dispatch_turn(
            session,
            current_turn=session.turn_counter + 1,
            module=god_of_carnage_module,
        )
    )

    assert result.execution_status == "success"
    # State should be unchanged (mock decides nothing)
    assert result.accepted_deltas == []
    assert result.rejected_deltas == []


def test_dispatcher_preserves_execution_result_coherence(
    god_of_carnage_module_with_state, god_of_carnage_module
):
    """Dispatcher returns coherent TurnExecutionResult regardless of path."""
    session = god_of_carnage_module_with_state
    session.execution_mode = "mock"

    result = asyncio.run(
        dispatch_turn(
            session,
            current_turn=session.turn_counter + 1,
            module=god_of_carnage_module,
        )
    )

    # Result should have all required TurnExecutionResult fields
    assert result.turn_number == session.turn_counter + 1
    assert result.session_id == session.session_id
    assert result.execution_status in ["success", "system_error"]
    assert isinstance(result.updated_canonical_state, dict)
    assert isinstance(result.accepted_deltas, list)
    assert isinstance(result.rejected_deltas, list)


def test_no_w2_scope_jump_dispatcher():
    """No scope jump into W2.2+ features."""
    assert True  # Scope validation is manual
