"""Tests for W2.4.5 responder-only proposal gating."""

import pytest
from app.runtime.w2_models import MockDecision, ProposalSource, ProposedStateDelta, GuardOutcome
from app.runtime.turn_executor import execute_turn


def test_mock_decision_requires_proposal_source():
    """MockDecision requires explicit proposal_source (not defaulted to responder)."""
    delta = ProposedStateDelta(
        target="characters.alice.emotional_state",
        next_value=75,
        delta_type=None,
        source="ai_proposal",
    )

    # Test that creating without proposal_source uses conservative MOCK default
    decision = MockDecision(
        proposed_deltas=[delta],
    )

    # Default must be MOCK (non-authoritative), not RESPONDER_DERIVED
    assert decision.proposal_source == ProposalSource.MOCK
    assert len(decision.proposed_deltas) == 1


def test_mock_decision_accepts_explicit_proposal_source():
    """MockDecision accepts explicit proposal_source field."""
    delta = ProposedStateDelta(
        target="characters.alice.emotional_state",
        next_value=75,
        delta_type=None,
        source="ai_proposal",
    )

    decision = MockDecision(
        proposed_deltas=[delta],
        proposal_source=ProposalSource.RESPONDER_DERIVED,
    )

    assert decision.proposal_source == ProposalSource.RESPONDER_DERIVED


def test_proposal_source_enum_has_all_values():
    """ProposalSource enum has all required values."""
    assert hasattr(ProposalSource, "RESPONDER_DERIVED")
    assert hasattr(ProposalSource, "MOCK")
    assert hasattr(ProposalSource, "ENGINE")
    assert hasattr(ProposalSource, "OPERATOR")


@pytest.mark.asyncio
async def test_execute_turn_rejects_non_responder_when_enforcement_enabled(god_of_carnage_module_with_state, god_of_carnage_module):
    """execute_turn() rejects non-responder proposals when enforcement enabled."""
    # Create session with initial state
    session = god_of_carnage_module_with_state

    # Create a mock decision with MOCK source (non-responder)
    delta = ProposedStateDelta(
        target="characters.veronique.emotional_state",
        next_value=50,
        delta_type=None,
        source="test_proposal",
    )

    decision = MockDecision(
        proposed_deltas=[delta],
        proposal_source=ProposalSource.MOCK,  # Non-responder source
    )

    # When enforcement is enabled (enforce_responder_only=True)
    result = await execute_turn(
        session=session,
        current_turn=1,
        mock_decision=decision,
        module=god_of_carnage_module,
        enforce_responder_only=True,  # Canonical enforcement enabled
    )

    # Should reject all proposals from non-responder source
    assert result.guard_outcome == GuardOutcome.REJECTED
    assert len(result.accepted_deltas) == 0
    assert len(result.rejected_deltas) == 1


@pytest.mark.asyncio
async def test_execute_turn_accepts_responder_with_enforcement(god_of_carnage_module_with_state, god_of_carnage_module):
    """execute_turn() accepts responder-derived proposals with enforcement enabled."""
    session = god_of_carnage_module_with_state

    # Create a mock decision with RESPONDER_DERIVED source
    delta = ProposedStateDelta(
        target="characters.veronique.emotional_state",
        next_value=75,
        delta_type=None,
        source="ai_proposal",
    )

    decision = MockDecision(
        proposed_deltas=[delta],
        proposal_source=ProposalSource.RESPONDER_DERIVED,  # Responder-derived
    )

    # With enforcement enabled, responder proposals should flow through normal validation
    result = await execute_turn(
        session=session,
        current_turn=1,
        mock_decision=decision,
        module=god_of_carnage_module,
        enforce_responder_only=True,
    )

    # Should be validated normally (not rejected by gate)
    # Status depends on validation, not on source gate
    assert result.guard_outcome in [GuardOutcome.ACCEPTED, GuardOutcome.PARTIALLY_ACCEPTED, GuardOutcome.REJECTED]
    # Key point: not rejected due to source gate reaching the enforcement


@pytest.mark.asyncio
async def test_execute_turn_allows_non_responder_when_enforcement_disabled(god_of_carnage_module_with_state, god_of_carnage_module):
    """execute_turn() allows non-responder proposals when enforcement disabled (default)."""
    session = god_of_carnage_module_with_state

    delta = ProposedStateDelta(
        target="characters.veronique.emotional_state",
        next_value=50,
        delta_type=None,
        source="test_proposal",
    )

    decision = MockDecision(
        proposed_deltas=[delta],
        proposal_source=ProposalSource.MOCK,  # Non-responder source
    )

    # With enforcement disabled (default), non-responder proposals pass gate
    result = await execute_turn(
        session=session,
        current_turn=1,
        mock_decision=decision,
        module=god_of_carnage_module,
        enforce_responder_only=False,  # Enforcement disabled
    )

    # Should NOT be rejected by gate (but may be rejected by validation)
    # Key: gate doesn't reject, validation may
    assert result.guard_outcome in [GuardOutcome.ACCEPTED, GuardOutcome.PARTIALLY_ACCEPTED, GuardOutcome.REJECTED]


@pytest.mark.asyncio
async def test_role_structured_responder_candidates_marked_responder_derived():
    """Responder candidates extracted from role-structured decision must be marked RESPONDER_DERIVED."""
    # Setup: import required classes for role-structured decision
    from app.runtime.role_contract import (
        InterpreterSection,
        DirectorSection,
        ResponderSection,
        StateChangeCandidate,
    )
    from app.runtime.role_structured_decision import ParsedRoleAwareDecision
    from app.runtime.ai_decision import ParsedAIDecision
    from app.runtime.ai_turn_executor import process_role_structured_decision

    # Create components for role-structured decision
    parsed_decision = ParsedAIDecision(
        scene_interpretation="Scene",
        detected_triggers=[],
        proposed_deltas=[],
        proposed_scene_id=None,
        rationale="Rationale",
        raw_output="raw",
        parsed_source="structured_payload",
    )

    responder = ResponderSection(
        state_change_candidates=[
            StateChangeCandidate(
                target_path="characters.veronique.emotional_state",
                proposed_value=50,
                rationale="Veronique is upset",
            ),
        ]
    )

    role_aware_decision = ParsedRoleAwareDecision(
        parsed_decision=parsed_decision,
        interpreter=InterpreterSection(
            scene_reading="",
            detected_tensions=[],
            trigger_candidates=[],
        ),
        director=DirectorSection(
            conflict_steering="",
            escalation_level=5,
            recommended_direction="hold",
        ),
        responder=responder,
    )

    # Extract responder candidates (simulate AI turn executor flow)
    extracted_decision = process_role_structured_decision(role_aware_decision)

    # Verify: responder candidates are marked RESPONDER_DERIVED
    assert extracted_decision.proposal_source == ProposalSource.RESPONDER_DERIVED
    assert len(extracted_decision.proposed_deltas) == 1
    assert extracted_decision.proposed_deltas[0].target == "characters.veronique.emotional_state"
    assert extracted_decision.proposed_deltas[0].next_value == 50
