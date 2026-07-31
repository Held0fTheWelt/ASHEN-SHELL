"""Wave 4: E7 technical failure fallback chain contracts."""
from __future__ import annotations

from app.story_runtime.failure_recovery import (
    DEFAULT_FAILURE_RECOVERY,
    ReducedContextRetryPolicy,
    build_reduced_context_retry_prompt,
    deterministic_continuation_turn,
)


def test_e7_chain_reduced_then_deterministic() -> None:
    bundle = DEFAULT_FAILURE_RECOVERY
    assert bundle.reduced_context_retry.enabled is True
    assert bundle.safe_turn.enabled is True
    assert bundle.reduced_context_retry.max_attempts == 1

    first = "PROMPT" + ("Y" * 4000)
    second = build_reduced_context_retry_prompt(
        original_prompt=first,
        policy=ReducedContextRetryPolicy(max_context_chars=1500),
    )
    assert len(second) < len(first)

    cont = deterministic_continuation_turn(prior_scene_id="s1", turn_number=9)
    assert cont["model_calls_additional"] == 0
    assert cont["degraded_mode"] == "technically_reduced"
