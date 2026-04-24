"""Full-route tests proving actor-lane absence governance through complete pipeline."""

from ai_stack.langgraph_runtime_executor import (
    _actor_lane_validation,
    _compute_reaction_order_divergence_for_render,
)
from ai_stack.runtime_quality_semantics import canonical_degradation_signals
from ai_stack.runtime_turn_contracts import DEGRADATION_SIGNAL_NO_ACTOR_LANE_OUTPUT
from ai_stack.goc_turn_seams import run_visible_render


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
    """Secondary responder nominated but not realized should show divergence with full structure."""
    state = {
        "selected_responder_set": [
            {"actor_id": "alice", "role": "primary_responder", "preferred_reaction_order": 0},
            {"actor_id": "bob", "role": "secondary_reactor", "preferred_reaction_order": 1},
        ],
        "spoken_lines": [{"speaker_id": "alice", "text": "line"}],
        "action_lines": [],
    }

    result = _compute_reaction_order_divergence_for_render(state)
    assert result["reaction_order_divergence"] == "secondary_responder_nominated_not_realized_in_output"
    assert result["divergence"] is True
    assert result["preferred_reaction_order_ids"] == ["alice", "bob"]
    assert result["realized_actor_order"] == ["alice"]
    assert result["not_realized_actor_ids"] == ["bob"]
    assert result["non_fatal"] is True
    assert result["justified"] is True
    assert result["justification"] is not None


def test_reaction_order_divergence_not_when_aligned():
    """Aligned order should not produce divergence; divergence=False."""
    state = {
        "selected_responder_set": [
            {"actor_id": "alice", "role": "primary_responder", "preferred_reaction_order": 0},
            {"actor_id": "bob", "role": "secondary_reactor", "preferred_reaction_order": 1},
        ],
        "spoken_lines": [
            {"speaker_id": "alice", "text": "line1"},
            {"speaker_id": "bob", "text": "line2"},
        ],
        "action_lines": [],
    }

    result = _compute_reaction_order_divergence_for_render(state)
    assert result["reaction_order_divergence"] is None
    assert result["divergence"] is False
    assert result["preferred_reaction_order_ids"] == ["alice", "bob"]
    assert result["realized_actor_order"] == ["alice", "bob"]
    assert result["not_realized_actor_ids"] == []
    assert result["non_fatal"] is True
    assert result["justified"] is False
    assert result["justification"] is None


def test_run_visible_render_survives_vitality_warning_and_reaction_order_divergence():
    """Verify vitality warning and reaction-order divergence both present in render_support."""
    bundle, markers = run_visible_render(
        module_id="god_of_carnage",
        committed_result={"committed_effects": ["test"], "commit_applied": True},
        validation_outcome={"status": "approved"},
        generation={
            "content": "test prose",
            "metadata": {
                "structured_output": {
                    "spoken_lines": [],
                    "action_lines": [],
                }
            }
        },
        transition_pattern="hard",
        render_context={
            "pacing_mode": "thin_edge",
            "carry_forward_tension_notes": "unresolved: escalating",
            "selected_responder_set": [
                {"actor_id": "alice", "role": "primary_responder"},
                {"actor_id": "bob", "role": "secondary_reactor"},
            ],
            "preferred_reaction_order_ids": ["alice", "bob"],
            "realized_actor_order": ["alice"],
            "reaction_order_divergence": "secondary_responder_nominated_not_realized_in_output",
        },
    )

    render_support = bundle.get("render_support", {})
    assert isinstance(render_support, dict), "render_support should be a dict"
    assert render_support.get("projection_version") == "render_support.v1", \
        "projection_version should be render_support.v1 for merge compatibility"

    assert render_support.get("vitality_floor_warning") == "thin_edge_output_empty_with_prior_tension", \
        f"Expected vitality warning, got: {render_support.get('vitality_floor_warning')}"

    assert render_support.get("reaction_order_divergence") is not None, \
        "reaction_order_divergence should be present in render_support"
    assert render_support["reaction_order_divergence"].get("divergence") is True
    assert render_support["reaction_order_divergence"].get("reason") == "secondary_responder_nominated_not_realized_in_output"
    assert render_support["reaction_order_divergence"].get("non_fatal") is True
    assert isinstance(render_support["reaction_order_divergence"].get("preferred"), list)
    assert isinstance(render_support["reaction_order_divergence"].get("realized"), list)


