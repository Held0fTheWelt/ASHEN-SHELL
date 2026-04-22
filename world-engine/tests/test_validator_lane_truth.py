"""Tests for the canonical live validator lane and the operator
introspection validator lane.

Live player turns validate through the graph's ``run_validation_seam``,
which records ``validator_lane="goc_rule_engine_v1"`` on each committed
turn. The world-engine narrative validator exposed at
``/internal/narrative/runtime/validate-and-recover`` is a separate
operator-introspection lane that reports
``validator_lane="operator_introspection_validate_and_recover"`` so
operators cannot mistake its output for live-turn validation evidence.

These tests pin the labeling and the truth-surface publication.
"""

from __future__ import annotations

from app.story_runtime.commit_models import (
    PlannerTruth,
    resolve_narrative_commit,
)
from app.story_runtime.manager import StoryRuntimeManager


def test_planner_truth_validator_layers_from_live_seam() -> None:
    """When validation_outcome has no explicit layers_used list, the extractor
    infers the set from validator_lane + dramatic_effect_gate — so downstream
    readers can still audit which validator layers ran."""
    rec = resolve_narrative_commit(
        turn_number=2,
        prior_scene_id="s1",
        player_input="hello",
        interpreted_input={"kind": "free_narration"},
        generation={"success": True, "metadata": {"structured_output": {}}},
        runtime_projection={"scenes": [{"scene_id": "s1"}]},
        graph_state={
            "validation_outcome": {
                "status": "approved",
                "reason": "goc_default_validator_pass",
                "validator_lane": "goc_rule_engine_v1",
            },
            "dramatic_effect_gate_outcome": {"gate_result": "accepted_clean"},
        },
    )
    pt = rec.planner_truth
    assert isinstance(pt, PlannerTruth)
    assert "goc_rule_engine_v1" in pt.validator_layers_used
    assert "dramatic_effect_gate" in pt.validator_layers_used


def test_planner_truth_prefers_explicit_validator_layers_list() -> None:
    rec = resolve_narrative_commit(
        turn_number=2,
        prior_scene_id="s1",
        player_input="hello",
        interpreted_input={"kind": "free_narration"},
        generation=None,
        runtime_projection={"scenes": [{"scene_id": "s1"}]},
        graph_state={
            "validation_outcome": {
                "status": "approved",
                "layers_used": ["scene_packet", "responder_scope", "trigger_legality"],
                "validator_lane": "goc_rule_engine_v1",
            },
        },
    )
    assert rec.planner_truth.validator_layers_used == [
        "scene_packet",
        "responder_scope",
        "trigger_legality",
    ]


def test_runtime_truth_surface_publishes_live_validator_lane_identity() -> None:
    mgr = StoryRuntimeManager(governed_runtime_config=None)
    ts = mgr.runtime_config_status().get("runtime_truth_surface") or {}

    assert ts.get("live_validator_lane") == "goc_rule_engine_v1"
    stages = ts.get("live_validator_stages") or []
    assert "run_validation_seam" in stages
    assert "dramatic_effect_gate" in stages
    # The operator endpoint must be named as a separate lane so operators know
    # its output is not live-turn evidence.
    assert (
        ts.get("operator_introspection_validator_endpoint")
        == "/api/internal/narrative/runtime/validate-and-recover"
    )
