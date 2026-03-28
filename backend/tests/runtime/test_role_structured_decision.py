"""Tests for W2.4.3 role-structured parsing and normalization."""

import pytest
from app.runtime.ai_decision import ParsedAIDecision
from app.runtime.role_structured_decision import ParsedRoleAwareDecision
from app.runtime.role_contract import (
    InterpreterSection,
    DirectorSection,
    ResponderSection,
)


def test_parsed_role_aware_decision_creation():
    """ParsedRoleAwareDecision wraps ParsedAIDecision with role sections."""
    parsed_decision = ParsedAIDecision(
        scene_interpretation="Scene",
        detected_triggers=[],
        proposed_deltas=[],
        proposed_scene_id=None,
        rationale="Rationale",
        raw_output="raw",
        parsed_source="structured_payload",
    )

    interpreter = InterpreterSection(
        scene_reading="Reading",
        detected_tensions=[],
        trigger_candidates=[],
    )
    director = DirectorSection(
        conflict_steering="Steering",
        escalation_level=5,
        recommended_direction="hold",
    )
    responder = ResponderSection()

    role_aware = ParsedRoleAwareDecision(
        parsed_decision=parsed_decision,
        interpreter=interpreter,
        director=director,
        responder=responder,
    )

    assert role_aware.parsed_decision == parsed_decision
    assert role_aware.interpreter == interpreter
    assert role_aware.director == director
    assert role_aware.responder == responder
