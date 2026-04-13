"""Deterministic runtime output validator with bounded semantic checks."""

from __future__ import annotations

from app.narrative.package_models import NarrativeDirectorScenePacket
from app.narrative.runtime_output_models import RuntimeTurnStructuredOutputV2
from app.narrative.validation_feedback import ValidationFeedback, ValidationViolation
from app.narrative.validator_strategies import OutputValidatorConfig, ValidationStrategy


def validate_runtime_output(
    *,
    packet: NarrativeDirectorScenePacket,
    output: RuntimeTurnStructuredOutputV2,
    config: OutputValidatorConfig,
) -> ValidationFeedback:
    """Validate output deterministically before commit."""
    violations: list[ValidationViolation] = []
    if not output.narrative_response.strip():
        violations.append(
            ValidationViolation(
                violation_type="empty_response",
                specific_issue="Generated narrative response is empty.",
                rule_violated="non_empty_narrative_response",
                suggested_fix="Provide a valid narrative response text.",
            )
        )
    illegal_triggers = [item for item in output.detected_triggers if item not in packet.legality_table.get("allowed_triggers", [])]
    if illegal_triggers:
        violations.append(
            ValidationViolation(
                violation_type="invalid_trigger",
                specific_issue=f"Detected illegal triggers: {', '.join(illegal_triggers)}.",
                rule_violated="trigger_must_be_legal_for_scene",
                suggested_fix="Replace illegal triggers with allowed scene triggers.",
            )
        )
    illegal_responders = [
        actor_id
        for actor_id in output.responder_actor_ids
        if actor_id not in set(packet.actor_minds.keys())
    ]
    if illegal_responders:
        violations.append(
            ValidationViolation(
                violation_type="invalid_responder",
                specific_issue=f"Responders not part of actor scope: {', '.join(illegal_responders)}.",
                rule_violated="responder_must_exist_in_actor_scope",
                suggested_fix="Only include actor ids present in scene actor_minds.",
            )
        )
    if config.strategy == ValidationStrategy.STRICT_RULE_ENGINE and config.strict_rule_engine_url is None:
        violations.append(
            ValidationViolation(
                violation_type="strict_rule_engine_unavailable",
                specific_issue="Strict rule engine strategy configured without endpoint.",
                rule_violated="strict_rule_engine_requires_url",
                suggested_fix="Provide strict_rule_engine_url or switch strategy.",
            )
        )
    return ValidationFeedback(
        passed=len(violations) == 0,
        violations=violations,
        corrections_needed=[item.suggested_fix for item in violations],
        legal_alternatives={"allowed_triggers": packet.legality_table.get("allowed_triggers", [])},
    )
