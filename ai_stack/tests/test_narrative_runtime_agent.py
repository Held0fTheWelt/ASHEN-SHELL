"""
Tests for NarrativeRuntimeAgent (Phase 1 & 2).

Tests the core streaming implementation and narrative validation rules.
"""

import pytest
from datetime import datetime, timezone
from uuid import uuid4

from ai_stack.narrative_runtime_agent import (
    NarrativeRuntimeAgent,
    NarrativeRuntimeAgentInput,
    NarrativeRuntimeAgentConfig,
    NarrativeEventKind,
)


@pytest.fixture
def agent_config():
    """Default agent configuration for testing."""
    return NarrativeRuntimeAgentConfig(
        max_narrator_blocks=10,
        motivation_pressure_threshold=0.3,
    )


@pytest.fixture
def narrator_agent(agent_config):
    """Instantiate NarrativeRuntimeAgent with test config."""
    return NarrativeRuntimeAgent(config=agent_config)


@pytest.fixture
def sample_runtime_state():
    """Sample RuntimeState for testing."""
    return {
        "scene_id": "alains_office_act1",
        "actor_positions": {
            "annette": {"location": "office", "state": "alert"},
            "alain": {"location": "office", "state": "focused"},
        },
        "environment_objects": [
            {"object_id": "desk", "state": "cluttered"},
            {"object_id": "chair", "state": "occupied"},
        ],
    }


@pytest.fixture
def sample_npc_agency_plan():
    """Sample NPCAgencyPlan with initiatives."""
    return {
        "initiatives": [
            {
                "actor_id": "annette",
                "initiative_type": "challenge_authority",
                "resolved": False,
                "motivation_intensity": 0.8,
            },
            {
                "actor_id": "alain",
                "initiative_type": "strategic_defense",
                "resolved": False,
                "motivation_intensity": 0.6,
            },
        ],
        "pressure_summary": "High dramatic tension",
    }


@pytest.fixture
def sample_agent_input(sample_runtime_state, sample_npc_agency_plan):
    """Sample NarrativeRuntimeAgentInput for testing."""
    return NarrativeRuntimeAgentInput(
        runtime_state=sample_runtime_state,
        npc_agency_plan=sample_npc_agency_plan,
        dramatic_signature={
            "primary_tension": "authority_challenge",
            "secondary_tension": "strategic_positioning",
        },
        narrative_threads=[
            {"thread_id": "loyalty_test", "state": "active"},
            {"thread_id": "power_shift", "state": "emerging"},
        ],
        session_id="test_session_001",
        turn_number=3,
        trace_id="trace_001",
        enable_langfuse_tracing=False,
    )


class TestNarrativeRuntimeAgentCore:
    """Test core streaming functionality."""

    def test_narrator_agent_instantiation(self, narrator_agent):
        """Agent instantiates with default or custom config."""
        assert narrator_agent is not None
        assert narrator_agent.config.max_narrator_blocks == 10

    def test_stream_narrator_blocks_yields_events(self, narrator_agent, sample_agent_input):
        """stream_narrator_blocks yields NarrativeRuntimeAgentEvent objects."""
        events = list(narrator_agent.stream_narrator_blocks(sample_agent_input))
        assert len(events) > 0
        assert all(hasattr(e, "event_kind") for e in events)

    def test_narrator_blocks_emitted_before_ruhepunkt(self, narrator_agent, sample_agent_input):
        """Narrator blocks are emitted before ruhepunkt signal."""
        events = list(narrator_agent.stream_narrator_blocks(sample_agent_input))
        event_kinds = [e.event_kind for e in events]

        # Find indices
        narrator_block_indices = [i for i, k in enumerate(event_kinds) if k == NarrativeEventKind.NARRATOR_BLOCK]
        ruhepunkt_indices = [i for i, k in enumerate(event_kinds) if k == NarrativeEventKind.RUHEPUNKT_REACHED]

        if narrator_block_indices and ruhepunkt_indices:
            assert max(narrator_block_indices) < min(ruhepunkt_indices)

    def test_ruhepunkt_signal_emitted_when_initiatives_exhausted(self, narrator_agent, sample_agent_input):
        """Ruhepunkt signal emitted when remaining initiatives reach 0."""
        events = list(narrator_agent.stream_narrator_blocks(sample_agent_input))
        event_kinds = [e.event_kind for e in events]
        assert NarrativeEventKind.RUHEPUNKT_REACHED in event_kinds

    def test_streaming_complete_event_emitted(self, narrator_agent, sample_agent_input):
        """Streaming complete event emitted at end."""
        events = list(narrator_agent.stream_narrator_blocks(sample_agent_input))
        event_kinds = [e.event_kind for e in events]
        assert NarrativeEventKind.STREAMING_COMPLETE in event_kinds

    def test_event_sequence_increments(self, narrator_agent, sample_agent_input):
        """Event sequence numbers increment for each event."""
        events = list(narrator_agent.stream_narrator_blocks(sample_agent_input))
        sequence_numbers = [e.sequence_number for e in events]
        assert sequence_numbers == list(range(1, len(events) + 1))


