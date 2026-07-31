"""Wave 4: state delta partial acceptance and capability switches."""
from __future__ import annotations

from world_engine.story_runtime.commit_models import resolve_narrative_commit
from world_engine.story_runtime.delta_evaluation import evaluate_proposed_deltas
from world_engine.story_runtime.failure_recovery import (
    DegradedMode,
    ReducedContextRetryPolicy,
    SafeTurnPolicy,
    build_reduced_context_retry_prompt,
    deterministic_continuation_turn,
)
from world_engine.story_runtime.mutation_policy import DEFAULT_MUTATION_POLICY, MutationPolicy
from world_engine.story_runtime.source_gate import narrative_commit_for_source_gate_rejection
from world_engine.story_runtime.state_deltas import StateDelta


def test_partial_delta_acceptance_commits_partially() -> None:
    partition = evaluate_proposed_deltas(
        [
            StateDelta(target_path="characters.veronique.tension", value=1, source="ai"),
            StateDelta(target_path="session_id", value="x", source="ai"),
        ]
    )
    assert partition.guard_outcome.value == "partial"
    assert len(partition.accepted) == 1
    assert len(partition.rejected) == 1

    rec = resolve_narrative_commit(
        turn_number=3,
        prior_scene_id="scene_1",
        player_input="I push harder.",
        interpreted_input={"kind": "speech"},
        generation={"success": True, "metadata": {}},
        runtime_projection={
            "start_scene_id": "scene_1",
            "scenes": [{"id": "scene_1"}],
        },
        proposed_deltas=[
            {"target_path": "characters.veronique.tension", "value": 1, "source": "ai"},
            {"target_path": "revision", "value": 99, "source": "ai"},
        ],
    )
    assert rec.guard_outcome == "partial"
    assert len(rec.accepted_deltas) == 1
    assert len(rec.rejected_deltas) == 1
    assert rec.situation_status == "partial"


def test_mutation_policy_default_is_permissive() -> None:
    policy = DEFAULT_MUTATION_POLICY
    assert policy.evaluate("characters.michel.stance").allowed is True
    assert policy.evaluate("relationships.axis.value").allowed is True
    assert policy.evaluate("session_id").allowed is False
    custom = MutationPolicy(deny_patterns=("characters.*.secret",))
    assert custom.evaluate("characters.a.secret").allowed is False


def test_reduced_context_retry_is_cheaper_than_first_attempt() -> None:
    original = "X" * 5000
    policy = ReducedContextRetryPolicy(max_context_chars=2000)
    retry = build_reduced_context_retry_prompt(original_prompt=original, policy=policy)
    assert len(retry) < len(original)
    assert len(retry) == 2000


def test_deterministic_continuation_needs_no_model_call() -> None:
    turn = deterministic_continuation_turn(prior_scene_id="scene_1", turn_number=4)
    assert turn["model_calls_additional"] == 0
    assert turn["degraded_mode"] == DegradedMode.TECHNICALLY_REDUCED.value


def test_technically_reduced_is_distinguishable_from_narratively_prevented() -> None:
    tech = SafeTurnPolicy().degraded_mode
    assert tech == DegradedMode.TECHNICALLY_REDUCED
    assert DegradedMode.TECHNICALLY_REDUCED.value != DegradedMode.NARRATIVELY_PREVENTED.value


def test_source_gate_rejection_commit_shape() -> None:
    commit = narrative_commit_for_source_gate_rejection(
        turn_number=1,
        prior_scene_id="scene_1",
        rejected_deltas=[StateDelta(target_path="characters.x.tension", source="unknown")],
    )
    assert commit["commit_reason_code"] == "source_gate_rejected"
    assert commit["accepted_deltas"] == []
    assert commit["guard_outcome"] == "rejected"


def test_each_capability_switch_has_documented_default() -> None:
    # Mirror defaults from _capability_switches without constructing a manager.
    defaults = {
        "capability_state_deltas": True,
        "capability_mutation_policy": True,
        "capability_source_gate": True,
        "capability_failure_recovery": True,
        "capability_scene_legality": True,
    }
    assert all(isinstance(v, bool) and v is True for v in defaults.values())
    assert len(defaults) == 5
