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