class TestMotivationAnalysis:
    """Test NPC motivation pressure analysis."""

    def test_analyze_motivation_pressure_counts_initiatives(self, narrator_agent, sample_agent_input):
        """Motivation analysis counts remaining unresolved initiatives."""
        analysis = narrator_agent._analyze_motivation_pressure(sample_agent_input)
        assert analysis["remaining_initiatives"] == 2  # Two unresolved in sample

    def test_analyze_motivation_pressure_identifies_actors(self, narrator_agent, sample_agent_input):
        """Motivation analysis identifies NPCs with initiatives."""
        analysis = narrator_agent._analyze_motivation_pressure(sample_agent_input)
        assert "annette" in analysis["initiative_actors"]
        assert "alain" in analysis["initiative_actors"]

    def test_analyze_motivation_pressure_zero_when_all_resolved(self, narrator_agent, sample_agent_input):
        """Remaining initiatives is zero when all resolved."""
        sample_agent_input.npc_agency_plan["initiatives"] = [
            {
                "actor_id": "annette",
                "initiative_type": "challenge_authority",
                "resolved": True,
                "motivation_intensity": 0.8,
            },
        ]
        analysis = narrator_agent._analyze_motivation_pressure(sample_agent_input)
        assert analysis["remaining_initiatives"] == 0


class TestNarratorValidation:
    """Test narrative voice validation rules."""

    def test_validate_rejects_modal_language_you_feel(self, narrator_agent, sample_agent_input):
        """Validation rejects modal language that forces player state."""
        invalid_block = {
            "narrator_text": "You feel a chill run down your spine.",
            "sequence": 0,
        }
        error = narrator_agent._validate_narrative_output(invalid_block, sample_agent_input)
        assert error is not None
        assert "modal language" in error.lower()

    def test_validate_rejects_modal_language_you_realize(self, narrator_agent, sample_agent_input):
        """Validation rejects 'you realize' language."""
        invalid_block = {
            "narrator_text": "You realize that Annette's strategy is faltering.",
            "sequence": 0,
        }
        error = narrator_agent._validate_narrative_output(invalid_block, sample_agent_input)
        assert error is not None

    def test_validate_rejects_hidden_intent_revelation(self, narrator_agent, sample_agent_input):
        """Validation rejects revelation of hidden NPC intent."""
        invalid_block = {
            "narrator_text": "Alain secretly plans to undermine Annette's authority.",
            "sequence": 0,
        }
        error = narrator_agent._validate_narrative_output(invalid_block, sample_agent_input)
        assert error is not None
        assert "hidden" in error.lower() or "intent" in error.lower()

    def test_validate_accepts_inner_perception(self, narrator_agent, sample_agent_input):
        """Validation accepts inner perception without forcing state."""
        valid_block = {
            "narrator_text": "The tension in the room is palpable. Alain leans forward, his expression hardening.",
            "sequence": 0,
        }
        error = narrator_agent._validate_narrative_output(valid_block, sample_agent_input)
        assert error is None

    def test_validate_accepts_narrative_threads(self, narrator_agent, sample_agent_input):
        """Validation accepts reference to narrative threads."""
        valid_block = {
            "narrator_text": "The unresolved power dynamic threads itself through the silence.",
            "sequence": 0,
        }
        error = narrator_agent._validate_narrative_output(valid_block, sample_agent_input)
        assert error is None


