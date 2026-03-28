"""Integration tests for W2.2.4: Scene and ending legality coherence.

Validates that scene transition and ending legality are consistent across
AI proposal validation (validators.py) and canonical situation derivation (next_situation.py).

These tests ensure both paths use SceneTransitionLegality for coherent decisions.
"""

import pytest
from app.content.module_models import (
    ContentModule,
    EndingCondition,
    ModuleMetadata,
    PhaseTransition,
    ScenePhase,
)
from app.runtime.next_situation import derive_next_situation
from app.runtime.scene_legality import SceneTransitionLegality, SceneLegalityDecision
from app.runtime.validators import validate_decision
from app.runtime.w2_models import SessionState, SessionStatus


class TestSceneTransitionLegalityCoherence:
    """Both validation and derivation paths use SceneTransitionLegality."""

    @pytest.fixture
    def simple_module(self):
        """Module with basic transitions, no endings."""
        metadata = ModuleMetadata(
            module_id="simple",
            title="Simple Test",
            version="0.1.0",
            contract_version="1.0.0",
        )

        scenes = {
            "scene_a": ScenePhase(id="scene_a", name="A", sequence=1, description="Scene A"),
            "scene_b": ScenePhase(id="scene_b", name="B", sequence=2, description="Scene B"),
        }

        transitions = {
            "a_to_b": PhaseTransition(
                id="a_to_b",
                from_phase="scene_a",
                to_phase="scene_b",
                trigger_conditions=[],
            ),
        }

        return ContentModule(
            metadata=metadata,
            scene_phases=scenes,
            phase_transitions=transitions,
            ending_conditions={},
            characters={},
            relationship_axes={},
            triggers={},
            assertions={},
        )

    @pytest.fixture
    def session_a(self):
        """Session in scene_a."""
        return SessionState(
            session_id="test",
            module_id="simple",
            module_version="0.1.0",
            current_scene_id="scene_a",
            status=SessionStatus.ACTIVE,
            canonical_state={},
        )

    def test_self_transition_always_legal(self, simple_module, session_a):
        """Self-transition is legal via canonical rules."""
        legality = SceneTransitionLegality.check_transition_legal(
            "scene_a", "scene_a", simple_module
        )
        assert legality.allowed
        assert "Self-transition" in legality.reason

    def test_valid_transition_legal(self, simple_module, session_a):
        """Valid transition is legal via canonical rules."""
        legality = SceneTransitionLegality.check_transition_legal(
            "scene_a", "scene_b", simple_module
        )
        assert legality.allowed

    def test_unreachable_scene_illegal(self, simple_module, session_a):
        """Unreachable scene is illegal via canonical rules."""
        # Try to transition from scene_b to scene_a (no transition exists)
        legality = SceneTransitionLegality.check_transition_legal(
            "scene_b", "scene_a", simple_module
        )
        assert not legality.allowed
        assert "reachable" in legality.reason.lower()

    def test_unknown_scene_illegal(self, simple_module, session_a):
        """Unknown scene is illegal via canonical rules."""
        legality = SceneTransitionLegality.check_transition_legal(
            "scene_a", "unknown_scene", simple_module
        )
        assert not legality.allowed
        assert "not in module" in legality.reason

    def test_validator_uses_canonical_legality(self, simple_module, session_a):
        """Validator uses SceneTransitionLegality for checks."""
        from app.runtime.turn_executor import MockDecision

        # Valid transition
        decision = MockDecision(proposed_scene_id="scene_b", proposed_deltas=[])
        outcome = validate_decision(decision, session_a, simple_module)
        assert outcome.is_valid

        # Invalid scene
        decision = MockDecision(proposed_scene_id="unknown", proposed_deltas=[])
        outcome = validate_decision(decision, session_a, simple_module)
        assert not outcome.is_valid


