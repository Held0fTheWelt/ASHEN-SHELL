"""Integration tests proving W2.5 recovery actually happens in execute_turn_with_ai().

These tests verify that recovery mechanisms (retry, reduced-context, fallback, safe-turn,
restore, markers) are actually wired into the real turn execution flow, not just defined
as policies.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock
from datetime import datetime, timezone
from copy import deepcopy

from app.runtime.ai_turn_executor import execute_turn_with_ai
from app.runtime.ai_adapter import AdapterResponse
from app.runtime.w2_models import (
    DegradedMarker,
    ExecutionFailureReason,
)
from app.runtime.ai_failure_recovery import RetryPolicy


class TestRetryLoopIntegration:
    """Verify retry loop actually triggers on retryable failures."""

    @pytest.mark.asyncio
    async def test_adapter_error_triggers_retry(
        self, god_of_carnage_module_with_state, god_of_carnage_module
    ):
        """Adapter error on attempt 1 should retry; second attempt is called."""
        session = god_of_carnage_module_with_state

        # Mock adapter to fail, providing responses for up to MAX_RETRIES calls
        retry_policy = RetryPolicy()
        responses = [
            AdapterResponse(error="Attempt 1 error", raw_output="", decisions=[])
            for _ in range(retry_policy.MAX_RETRIES)
        ]

        adapter = MagicMock()
        adapter.generate = MagicMock(side_effect=responses)

        result = await execute_turn_with_ai(
            session, 1, adapter, god_of_carnage_module
        )

        # Verify at least 2 calls (initial attempt + at least 1 retry)
        assert adapter.generate.call_count >= 2, \
            f"Should have retried (at least 2 calls), but was called {adapter.generate.call_count} times"

    @pytest.mark.asyncio
    async def test_retry_exhaustion_after_max_attempts(
        self, god_of_carnage_module_with_state, god_of_carnage_module
    ):
        """After MAX_RETRIES adapter errors, should exhaust retries."""
        session = god_of_carnage_module_with_state

        # Always fail with adapter error
        error_response = AdapterResponse(
            error="Persistent connection failure",
            raw_output="",
            decisions=[]
        )

        adapter = MagicMock()
        adapter.generate = MagicMock(return_value=error_response)

        result = await execute_turn_with_ai(
            session, 1, adapter, god_of_carnage_module
        )

        # Should have retried MAX_RETRIES times (3)
        retry_policy = RetryPolicy()
        assert adapter.generate.call_count == retry_policy.MAX_RETRIES, \
            f"Should have tried max {retry_policy.MAX_RETRIES} times"
        # Should not succeed
        assert result.execution_status != "success", f"Expected failure but got {result.execution_status}"

    @pytest.mark.asyncio
    async def test_empty_response_triggers_retry(
        self, god_of_carnage_module_with_state, god_of_carnage_module
    ):
        """Empty response on attempt 1 should retry; second attempt is called."""
        session = god_of_carnage_module_with_state

        retry_policy = RetryPolicy()
        responses = [
            AdapterResponse(error=None, raw_output="", decisions=[])
            for _ in range(retry_policy.MAX_RETRIES)
        ]

        adapter = MagicMock()
        adapter.generate = MagicMock(side_effect=responses)

        result = await execute_turn_with_ai(
            session, 1, adapter, god_of_carnage_module
        )

        # Verify at least 2 calls (initial attempt + at least 1 retry)
        assert adapter.generate.call_count >= 2, \
            f"Should have retried (at least 2 calls), but was called {adapter.generate.call_count} times"