class TestEventSerialization:
    """Test event serialization to JSON."""

    def test_event_serializes_to_json(self, narrator_agent, sample_agent_input):
        """Events serialize to valid JSON."""
        events = list(narrator_agent.stream_narrator_blocks(sample_agent_input))
        for event in events:
            json_str = event.to_json()
            assert json_str is not None
            assert isinstance(json_str, str)
            # Should be parseable
            import json
            data = json.loads(json_str)
            assert "event_id" in data
            assert "event_kind" in data

    def test_event_json_contains_timestamp(self, narrator_agent, sample_agent_input):
        """Event JSON contains ISO timestamp."""
        events = list(narrator_agent.stream_narrator_blocks(sample_agent_input))
        for event in events:
            json_str = event.to_json()
            import json
            data = json.loads(json_str)
            # Should be ISO format
            assert "T" in data["timestamp"]


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_npc_agency_plan(self, narrator_agent):
        """Agent handles empty NPC agency plan gracefully."""
        agent_input = NarrativeRuntimeAgentInput(
            runtime_state={"scene_id": "test"},
            npc_agency_plan={},  # Empty
            dramatic_signature={},
            narrative_threads=[],
            session_id="test",
            turn_number=1,
        )
        events = list(narrator_agent.stream_narrator_blocks(agent_input))
        # Should still emit ruhepunkt and complete
        event_kinds = [e.event_kind for e in events]
        assert NarrativeEventKind.RUHEPUNKT_REACHED in event_kinds

    def test_max_narrator_blocks_respected(self, narrator_agent):
        """Agent stops at max_narrator_blocks limit."""
        narrator_agent.config.max_narrator_blocks = 3
        # Create input with many initiatives
        many_initiatives = [
            {"actor_id": f"npc_{i}", "resolved": False}
            for i in range(20)
        ]
        agent_input = NarrativeRuntimeAgentInput(
            runtime_state={"scene_id": "test"},
            npc_agency_plan={"initiatives": many_initiatives},
            dramatic_signature={},
            narrative_threads=[],
            session_id="test",
            turn_number=1,
        )
        events = list(narrator_agent.stream_narrator_blocks(agent_input))
        narrator_blocks = [e for e in events if e.event_kind == NarrativeEventKind.NARRATOR_BLOCK]
        assert len(narrator_blocks) <= 3

    def test_error_event_on_invalid_narrator_output(self, narrator_agent, sample_agent_input):
        """Error event emitted if narrator output validation fails."""
        # Mock _generate_narrator_block to return invalid output
        original_generate = narrator_agent._generate_narrator_block
        def mock_generate(*args, **kwargs):
            return {"narrator_text": "You feel scared and confused by Alain's moves."}
        narrator_agent._generate_narrator_block = mock_generate

        try:
            events = list(narrator_agent.stream_narrator_blocks(sample_agent_input))
            event_kinds = [e.event_kind for e in events]
            # Should emit error
            assert NarrativeEventKind.ERROR in event_kinds
        finally:
            narrator_agent._generate_narrator_block = original_generate


@pytest.mark.mvp3
class TestMVP3Gate:
    """MVP3 gate verification for NarrativeRuntimeAgent core."""

    def test_mvp3_narrative_agent_streams_continuously(self, narrator_agent, sample_agent_input):
        """Gate: Agent streams narrator blocks continuously (not turn-sequential)."""
        events = list(narrator_agent.stream_narrator_blocks(sample_agent_input))
        narrator_events = [e for e in events if e.event_kind == NarrativeEventKind.NARRATOR_BLOCK]
        # Should have at least one narrator block
        assert len(narrator_events) >= 1

    def test_mvp3_narrative_agent_respects_motivation_pressure(self, narrator_agent, sample_agent_input):
        """Gate: Agent generates blocks based on NPC motivation pressure."""
        analysis = narrator_agent._analyze_motivation_pressure(sample_agent_input)
        assert analysis["pressure_score"] > 0
        assert analysis["remaining_initiatives"] > 0

    def test_mvp3_narrative_agent_signals_ruhepunkt(self, narrator_agent, sample_agent_input):
        """Gate: Agent signals ruhepunkt when initiatives exhausted."""
        events = list(narrator_agent.stream_narrator_blocks(sample_agent_input))
        ruhepunkt_events = [e for e in events if e.event_kind == NarrativeEventKind.RUHEPUNKT_REACHED]
        assert len(ruhepunkt_events) == 1
        assert ruhepunkt_events[0].data["ruhepunkt_reached"] is True

    def test_mvp3_narrative_validation_enforces_voice_rules(self, narrator_agent, sample_agent_input):
        """Gate: Narrator validation enforces all voice rules."""
        # Test all three major rules
        rules_tested = 0

        # Rule 1: Modal language
        invalid1 = {"narrator_text": "You feel trapped."}
        if narrator_agent._validate_narrative_output(invalid1, sample_agent_input):
            rules_tested += 1

        # Rule 2: Hidden intent
        invalid2 = {"narrator_text": "Alain secretly wants to dominate."}
        if narrator_agent._validate_narrative_output(invalid2, sample_agent_input):
            rules_tested += 1

        # Rule 3: Valid perception
        valid = {"narrator_text": "The air grows cold as Alain rises."}
        if narrator_agent._validate_narrative_output(valid, sample_agent_input) is None:
            rules_tested += 1

        assert rules_tested >= 3
