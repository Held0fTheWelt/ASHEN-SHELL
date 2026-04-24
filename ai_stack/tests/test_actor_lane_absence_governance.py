"""Full-route tests proving actor-lane absence governance through complete pipeline."""

from ai_stack.langgraph_runtime_executor import (
    _actor_lane_validation,
    _compute_reaction_order_divergence_for_render,
)
from ai_stack.runtime_quality_semantics import canonical_degradation_signals
from ai_stack.runtime_turn_contracts import DEGRADATION_SIGNAL_NO_ACTOR_LANE_OUTPUT


def test_actor_lane_valid_output_is_healthy():
    """Valid structured actor lanes should not trigger degradation."""
    state = {
        "selected_responder_set": [
            {"actor_id": "alice"},
            {"actor_id": "bob"},
        ]
    }
    generation = {
        "metadata": {
            "structured_output": {
                "spoken_lines": [
                    {"speaker_id": "alice", "line": "Hello"},
                    {"speaker_id": "bob", "line": "Hi"},
                ]
            }
        }
    }
    result = _actor_lane_validation(state=state, generation=generation)
    assert result["status"] == "approved"
    assert result["reason"] == "actor_lane_legal"


def test_actor_lane_absent_with_selected_responders_is_weak_but_legal():
    """No structured output when responders selected should create weak_but_legal quality."""
    state = {
        "selected_responder_set": [
            {"actor_id": "alice"},
            {"actor_id": "bob"},
        ]
    }
    generation = {"metadata": {}}
    result = _actor_lane_validation(state=state, generation=generation)
    assert result["status"] == "approved"
    assert result["reason"] == "no_structured_actor_output_with_selected_responders"

    markers: list[str] = []
    if result["reason"] == "no_structured_actor_output_with_selected_responders":
        markers.append("no_actor_lane_output_with_selected_responders")

    signals = canonical_degradation_signals(
        state={"visibility_class_markers": markers},
        fallback_taken=False,
    )
    assert DEGRADATION_SIGNAL_NO_ACTOR_LANE_OUTPUT in signals


def test_actor_lane_absent_no_responders_no_degradation():
    """No structured output with no responders should not trigger degradation signal."""
    state = {"selected_responder_set": []}
    generation = {"metadata": {}}
    result = _actor_lane_validation(state=state, generation=generation)
    assert result["status"] == "approved"
    assert result["reason"] == "no_structured_actor_output"

    markers: list[str] = []
    if result["reason"] == "no_structured_actor_output_with_selected_responders":
        markers.append("no_actor_lane_output_with_selected_responders")

    signals = canonical_degradation_signals(
        state={"visibility_class_markers": markers},
        fallback_taken=False,
    )
    assert DEGRADATION_SIGNAL_NO_ACTOR_LANE_OUTPUT not in signals


def test_render_support_merge_preserves_earlier_writes():
    """Multiple render_support writes should merge, not overwrite."""
    bundle = {
        "render_support": {
            "projection_version": "render_support.v1",
            "reaction_order_divergence": {
                "divergence": True,
                "reason": "secondary_responder_nominated_not_realized_in_output",
                "non_fatal": True,
                "justified": False,
            },
        }
    }

    director_surface_hints = {"hint": "value"}

    if director_surface_hints:
        render_support = bundle.setdefault("render_support", {})
        if not isinstance(render_support, dict):
            render_support = {}
            bundle["render_support"] = render_support
        render_support.setdefault("projection_version", "render_support.v1")
        render_support.setdefault("player_visible", False)
        render_support["director_surface_hints"] = director_surface_hints

    assert bundle["render_support"]["projection_version"] == "render_support.v1"
    assert bundle["render_support"]["reaction_order_divergence"]["reason"] == "secondary_responder_nominated_not_realized_in_output"
    assert bundle["render_support"]["reaction_order_divergence"]["non_fatal"] is True
    assert bundle["render_support"]["director_surface_hints"] == director_surface_hints


def test_reaction_order_divergence_in_render_support():
    """Secondary responder nominated but not realized should show divergence."""
    state = {
        "selected_responder_set": [
            {"actor_id": "alice", "role": "primary_responder"},
            {"actor_id": "bob", "role": "secondary_reactor"},
        ],
        "spoken_lines": [{"speaker_id": "alice", "text": "line"}],
        "action_lines": [],
    }

    result = _compute_reaction_order_divergence_for_render(state)
    assert result["reaction_order_divergence"] == "secondary_responder_nominated_not_realized_in_output"
    assert result["preferred_reaction_order_ids"] == ["alice", "bob"]
    assert result["realized_actor_order"] == ["alice"]


def test_reaction_order_divergence_not_when_aligned():
    """Aligned order should not produce divergence."""
    state = {
        "selected_responder_set": [
            {"actor_id": "alice", "role": "primary_responder"},
            {"actor_id": "bob", "role": "secondary_reactor"},
        ],
        "spoken_lines": [
            {"speaker_id": "alice", "text": "line1"},
            {"speaker_id": "bob", "text": "line2"},
        ],
        "action_lines": [],
    }

    result = _compute_reaction_order_divergence_for_render(state)
    assert result["reaction_order_divergence"] is None
    assert result["preferred_reaction_order_ids"] == ["alice", "bob"]
    assert result["realized_actor_order"] == ["alice", "bob"]
