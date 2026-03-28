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
