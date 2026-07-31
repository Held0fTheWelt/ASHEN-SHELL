"""Wave 3: blocked is reserved for situatively impossible outcomes only."""
from __future__ import annotations

from world_engine.story_runtime.narrative_commit_resolution import eval_core_transition_rules
from world_engine.story_runtime.situation_status_mapping import (
    AI_AFFORDANCE_STATUSES,
    AI_TO_SITUATION_STATUS,
    map_ai_affordance_to_situation_status,
    mapping_is_not_poorer,
)


def test_blocked_only_for_impossible_unknown_scene() -> None:
    work = eval_core_transition_rules(
        proposed_scene_id="no_such_scene",
        prior_scene_id="scene_1",
        known_scene_ids={"scene_1", "scene_2"},
        has_transition_rules=True,
        transition_map={"scene_1": {"scene_2"}},
        model_raw="no_such_scene",
        consequences=[],
    )
    assert work.situation_status == "blocked"
    assert work.commit_reason_code == "unknown_target_scene"


def test_off_map_transition_is_not_blocked() -> None:
    work = eval_core_transition_rules(
        proposed_scene_id="scene_2",
        prior_scene_id="scene_1",
        known_scene_ids={"scene_1", "scene_2"},
        has_transition_rules=True,
        transition_map={"scene_1": {"scene_3"}},
        model_raw="scene_2",
        consequences=[],
    )
    assert work.situation_status == "partial"
    assert work.allowed is True


def test_no_resolution_status_maps_to_poorer_commit_status() -> None:
    assert AI_AFFORDANCE_STATUSES == frozenset(AI_TO_SITUATION_STATUS)
    for ai_status in sorted(AI_AFFORDANCE_STATUSES):
        mapped = map_ai_affordance_to_situation_status(ai_status)
        assert mapping_is_not_poorer(ai_status, mapped)
        # partial / prevented / offscreen must never collapse to blocked
        if ai_status in {"partial", "prevented", "allowed_offscreen", "allowed"}:
            assert mapped != "blocked"
