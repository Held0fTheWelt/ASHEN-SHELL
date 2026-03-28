"""Tests for W2.4.4 AI decision logging with role diagnostics."""

import pytest
from app.runtime.w2_models import (
    InterpreterDiagnosticSummary,
    DirectorDiagnosticSummary,
    AIDecisionLog,
    GuardOutcome,
)


def test_interpreter_diagnostic_summary_creation():
    """InterpreterDiagnosticSummary can be created with scene_reading and detected_tensions."""
    summary = InterpreterDiagnosticSummary(
        scene_reading="The characters are in conflict over resources.",
        detected_tensions=["resource_competition", "power_struggle"],
    )

    assert summary.scene_reading == "The characters are in conflict over resources."
    assert summary.detected_tensions == ["resource_competition", "power_struggle"]


def test_director_diagnostic_summary_creation():
    """DirectorDiagnosticSummary can be created with conflict_steering and recommended_direction."""
    summary = DirectorDiagnosticSummary(
        conflict_steering="Escalate the tension to force a confrontation.",
        recommended_direction="escalate",
    )

    assert summary.conflict_steering == "Escalate the tension to force a confrontation."
    assert summary.recommended_direction == "escalate"


def test_director_diagnostic_summary_validates_direction_enum():
    """DirectorDiagnosticSummary only accepts valid recommended_direction values."""
    valid_directions = ["escalate", "stabilize", "shift_alliance", "redirect", "hold"]

    for direction in valid_directions:
        summary = DirectorDiagnosticSummary(
            conflict_steering="text",
            recommended_direction=direction,
        )
        assert summary.recommended_direction == direction


def test_ai_decision_log_accepts_role_fields():
    """AIDecisionLog accepts interpreter_output, director_output, responder_output, guard_outcome."""
    interpreter = InterpreterDiagnosticSummary(
        scene_reading="Scene reading",
        detected_tensions=["tension1"],
    )
    director = DirectorDiagnosticSummary(
        conflict_steering="Steering text",
        recommended_direction="hold",
    )

    log = AIDecisionLog(
        session_id="sess1",
        turn_number=1,
        raw_output="mock output",
        guard_outcome=GuardOutcome.ACCEPTED,
        interpreter_output=interpreter,
        director_output=director,
        responder_output=None,
    )

    assert log.interpreter_output == interpreter
    assert log.director_output == director
    assert log.responder_output is None
    assert log.guard_outcome == GuardOutcome.ACCEPTED