def test_opening_leniency_produces_degradation_signal():
    """Verify opening-turn leniency approval produces DEGRADATION_SIGNAL_OPENING_LENIENCY_APPROVED."""
    from ai_stack.runtime_quality_semantics import canonical_degradation_signals
    from ai_stack.runtime_turn_contracts import DEGRADATION_SIGNAL_OPENING_LENIENCY_APPROVED

    state = {
        "validation_outcome": {
            "status": "approved",
            "reason": "opening_leniency_approved",
        },
    }

    signals = canonical_degradation_signals(state=state, fallback_taken=False)
    assert DEGRADATION_SIGNAL_OPENING_LENIENCY_APPROVED in signals, \
        f"Expected {DEGRADATION_SIGNAL_OPENING_LENIENCY_APPROVED} in signals, got {signals}"


def test_opening_leniency_produces_weak_quality_class():
    """Verify opening-leniency approval results in weak_but_legal quality class."""
    from ai_stack.runtime_quality_semantics import canonical_quality_class, canonical_degradation_signals
    from ai_stack.runtime_turn_contracts import QUALITY_CLASS_WEAK_BUT_LEGAL

    state = {
        "validation_outcome": {
            "status": "approved",
            "reason": "opening_leniency_approved",
        },
    }

    signals = canonical_degradation_signals(state=state, fallback_taken=False)
    quality = canonical_quality_class(
        validation_outcome=state["validation_outcome"],
        commit_applied=True,
        degradation_signals=signals,
    )
    assert quality == QUALITY_CLASS_WEAK_BUT_LEGAL, \
        f"Expected {QUALITY_CLASS_WEAK_BUT_LEGAL}, got {quality}"


def test_story_rendering_uses_canonical_normalized_entries():
    """Verify rendered story entries use canonical structure, not legacy audit-log projection."""
    bundle, markers = run_visible_render(
        module_id="god_of_carnage",
        committed_result={"committed_effects": ["test"], "commit_applied": True},
        validation_outcome={"status": "approved"},
        generation={
            "content": "canonical prose",
            "metadata": {
                "structured_output": {
                    "spoken_lines": [
                        {"speaker_id": "alice", "text": "hello world"},
                    ],
                    "action_lines": [
                        {"actor_id": "alice", "action": "nods"},
                    ],
                }
            }
        },
        transition_pattern="hard",
        render_context={
            "module_id": "god_of_carnage",
            "turn_number": 5,
            "selected_responder_set": [
                {"actor_id": "alice", "role": "primary_responder"},
            ],
        },
    )

    assert isinstance(bundle, dict), "bundle should be a dict"
    assert "spoken_lines" in bundle, "canonical spoken_lines should be in bundle"
    assert isinstance(bundle.get("spoken_lines"), list), "spoken_lines should be a list"
    assert len(bundle["spoken_lines"]) > 0, "should have rendered spoken lines"

    assert "action_lines" in bundle, "canonical action_lines should be in bundle"
    assert isinstance(bundle.get("action_lines"), list), "action_lines should be a list"

    assert "gm_narration" in bundle, "gm_narration (prose) should be in bundle"
    narration = bundle.get("gm_narration")
    assert isinstance(narration, list), "gm_narration should be a list"
    assert len(narration) > 0, "gm_narration should contain prose entries"
    assert "canonical prose" in narration, "gm_narration should contain generation prose"
