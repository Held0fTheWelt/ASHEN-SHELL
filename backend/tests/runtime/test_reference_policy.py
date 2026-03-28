import pytest
from app.runtime.reference_policy import ReferencePolicyDecision, ReferencePolicy


def test_reference_policy_decision_allowed():
    """ReferencePolicyDecision represents allowed reference."""
    decision = ReferencePolicyDecision(allowed=True)
    assert decision.allowed is True
    assert decision.reason_code is None
    assert decision.reason_message is None


def test_reference_policy_decision_blocked():
    """ReferencePolicyDecision represents blocked reference."""
    decision = ReferencePolicyDecision(
        allowed=False,
        reason_code="unknown_character",
        reason_message="Character 'nonexistent' not in module"
    )
    assert decision.allowed is False
    assert decision.reason_code == "unknown_character"
    assert decision.reason_message == "Character 'nonexistent' not in module"


class TestCharacterReferences:
    """Test character reference validation (existence-only)."""

    def test_valid_character_reference(self, god_of_carnage_module):
        """Valid character reference is allowed."""
        decision = ReferencePolicy.evaluate("character", "veronique", god_of_carnage_module)
        assert decision.allowed is True
        assert decision.reason_code is None

    def test_invalid_character_reference(self, god_of_carnage_module):
        """Nonexistent character reference is rejected."""
        decision = ReferencePolicy.evaluate("character", "nonexistent_character", god_of_carnage_module)
        assert decision.allowed is False
        assert decision.reason_code == "unknown_character"
        assert "not in module" in decision.reason_message.lower()

    def test_empty_character_id(self, god_of_carnage_module):
        """Empty character ID is rejected."""
        decision = ReferencePolicy.evaluate("character", "", god_of_carnage_module)
        assert decision.allowed is False
        assert decision.reason_code == "unknown_character"

    def test_character_reference_without_module(self):
        """Character validation requires module."""
        decision = ReferencePolicy.evaluate("character", "veronique", None)
        assert decision.allowed is False
        assert decision.reason_code == "unknown_character"


class TestRelationshipReferences:
    """Test relationship reference validation (existence-only)."""

    def test_valid_relationship_reference(self, god_of_carnage_module):
        """Valid relationship reference is allowed."""
        # Find first relationship ID from the module
        if god_of_carnage_module.relationship_axes:
            rel_id = next(iter(god_of_carnage_module.relationship_axes.keys()))
            decision = ReferencePolicy.evaluate("relationship", rel_id, god_of_carnage_module)
            assert decision.allowed is True
            assert decision.reason_code is None

    def test_invalid_relationship_reference(self, god_of_carnage_module):
        """Nonexistent relationship reference is rejected."""
        decision = ReferencePolicy.evaluate("relationship", "nonexistent_relationship_xyz", god_of_carnage_module)
        assert decision.allowed is False
        assert decision.reason_code == "unknown_relationship"
        assert "not in module" in decision.reason_message.lower()

    def test_empty_relationship_id(self, god_of_carnage_module):
        """Empty relationship ID is rejected."""
        decision = ReferencePolicy.evaluate("relationship", "", god_of_carnage_module)
        assert decision.allowed is False
        assert decision.reason_code == "unknown_relationship"


class TestSceneReferences:
    """Test scene reference validation (existence + reachability)."""

    def test_self_reference_scene_allowed(self, god_of_carnage_module, god_of_carnage_module_with_state):
        """Current scene can reference itself."""
        current_scene = god_of_carnage_module_with_state.current_scene_id
        decision = ReferencePolicy.evaluate(
            "scene",
            current_scene,
            god_of_carnage_module,
            session=god_of_carnage_module_with_state,
            current_scene_id=current_scene
        )
        assert decision.allowed is True

    def test_unknown_scene_reference(self, god_of_carnage_module, god_of_carnage_module_with_state):
        """Nonexistent scene reference is rejected."""
        decision = ReferencePolicy.evaluate(
            "scene",
            "nonexistent_scene_xyz",
            god_of_carnage_module,
            session=god_of_carnage_module_with_state,
            current_scene_id=god_of_carnage_module_with_state.current_scene_id
        )
        assert decision.allowed is False
        assert decision.reason_code == "unknown_scene"

    def test_scene_reference_without_context(self, god_of_carnage_module):
        """Scene reference without current_scene_id fails for non-self references."""
        # Pick any scene ID
        if god_of_carnage_module.scene_phases:
            scene_id = next(iter(god_of_carnage_module.scene_phases.keys()))
            decision = ReferencePolicy.evaluate(
                "scene",
                scene_id,
                god_of_carnage_module,
                session=None,
                current_scene_id=None
            )
            assert decision.allowed is False
            assert decision.reason_code == "missing_context"