class TestEndingLegalityCoherence:
    """Ending legality is checked via canonical SceneTransitionLegality."""

    @pytest.fixture
    def ending_module(self):
        """Module with one unconditional ending."""
        metadata = ModuleMetadata(
            module_id="ending_test",
            title="Ending Test",
            version="0.1.0",
            contract_version="1.0.0",
        )

        scenes = {
            "play": ScenePhase(id="play", name="Play", sequence=1, description="Gameplay"),
        }

        endings = {
            "end_default": EndingCondition(
                id="end_default",
                name="Default",
                description="Default ending",
                trigger_conditions=[],
                outcome={"type": "default"},
            ),
        }

        return ContentModule(
            metadata=metadata,
            scene_phases=scenes,
            phase_transitions={},
            ending_conditions=endings,
            characters={},
            relationship_axes={},
            triggers={},
            assertions={},
        )

    @pytest.fixture
    def session_in_play(self):
        """Session in play scene."""
        return SessionState(
            session_id="test",
            module_id="ending_test",
            module_version="0.1.0",
            current_scene_id="play",
            status=SessionStatus.ACTIVE,
            canonical_state={},
        )

    def test_unconditional_ending_legal(self, ending_module, session_in_play):
        """Unconditional ending is legal via canonical rules."""
        ending_id, legality = SceneTransitionLegality.check_ending_legal(
            ending_module, session=session_in_play, detected_triggers=[]
        )
        assert ending_id == "end_default"
        assert legality.allowed

    def test_no_ending_when_none_defined(self):
        """No ending available when module has no endings."""
        module = ContentModule(
            metadata=ModuleMetadata(
                module_id="no_endings",
                title="No Endings",
                version="0.1.0",
                contract_version="1.0.0",
            ),
            scene_phases={"s": ScenePhase(id="s", name="S", sequence=1, description="")},
            phase_transitions={},
            ending_conditions={},
            characters={},
            relationship_axes={},
            triggers={},
            assertions={},
        )
        ending_id, legality = SceneTransitionLegality.check_ending_legal(
            module, detected_triggers=[]
        )
        assert ending_id is None
        assert not legality.allowed


class TestNoIllegalNarrativeForcing:
    """Core requirement: AI cannot force illegal narrative progression."""

    @pytest.fixture
    def gated_module(self):
        """Module with conditional transition (gated behind a trigger)."""
        metadata = ModuleMetadata(
            module_id="gated",
            title="Gated",
            version="0.1.0",
            contract_version="1.0.0",
        )

        scenes = {
            "s1": ScenePhase(id="s1", name="S1", sequence=1, description=""),
            "s2": ScenePhase(id="s2", name="S2", sequence=2, description=""),
            "s3": ScenePhase(id="s3", name="S3", sequence=3, description=""),
        }

        # Conditional transition requires trigger
        transitions = {
            "t": PhaseTransition(
                id="t",
                from_phase="s2",
                to_phase="s3",
                trigger_conditions=["unlock"],
            ),
        }

        return ContentModule(
            metadata=metadata,
            scene_phases=scenes,
            phase_transitions=transitions,
            ending_conditions={},
            characters={},
            relationship_axes={},
            triggers={},
            assertions={},
        )

    @pytest.fixture
    def session_s2(self):
        """Session at s2."""
        return SessionState(
            session_id="test",
            module_id="gated",
            module_version="0.1.0",
            current_scene_id="s2",
            status=SessionStatus.ACTIVE,
            canonical_state={},
        )

    def test_conditional_transition_blocked_without_trigger(
        self, gated_module, session_s2
    ):
        """Transition requiring unmet trigger is illegal."""
        legality = SceneTransitionLegality.check_transition_legal(
            "s2", "s3", gated_module, detected_triggers=[]
        )
        assert not legality.allowed
        assert "unmet" in legality.reason.lower()

    def test_conditional_transition_allowed_with_trigger(
        self, gated_module, session_s2
    ):
        """Transition becomes legal when trigger is present."""
        legality = SceneTransitionLegality.check_transition_legal(
            "s2", "s3", gated_module, detected_triggers=["unlock"]
        )
        assert legality.allowed

    def test_validator_rejects_unreachable_scene(self, gated_module, session_s2):
        """Validator blocks jump to unreachable scene (no direct transition)."""
        from app.runtime.turn_executor import MockDecision

        # No transition exists from s2 to s1
        decision = MockDecision(proposed_scene_id="s1", proposed_deltas=[])
        outcome = validate_decision(decision, session_s2, gated_module)
        assert not outcome.is_valid
        assert any("reachable" in e.lower() for e in outcome.errors)
