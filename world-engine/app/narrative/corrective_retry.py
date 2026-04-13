"""Corrective retry orchestration for rejected generation outputs."""

from __future__ import annotations

from app.narrative.runtime_output_models import RuntimeTurnStructuredOutputV2
from app.narrative.validation_feedback import ValidationFeedback


def apply_corrective_retry(
    *,
    original_output: RuntimeTurnStructuredOutputV2,
    feedback: ValidationFeedback,
) -> RuntimeTurnStructuredOutputV2:
    """Build one deterministic corrective retry candidate from feedback."""
    if feedback.passed:
        return original_output
    response = original_output.narrative_response.strip()
    if not response:
        response = "A measured silence settles before the conversation continues."
    return RuntimeTurnStructuredOutputV2(
        narrative_response=response,
        intent_summary=original_output.intent_summary or "corrective_retry",
        responder_actor_ids=original_output.responder_actor_ids,
        detected_triggers=[],
        conflict_vector=original_output.conflict_vector,
        proposed_state_effects=original_output.proposed_state_effects,
        confidence=original_output.confidence,
        blocked_turn_reason=None,
    )