class TestTriggerReferences:
    """Test trigger reference validation (existence + applicability)."""

    def test_unknown_trigger_reference(self, god_of_carnage_module, god_of_carnage_module_with_state):
        """Nonexistent trigger reference is rejected."""
        decision = ReferencePolicy.evaluate(
            "trigger",
            "nonexistent_trigger_xyz",
            god_of_carnage_module,
            session=god_of_carnage_module_with_state,
            current_scene_id=god_of_carnage_module_with_state.current_scene_id
        )
        assert decision.allowed is False
        assert decision.reason_code == "unknown_trigger"


class TestReferenceValidationIntegration:
    """Integration tests: reference validation in decision validation pipeline."""

    def test_reference_policy_decision_values(self):
        """Test that ReferencePolicyDecision correctly represents allowed/blocked states."""
        allowed = ReferencePolicyDecision(allowed=True)
        assert allowed.allowed is True
        assert allowed.reason_code is None

        blocked = ReferencePolicyDecision(
            allowed=False,
            reason_code="unknown_character",
            reason_message="Not found"
        )
        assert blocked.allowed is False
        assert blocked.reason_code == "unknown_character"
        assert blocked.reason_message == "Not found"

    def test_invalid_reference_type(self, god_of_carnage_module):
        """Invalid reference type is rejected."""
        decision = ReferencePolicy.evaluate(
            "invalid_type",
            "some_id",
            god_of_carnage_module
        )
        assert decision.allowed is False
        assert decision.reason_code == "invalid_reference_type"

    def test_delta_with_unknown_character_rejected(self, god_of_carnage_module, god_of_carnage_module_with_state):
        """Delta targeting unknown character is rejected through canonical validator."""
        from app.runtime.validators import _validate_delta
        from app.runtime.turn_executor import ProposedStateDelta

        delta = ProposedStateDelta(target="characters.ghost_character.emotional_state", next_value=70)
        errors = _validate_delta(delta, god_of_carnage_module_with_state, god_of_carnage_module)
        assert len(errors) > 0
        assert any("reference" in e.lower() for e in errors)

    def test_delta_with_valid_character_no_reference_error(self, god_of_carnage_module, god_of_carnage_module_with_state):
        """Delta targeting valid character produces no reference error."""
        from app.runtime.validators import _validate_delta
        from app.runtime.turn_executor import ProposedStateDelta

        delta = ProposedStateDelta(target="characters.veronique.emotional_state", next_value=70)
        errors = _validate_delta(delta, god_of_carnage_module_with_state, god_of_carnage_module)
        reference_errors = [e for e in errors if "reference" in e.lower() and "character" in e.lower()]
        assert len(reference_errors) == 0

    def test_delta_with_unknown_relationship_rejected(self, god_of_carnage_module, god_of_carnage_module_with_state):
        """Delta targeting unknown relationship axis is rejected."""
        from app.runtime.validators import _validate_delta
        from app.runtime.turn_executor import ProposedStateDelta

        delta = ProposedStateDelta(target="relationships.ghost_relationship.value", next_value=50)
        errors = _validate_delta(delta, god_of_carnage_module_with_state, god_of_carnage_module)
        assert len(errors) > 0
        assert any("reference" in e.lower() for e in errors)

    def test_proposed_scene_unknown_rejected_via_reference_policy(self, god_of_carnage_module, god_of_carnage_module_with_state):
        """Unknown proposed_scene_id is rejected via ReferencePolicy."""
        from app.runtime.validators import validate_decision
        from app.runtime.turn_executor import MockDecision

        decision = MockDecision(proposed_scene_id="nonexistent_scene_xyz")
        outcome = validate_decision(decision, god_of_carnage_module_with_state, god_of_carnage_module)
        assert not outcome.is_valid
        assert any("scene" in e.lower() for e in outcome.errors)

    def test_action_structure_trigger_assertion_unknown_trigger_rejected(self, god_of_carnage_module):
        """TRIGGER_ASSERTION with unknown trigger ID is rejected."""
        from app.runtime.validators import validate_action_structure

        is_valid, errors = validate_action_structure(
            "TRIGGER_ASSERTION",
            {"trigger_ids": ["nonexistent_trigger_xyz"]},
            module=god_of_carnage_module,
        )
        assert not is_valid
        assert len(errors) > 0

    def test_action_structure_dialogue_impulse_unknown_character_rejected(self, god_of_carnage_module):
        """DIALOGUE_IMPULSE with unknown character is rejected."""
        from app.runtime.validators import validate_action_structure

        is_valid, errors = validate_action_structure(
            "DIALOGUE_IMPULSE",
            {"character_id": "ghost_character", "impulse_text": "Hello"},
            module=god_of_carnage_module,
        )
        assert not is_valid
        assert len(errors) > 0
