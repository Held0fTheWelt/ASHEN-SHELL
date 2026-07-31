"""Wave 3: free role-play commit vocabulary (partial vs blocked)."""
from __future__ import annotations

from world_engine.story_runtime.commit_models import resolve_narrative_commit
from world_engine.story_runtime.narrative_commit_resolution import eval_core_transition_rules


def test_free_action_without_scene_transition_commits_partial() -> None:
    work = eval_core_transition_rules(
        proposed_scene_id="scene_2",
        prior_scene_id="scene_1",
        known_scene_ids={"scene_1", "scene_2"},
        has_transition_rules=True,
        transition_map={"scene_1": {"scene_3"}},  # scene_2 not allowed
        model_raw="scene_2",
        consequences=[],
    )
    assert work.situation_status == "partial"
    assert work.allowed is True
    assert work.committed_scene_id == "scene_1"
    assert work.commit_reason_code == "illegal_transition_not_allowed"

    rec = resolve_narrative_commit(
        turn_number=2,
        prior_scene_id="scene_1",
        player_input="I confront Michel about the ruined notebook.",
        interpreted_input={"kind": "speech", "confidence": 0.9},
        generation={
            "success": True,
            "metadata": {"structured_output": {"proposed_scene_id": "scene_2"}},
        },
        runtime_projection={
            "start_scene_id": "scene_1",
            "scenes": [{"id": "scene_1"}, {"id": "scene_2"}],
            "transition_hints": [{"from": "scene_1", "to": "scene_3"}],
        },
        graph_state={"selected_scene_function": "escalate_conflict"},
    )
    assert rec.situation_status == "partial"
    assert rec.allowed is True
    assert rec.beat_progression is not None
    assert rec.beat_progression.advancement_reason != "blocked_turn_no_advance"
    assert "partial" in rec.beat_progression.advancement_reason or rec.beat_progression.advanced is True


def test_prevented_action_still_witnessed() -> None:
    """Prevented outcomes still produce a beat tick (witnessed, not frozen)."""
    from world_engine.story_runtime.commit_models import BeatProgression, PlannerTruth, _resolve_beat_progression

    prior = BeatProgression(
        beat_id="scene_1:escalate_conflict",
        beat_slot=1,
        pressure_state="tension",
        pacing_carry_forward="measured",
        responder_focus_carry_forward=[],
        advanced=False,
        advancement_reason="continuity_carry_forward",
        continuity_carry_forward_reason="tension",
        prior_beat_id=None,
    )
    planner = PlannerTruth(
        selected_scene_function="escalate_conflict",
        pacing_mode="measured",
        responder_id=None,
        responder_scope=[],
    )
    bp = _resolve_beat_progression(
        graph_state={},
        planner=planner,
        committed_scene_id="scene_1",
        prior_scene_id="scene_1",
        situation_status="prevented",
        prior_beat=prior,
    )
    assert bp.advanced is True
    assert bp.advancement_reason == "prevented_but_witnessed"
    assert bp.beat_slot == 2


def test_blocked_is_rare_unknown_scene_only() -> None:
    work = eval_core_transition_rules(
        proposed_scene_id="scene_missing",
        prior_scene_id="scene_1",
        known_scene_ids={"scene_1", "scene_2"},
        has_transition_rules=True,
        transition_map={"scene_1": {"scene_2"}},
        model_raw="scene_missing",
        consequences=[],
    )
    assert work.situation_status == "blocked"
    assert work.allowed is False
    assert work.commit_reason_code == "unknown_target_scene"
