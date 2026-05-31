"""Phase 6C tests for W5 location framing (ADR-0070)."""

from __future__ import annotations

from pathlib import Path

from ai_stack.actor_tracking import (
    LEGACY_AREA_COMPAT_SCHEMA_VERSION,
    W5_LOCATION_FRAMING_SCHEMA_VERSION,
    W5ActorSituation,
    W5ActorType,
    W5Dimension,
    W5Fact,
    W5FactStatus,
    W5FreshnessStatus,
    W5Projection,
    W5ProjectionConsumer,
    W5Snapshot,
    W5Source,
    W5TruthLevel,
    W5VisibilityScope,
    ensure_legacy_area_fields_for_compat,
    build_w5_location_framing,
    location_framing_to_local_context_transition,
    w5_location_framing_to_legacy_area_fields,
)
from ai_stack.contracts.narrator_consequence_contracts import (
    build_local_context_transition,
    build_narrator_consequence_plan,
)
from ai_stack.story_runtime.narrative.sensory_context_engine import (
    derive_sensory_context,
)


TURN = 7
ACTOR = "annette"
REPO_ROOT = Path(__file__).resolve().parents[2]


def _projection(
    *,
    current: str = "salon",
    previous: str | None = "hallway",
    changed: bool = True,
    how: bool = True,
    inferred_why: bool = True,
) -> W5Projection:
    how_summary = {"facts": {"tone": "controlled", "physicality": "still"}} if how else {"facts": {}}
    why_summary = {"facts": {"motive": "avoid_escalation"}} if inferred_why else {"facts": {}}
    source_attribution = {
        "where_summary.facts.scene_location": "participant_state_move",
        "where_summary.location_changed": "derived_from_where_facts",
        "how_summary.facts.tone": "committed_action",
    }
    truth_attribution = {
        "where_summary.facts.scene_location": "observed",
        "where_summary.location_changed": "observed",
        "how_summary.facts.tone": "observed",
    }
    if inferred_why:
        source_attribution["why_summary.facts.motive"] = "character_mind_record"
        truth_attribution["why_summary.facts.motive"] = "inferred"
    where = {
        "actor_id": ACTOR,
        "facts": {"scene_location": current},
        "current_location": current,
        "location_changed": changed,
    }
    if previous is not None:
        where["previous_location"] = previous
    return W5Projection(
        target_consumer=W5ProjectionConsumer.NARRATOR,
        actor_id=ACTOR,
        where_summary=where,
        what_summary={"facts": {"current_action": "listens"}},
        how_summary=how_summary,
        why_summary=why_summary,
        source_attribution=source_attribution,
        truth_attribution=truth_attribution,
    )


def _fact(
    *,
    fact_id: str,
    location: str,
    actor_id: str = ACTOR,
    truth: W5TruthLevel = W5TruthLevel.OBSERVED,
) -> W5Fact:
    return W5Fact(
        fact_id=fact_id,
        actor_id=actor_id,
        dimension=W5Dimension.WHERE,
        key="scene_location",
        value=location,
        source=W5Source.PARTICIPANT_STATE_MOVE,
        truth_level=truth,
        valid_from_turn=TURN,
        last_confirmed_turn=TURN,
        visibility=W5VisibilityScope.PUBLIC,
        status=W5FactStatus.ACTIVE,
    )


def _snapshot(location: str, *, turn: int) -> W5Snapshot:
    actor = W5ActorSituation(
        actor_id=ACTOR,
        actor_type=W5ActorType.HUMAN,
        actor_role_in_scene="player",
        involvement_type="primary",
        where=(_fact(fact_id=f"where_{turn}", location=location),),
        freshness_status=W5FreshnessStatus.FRESH,
        last_confirmed_turn=turn,
    )
    return W5Snapshot(
        snapshot_id=f"w5_location_framing_{turn}",
        story_session_id="session_location_framing",
        turn_number=turn,
        actors={ACTOR: actor},
        created_at=f"turn:{turn}",
    )


def test_w5_current_location_maps_to_legacy_current_area() -> None:
    framing = build_w5_location_framing(_projection(current="salon", previous=None, changed=False))

    assert framing["schema_version"] == W5_LOCATION_FRAMING_SCHEMA_VERSION
    assert framing["source"] == "w5_projection"
    assert framing["current_location"] == "salon"
    assert framing["scene_location"] == "salon"
    assert framing["current_area"] == "salon"
    assert framing["to_area"] == "salon"
    assert framing["location_changed"] is False


def test_w5_previous_and_current_map_to_from_area_and_to_area() -> None:
    framing = build_w5_location_framing(_projection(current="salon", previous="hallway", changed=True))
    transition = location_framing_to_local_context_transition(framing)

    assert framing["previous_location"] == "hallway"
    assert framing["from_area"] == "hallway"
    assert framing["to_area"] == "salon"
    assert transition["from_area"] == "hallway"
    assert transition["from_location_id"] == "hallway"
    assert transition["to_area"] == "salon"
    assert transition["to_location_id"] == "salon"
    assert transition["current_area"] == "salon"


def test_w5_location_changed_maps_to_scene_changed_equivalent() -> None:
    framing = build_w5_location_framing(_projection(current="salon", previous="hallway", changed=True))
    transition = location_framing_to_local_context_transition(framing)

    assert framing["location_changed"] is True
    assert framing["scene_changed"] is True
    assert transition["location_changed"] is True
    assert transition["scene_changed"] is True
    assert transition["w5_location_framing"]["w5_location_changed"] is True
    assert transition["location_framing_authority"] == "w5"
    assert transition["local_context_transition_source"] == "w5_location_framing"


def test_no_location_change_preserves_legacy_movement_target_for_parity() -> None:
    framing = build_w5_location_framing(_projection(current="salon", previous=None, changed=False))
    transition = location_framing_to_local_context_transition(
        framing,
        legacy_transition={
            "from_area": "salon",
            "from_location_id": "salon",
            "to_area": "kitchen",
            "to_location_id": "kitchen",
            "transition_type": "movement",
            "new_area_established": True,
        },
    )

    assert transition["from_area"] == "salon"
    assert transition["to_area"] == "kitchen"
    assert transition["to_location_id"] == "kitchen"
    assert transition["current_area"] == "kitchen"
    assert transition["location_changed"] is False
    assert transition["location_framing_authority"] == "legacy_fallback"
    assert transition["local_context_transition_source"] == "legacy"


def test_valid_w5_current_location_is_primary_over_legacy_current_area() -> None:
    scene_model = {"scene_affordances": {"current_area": "salon", "locations": []}}
    framing = build_w5_location_framing(_projection(current="kitchen", previous="salon", changed=True))
    transition = build_local_context_transition(
        player_action_frame={"action_kind": "posture_change"},
        affordance_resolution={"affordance_status": "allowed"},
        scene_affordance_model=scene_model,
        current_player_local_context={"current_area": "salon", "current_location_id": "salon"},
        w5_location_framing=framing,
    )

    assert transition["from_area"] == "salon"
    assert transition["to_area"] == "kitchen"
    assert transition["current_area"] == "kitchen"
    assert transition["location_changed"] is True
    assert transition["location_framing_authority"] == "w5"
    assert transition["local_context_transition_source"] == "w5_location_framing"


def test_phase_6c4_valid_w5_marks_legacy_area_fields_as_compatibility_not_authority() -> None:
    framing = build_w5_location_framing(_projection(current="kitchen", previous="salon", changed=True))
    transition = location_framing_to_local_context_transition(
        framing,
        legacy_transition={
            "from_area": "salon",
            "from_location_id": "salon",
            "to_area": "hallway",
            "to_location_id": "hallway",
            "transition_type": "movement",
            "new_area_established": True,
        },
    )

    assert transition["location_framing_authority"] == "w5"
    assert transition["local_context_transition_source"] == "w5_location_framing"
    assert transition["from_area"] == "salon"
    assert transition["to_area"] == "kitchen"
    assert transition["current_area"] == "kitchen"
    assert transition["to_area"] != "hallway"


def test_w5_location_changed_true_overrides_legacy_transition_target() -> None:
    framing = build_w5_location_framing(_projection(current="kitchen", previous="salon", changed=True))
    transition = location_framing_to_local_context_transition(
        framing,
        legacy_transition={
            "from_area": "salon",
            "from_location_id": "salon",
            "to_area": "hallway",
            "to_location_id": "hallway",
            "transition_type": "movement",
            "new_area_established": True,
            "location_found": True,
        },
    )

    assert transition["from_area"] == "salon"
    assert transition["to_area"] == "kitchen"
    assert transition["current_area"] == "kitchen"
    assert transition["location_framing_authority"] == "w5"
    assert transition["local_context_transition_source"] == "w5_location_framing"


def test_same_location_yields_location_changed_false() -> None:
    current = _snapshot("salon", turn=TURN)
    previous = _snapshot("salon", turn=TURN - 1)
    framing = build_w5_location_framing(current.to_dict(), previous_w5_value=previous.to_dict())

    assert framing["source"] == "w5_projection"
    assert framing["current_location"] == "salon"
    assert framing["previous_location"] == "salon"
    assert framing["location_changed"] is False
    assert framing["scene_changed"] is False


def test_missing_w5_uses_legacy_fallback_without_crash() -> None:
    framing = build_w5_location_framing(
        None,
        legacy_fallback={"current_area": "living_room", "from_area": "hallway", "scene_changed": True},
    )

    assert framing["source"] == "legacy_fallback"
    assert framing["fallback_reason"] == "missing_w5"
    assert framing["current_location"] == "living_room"
    assert framing["previous_location"] == "hallway"
    assert framing["location_changed"] is True


def test_malformed_w5_uses_legacy_fallback_without_crash() -> None:
    framing = build_w5_location_framing(
        {"target_consumer": "narrator", "schema_version": "invalid"},
        legacy_fallback={"to_area": "kitchen", "from_area": "salon"},
    )

    assert framing["source"] == "legacy_fallback"
    assert framing["fallback_reason"] == "malformed_w5"
    assert framing["current_location"] == "kitchen"
    assert framing["previous_location"] == "salon"
    assert framing["location_changed"] is True
    assert "malformed_w5" in framing["warnings"]
    transition = location_framing_to_local_context_transition(framing)
    assert transition["w5_location_framing"]["w5_location_framing_failed"] is True
    assert transition["location_framing_authority"] == "legacy_fallback"
    assert transition["local_context_transition_source"] == "legacy"


def test_malformed_w5_with_legacy_transition_preserves_legacy_authority() -> None:
    framing = build_w5_location_framing(
        {"target_consumer": "narrator", "schema_version": "invalid"},
        legacy_fallback={"to_area": "kitchen", "from_area": "salon"},
    )
    transition = location_framing_to_local_context_transition(
        framing,
        legacy_transition={
            "from_area": "salon",
            "to_area": "hallway",
            "transition_type": "movement",
            "new_area_established": True,
        },
    )

    assert transition["to_area"] == "hallway"
    assert transition["location_framing_authority"] == "legacy_fallback"
    assert transition["local_context_transition_source"] == "legacy"


def test_old_payload_without_w5_uses_legacy_local_context_transition() -> None:
    transition = build_local_context_transition(
        player_action_frame={"action_kind": "posture_change"},
        affordance_resolution={"affordance_status": "allowed"},
        scene_affordance_model={"scene_affordances": {"current_area": "salon", "locations": []}},
        current_player_local_context={"current_area": "salon"},
    )

    assert transition["from_area"] == "salon"
    assert "w5_location_framing" not in transition


def test_how_remains_first_class_and_not_folded_into_what() -> None:
    projection = _projection(current="salon", previous="hallway", changed=True)
    framing = build_w5_location_framing(projection)

    assert framing["has_how"] is True
    assert framing["how_summary"]["facts"]["tone"] == "controlled"
    assert projection.what_summary["facts"] == {"current_action": "listens"}
    assert "tone" not in projection.what_summary["facts"]


def test_inferred_why_remains_soft_truth() -> None:
    framing = build_w5_location_framing(_projection(inferred_why=True))

    assert framing["has_inferred_why"] is True
    assert framing["why_summary"]["facts"]["motive"] == "avoid_escalation"
    assert framing["truth_attribution"]["why_summary.facts.motive"] == "inferred"
    assert framing["truth_attribution"]["why_summary.facts.motive"] != "observed"


def test_source_and_truth_attribution_are_preserved() -> None:
    framing = build_w5_location_framing(_projection())

    assert framing["source_attribution"]["where_summary.facts.scene_location"] == "participant_state_move"
    assert framing["source_attribution"]["where_summary.location_changed"] == "derived_from_where_facts"
    assert framing["truth_attribution"]["where_summary.facts.scene_location"] == "observed"
    assert framing["truth_attribution"]["where_summary.location_changed"] == "observed"


def test_phase_6c6_compat_shim_derives_legacy_area_fields_from_valid_w5() -> None:
    framing = build_w5_location_framing(_projection(current="kitchen", previous="salon", changed=True))
    compat = w5_location_framing_to_legacy_area_fields(
        framing,
        legacy_fields={"current_area": "legacy_salon", "to_area": "legacy_hall"},
    )

    assert compat["schema_version"] == LEGACY_AREA_COMPAT_SCHEMA_VERSION
    assert compat["legacy_area_compat_source"] == "w5_location_framing"
    assert compat["current_area"] == "kitchen"
    assert compat["from_area"] == "salon"
    assert compat["to_area"] == "kitchen"
    assert compat["location_changed"] is True
    assert compat["location_framing_authority"] == "w5"
    assert compat["local_context_transition_source"] == "w5_location_framing"
    assert compat["has_how"] is True
    assert compat["has_inferred_why"] is True


def test_phase_6c6_compat_shim_preserves_legacy_fields_when_w5_missing() -> None:
    compat = w5_location_framing_to_legacy_area_fields(
        None,
        legacy_fields={
            "current_area": "salon",
            "from_area": "hallway",
            "to_area": "kitchen",
            "location_changed": True,
        },
    )

    assert compat["legacy_area_compat_source"] == "old_payload_fallback"
    assert compat["legacy_area_compat_reason"] == "old_payload_without_w5_location_framing"
    assert compat["current_area"] == "salon"
    assert compat["from_area"] == "hallway"
    assert compat["to_area"] == "kitchen"
    assert compat["location_framing_authority"] == "legacy_fallback"
    assert compat["local_context_transition_source"] == "legacy"


def test_phase_6c6_compat_shim_preserves_legacy_fields_when_w5_malformed() -> None:
    framing = build_w5_location_framing(
        {"target_consumer": "narrator", "schema_version": "invalid"},
        legacy_fallback={"current_area": "kitchen", "from_area": "salon", "to_area": "kitchen"},
    )
    compat = w5_location_framing_to_legacy_area_fields(
        framing,
        legacy_fields={"current_area": "salon", "from_area": "salon", "to_area": "hallway"},
    )

    assert compat["legacy_area_compat_source"] == "malformed_w5_fallback"
    assert compat["legacy_area_compat_reason"] == "malformed_w5"
    assert compat["current_area"] == "salon"
    assert compat["from_area"] == "salon"
    assert compat["to_area"] == "hallway"
    assert compat["location_framing_authority"] == "legacy_fallback"


def test_phase_6c6_w5_native_transition_operates_without_direct_area_input() -> None:
    framing = build_w5_location_framing(_projection(current="kitchen", previous="salon", changed=True))
    transition = build_local_context_transition(
        player_action_frame={"action_kind": "posture_change"},
        affordance_resolution={"affordance_status": "allowed"},
        scene_affordance_model={"scene_affordances": {"locations": []}},
        current_player_local_context={},
        w5_location_framing=framing,
    )

    assert transition["from_area"] == "salon"
    assert transition["to_area"] == "kitchen"
    assert transition["current_area"] == "kitchen"
    assert transition["legacy_area_compat_source"] == "w5_location_framing"
    assert transition["location_framing_authority"] == "w5"
    assert transition["local_context_transition_source"] == "w5_location_framing"
    assert transition["w5_location_framing"]["legacy_area_compat_source"] == "w5_location_framing"


def test_phase_6c6_ensure_legacy_area_fields_is_non_mutating_rollback_shim() -> None:
    framing = build_w5_location_framing(_projection(current="kitchen", previous="salon", changed=True))
    payload = {"transition_type": "movement", "current_area": "legacy_salon"}
    shimmed = ensure_legacy_area_fields_for_compat(payload, w5_location_framing=framing)

    assert payload == {"transition_type": "movement", "current_area": "legacy_salon"}
    assert shimmed["current_area"] == "kitchen"
    assert shimmed["from_area"] == "salon"
    assert shimmed["to_area"] == "kitchen"
    assert shimmed["legacy_area_compat_source"] == "w5_location_framing"


def test_phase_6c6_removing_direct_area_fields_from_w5_native_fixture_preserves_sensory_output() -> None:
    scene_affordances = {
        "scene_affordances": {
            "locations": [
                {"id": "salon", "entry_sensory_detail": {"en": "The salon air is tense."}},
                {"id": "kitchen", "entry_sensory_detail": {"en": "The kitchen tiles feel cold."}},
            ],
        }
    }
    policy = {
        "runtime_governance_policy": {
            "sensory_context": {
                "enabled": True,
                "min_layers_per_turn": 1,
                "max_layers_per_turn": 3,
                "require_structured_events": True,
            },
        },
    }
    framing = build_w5_location_framing(_projection(current="kitchen", previous="salon", changed=True))
    with_legacy_area_fields = derive_sensory_context(
        scene_plan_record={"selected_scene_function": "establish_pressure"},
        local_context_transition={"current_area": "salon", "to_area": "salon"},
        scene_affordances=scene_affordances,
        module_runtime_policy=policy,
        session_output_language="en",
        w5_location_framing=framing,
    )
    without_legacy_area_fields = derive_sensory_context(
        scene_plan_record={"selected_scene_function": "establish_pressure"},
        local_context_transition={},
        scene_affordances=scene_affordances,
        module_runtime_policy=policy,
        session_output_language="en",
        w5_location_framing=framing,
    )

    assert without_legacy_area_fields["target"]["location_id"] == "kitchen"
    assert without_legacy_area_fields["target"]["location_id"] == with_legacy_area_fields["target"]["location_id"]
    assert without_legacy_area_fields["target"]["selected_layers"] == with_legacy_area_fields["target"]["selected_layers"]
    assert without_legacy_area_fields["w5_location_framing_diagnostics"]["legacy_area_compat_source"] == "w5_location_framing"


def test_phase_6c4_no_raw_w5_history_emitted_in_authority_diagnostics() -> None:
    payload = _projection(current="kitchen", previous="salon", changed=True).to_dict()
    payload["w5_history"] = [{"private_npc_fact": "do not leak"}]
    framing = build_w5_location_framing(payload)
    transition = location_framing_to_local_context_transition(framing)
    plan = build_narrator_consequence_plan(
        lang="en",
        player_action_frame={"resolved_target": {"target_id": "kitchen"}},
        affordance_resolution={"affordance_status": "allowed"},
        scene_affordance_model={"scene_affordances": {"locations": []}},
        local_context_transition=transition,
        w5_location_framing=framing,
    )
    sensory = derive_sensory_context(
        scene_plan_record={"selected_scene_function": "establish_pressure"},
        local_context_transition=transition,
        scene_affordances={"scene_affordances": {"locations": [{"id": "kitchen"}]}},
        module_runtime_policy={
            "runtime_governance_policy": {
                "sensory_context": {
                    "enabled": True,
                    "min_layers_per_turn": 1,
                    "max_layers_per_turn": 1,
                    "require_structured_events": True,
                },
            },
        },
        session_output_language="en",
        w5_location_framing=framing,
    )

    assert transition["location_framing_authority"] == "w5"
    assert plan["w5_location_framing"]["location_framing_authority"] == "w5"
    assert sensory["w5_location_framing_diagnostics"]["location_framing_authority"] == "w5"
    for emitted in (
        framing,
        transition["w5_location_framing"],
        plan["w5_location_framing"],
        sensory["w5_location_framing_diagnostics"],
        w5_location_framing_to_legacy_area_fields(framing),
    ):
        assert "w5_history" not in emitted
        assert "private_npc_fact" not in str(emitted)


def test_narrator_consequence_plan_records_w5_first_location_framing() -> None:
    framing = build_w5_location_framing(_projection(current="kitchen", previous="salon", changed=True))
    plan = build_narrator_consequence_plan(
        lang="en",
        player_action_frame={"resolved_target": {"target_id": "kitchen"}},
        affordance_resolution={"affordance_status": "allowed"},
        scene_affordance_model={"scene_affordances": {"locations": []}},
        local_context_transition=location_framing_to_local_context_transition(framing),
        w5_location_framing=framing,
    )

    assert plan["w5_location_framing"]["w5_location_framing_used"] is True
    assert plan["w5_location_framing"]["w5_location_framing_source"] == "w5_projection"
    assert plan["w5_location_framing"]["w5_current_location"] == "kitchen"
    assert plan["w5_location_framing"]["w5_previous_location"] == "salon"
    assert plan["w5_location_framing"]["location_framing_authority"] == "w5"
    assert plan["w5_location_framing"]["local_context_transition_source"] == "w5_location_framing"


def test_narrator_consequence_semantic_parity_when_w5_and_legacy_agree() -> None:
    scene_model = {
        "scene_affordances": {
            "current_area": "salon",
            "locations": [
                {
                    "id": "kitchen",
                    "entry_sensory_detail": {"en": "The kitchen tiles feel cold."},
                    "available_affordances": ["look_at"],
                }
            ],
        }
    }
    frame = {
        "action_kind": "movement",
        "resolved_target": {"target_id": "kitchen", "matched_alias": "kitchen"},
    }
    aff = {"affordance_status": "allowed"}
    legacy_transition = build_local_context_transition(
        player_action_frame=frame,
        affordance_resolution=aff,
        scene_affordance_model=scene_model,
        current_player_local_context={"current_area": "salon"},
    )
    framing = build_w5_location_framing(_projection(current="salon", previous=None, changed=False))
    w5_transition = build_local_context_transition(
        player_action_frame=frame,
        affordance_resolution=aff,
        scene_affordance_model=scene_model,
        current_player_local_context={"current_area": "salon"},
        w5_location_framing=framing,
    )

    for key in (
        "from_area",
        "from_location_id",
        "to_area",
        "to_location_id",
        "transition_type",
        "new_area_established",
        "location_found",
    ):
        assert w5_transition[key] == legacy_transition[key]

    legacy_plan = build_narrator_consequence_plan(
        lang="en",
        player_action_frame=frame,
        affordance_resolution=aff,
        scene_affordance_model=scene_model,
        local_context_transition=legacy_transition,
    )
    w5_plan = build_narrator_consequence_plan(
        lang="en",
        player_action_frame=frame,
        affordance_resolution=aff,
        scene_affordance_model=scene_model,
        local_context_transition=w5_transition,
        w5_location_framing=framing,
    )
    for key in (
        "consequence_text",
        "consequence_type",
        "source",
        "requires_model_realization",
        "local_context_updated",
        "affordances_available",
        "transition_type",
    ):
        assert w5_plan[key] == legacy_plan[key]


def test_location_changed_false_does_not_force_scene_shift_framing() -> None:
    framing = build_w5_location_framing(_projection(current="salon", previous="salon", changed=False))
    transition = location_framing_to_local_context_transition(
        framing,
        legacy_transition={"from_area": "salon", "to_area": "salon", "transition_type": "posture_change"},
    )

    assert transition["scene_changed"] is False
    assert transition["location_changed"] is False
    assert transition["transition_type"] == "posture_change"
    assert transition["location_framing_authority"] == "w5"


def test_hard_cut_scene_shift_framing_is_available_from_w5_where_summary() -> None:
    framing = build_w5_location_framing(_projection(current="kitchen", previous="salon", changed=True))
    transition = location_framing_to_local_context_transition(framing)

    assert framing["location_changed"] is True
    assert transition["scene_changed"] is True
    assert transition["from_area"] == "salon"
    assert transition["to_area"] == "kitchen"


def test_sensory_context_prefers_w5_first_location_framing() -> None:
    framing = build_w5_location_framing(_projection(current="kitchen", previous="salon", changed=True))
    result = derive_sensory_context(
        scene_plan_record={"selected_scene_function": "establish_pressure"},
        local_context_transition={"to_area": "salon"},
        scene_affordances={
            "scene_affordances": {
                "locations": [
                    {"id": "salon", "entry_sensory_detail": {"en": "The salon air is tense."}},
                    {"id": "kitchen", "entry_sensory_detail": {"en": "The kitchen tiles feel cold."}},
                ],
            }
        },
        narrator_sensory_palette={"rooms": {"kitchen": {"ambient": "A refrigerator hums."}}},
        module_runtime_policy={
            "runtime_governance_policy": {
                "sensory_context": {
                    "enabled": True,
                    "min_layers_per_turn": 1,
                    "max_layers_per_turn": 3,
                    "require_structured_events": True,
                },
            },
        },
        session_output_language="en",
        w5_location_framing=framing,
    )

    assert result["target"]["location_id"] == "kitchen"
    layer_ids = {layer["layer_id"] for layer in result["target"]["selected_layers"]}
    assert "room:kitchen:ambient" in layer_ids
    assert result["w5_location_framing_diagnostics"]["w5_location_framing_used"] is True
    assert result["w5_location_framing_diagnostics"]["w5_current_location"] == "kitchen"
    assert result["w5_location_framing_diagnostics"]["location_framing_authority"] == "w5"
    assert (
        result["w5_location_framing_diagnostics"]["local_context_transition_source"]
        == "w5_location_framing"
    )


def test_sensory_context_same_location_parity_with_legacy_resolution() -> None:
    scene_affordances = {
        "scene_affordances": {
            "locations": [
                {"id": "salon", "entry_sensory_detail": {"en": "The salon air is tense."}},
            ],
        }
    }
    policy = {
        "runtime_governance_policy": {
            "sensory_context": {
                "enabled": True,
                "min_layers_per_turn": 1,
                "max_layers_per_turn": 3,
                "require_structured_events": True,
            },
        },
    }
    legacy = derive_sensory_context(
        scene_plan_record={"selected_scene_function": "establish_pressure"},
        local_context_transition={"current_area": "salon"},
        scene_affordances=scene_affordances,
        module_runtime_policy=policy,
        session_output_language="en",
    )
    framing = build_w5_location_framing(_projection(current="salon", previous="salon", changed=False))
    with_w5 = derive_sensory_context(
        scene_plan_record={"selected_scene_function": "establish_pressure"},
        local_context_transition={"current_area": "salon"},
        scene_affordances=scene_affordances,
        module_runtime_policy=policy,
        session_output_language="en",
        w5_location_framing=framing,
    )

    assert with_w5["target"]["location_id"] == legacy["target"]["location_id"] == "salon"
    assert with_w5["state"]["location_id"] == legacy["state"]["location_id"] == "salon"


def test_sensory_context_malformed_w5_uses_legacy_location_fallback() -> None:
    framing = build_w5_location_framing(
        {"target_consumer": "narrator", "schema_version": "invalid"},
        legacy_fallback={"current_area": "kitchen"},
    )
    result = derive_sensory_context(
        scene_plan_record={"selected_scene_function": "establish_pressure"},
        local_context_transition={"current_area": "salon"},
        scene_affordances={
            "scene_affordances": {
                "locations": [
                    {"id": "salon", "entry_sensory_detail": {"en": "The salon air is tense."}},
                    {"id": "kitchen", "entry_sensory_detail": {"en": "The kitchen tiles feel cold."}},
                ],
            }
        },
        module_runtime_policy={
            "runtime_governance_policy": {
                "sensory_context": {
                    "enabled": True,
                    "min_layers_per_turn": 1,
                    "max_layers_per_turn": 3,
                    "require_structured_events": True,
                },
            },
        },
        session_output_language="en",
        w5_location_framing=framing,
    )

    assert result["target"]["location_id"] == "salon"
    diagnostics = result["w5_location_framing_diagnostics"]
    assert diagnostics["w5_location_framing_failed"] is True
    assert diagnostics["location_framing_authority"] == "legacy_fallback"
    assert diagnostics["local_context_transition_source"] == "legacy"


def test_sensory_context_w5_framing_without_how_or_why_does_not_crash() -> None:
    framing = build_w5_location_framing(_projection(current="salon", previous=None, changed=False, how=False, inferred_why=False))
    result = derive_sensory_context(
        scene_plan_record={"selected_scene_function": "establish_pressure"},
        local_context_transition={"current_area": "kitchen"},
        scene_affordances={
            "scene_affordances": {
                "locations": [
                    {"id": "salon", "entry_sensory_detail": {"en": "The salon air is tense."}},
                    {"id": "kitchen", "entry_sensory_detail": {"en": "The kitchen tiles feel cold."}},
                ],
            }
        },
        module_runtime_policy={
            "runtime_governance_policy": {
                "sensory_context": {
                    "enabled": True,
                    "min_layers_per_turn": 1,
                    "max_layers_per_turn": 3,
                    "require_structured_events": True,
                },
            },
        },
        session_output_language="en",
        w5_location_framing=framing,
    )

    assert result["target"]["location_id"] == "salon"
    assert framing["has_how"] is False
    assert framing["has_inferred_why"] is False
    assert result["w5_location_framing_diagnostics"]["location_framing_authority"] == "w5"


def test_graph_runtime_synthesizes_w5_location_framing_in_action_resolution_commit() -> None:
    from ai_stack.langgraph.langgraph_runtime import RuntimeTurnGraphExecutor

    graph = object.__new__(RuntimeTurnGraphExecutor)
    update = graph._resolve_player_action(
        {
            "module_id": "god_of_carnage",
            "player_input": "Go to the kitchen",
            "interpreted_input": {
                "normalized_english_text": "Go to the kitchen.",
                "player_input_kind": "physical_action",
                "action_kind": "go_to",
                "verb": "go_to",
                "resolved_target_id": "kitchen",
                "resolved_target_type": "location",
                "target_query_english": "kitchen",
                "commit_policy": "commit_action",
            },
            "turn_number": TURN,
            "current_scene_id": "salon",
            "player_local_context": {"current_area": "salon", "current_location_id": "salon"},
            "environment_state": {
                "current_room_id": "salon",
                "actor_locations": {"annette_reille": "salon"},
            },
            "actor_lane_context": {
                "human_actor_id": "annette_reille",
                "selected_player_role": "annette_reille",
                "npc_actor_ids": [],
                "actor_lanes": {"annette_reille": "human"},
            },
            "w5_latest_snapshot": _snapshot("salon", turn=TURN - 1).to_dict(),
        }
    )

    framing = update["w5_location_framing"]
    diagnostics = update["graph_diagnostics"]["w5_location_framing"]
    transition = update["local_context_transition"]
    consequence = update["narrator_consequence_plan"]

    assert framing["schema_version"] == W5_LOCATION_FRAMING_SCHEMA_VERSION
    assert framing["source"] == "w5_projection"
    assert framing["current_location"] == "salon"
    assert diagnostics["w5_location_framing_used"] is True
    assert diagnostics["w5_location_framing_failed"] is False
    assert diagnostics["w5_current_location"] == "salon"
    assert diagnostics["location_framing_authority"] == "w5"
    assert diagnostics["local_context_transition_source"] == "w5_location_framing"
    assert diagnostics["legacy_area_compat_source"] == "w5_location_framing"
    assert transition["w5_location_framing"]["w5_location_framing_source"] == "w5_projection"
    assert consequence["w5_location_framing"]["w5_location_framing_source"] == "w5_projection"
    assert "committed_result" not in update


def test_graph_runtime_missing_w5_keeps_legacy_location_fallback() -> None:
    from ai_stack.langgraph.langgraph_runtime import RuntimeTurnGraphExecutor

    graph = object.__new__(RuntimeTurnGraphExecutor)
    update = graph._resolve_player_action(
        {
            "module_id": "god_of_carnage",
            "player_input": "Look around",
            "interpreted_input": {
                "normalized_english_text": "Look around.",
                "player_input_kind": "perception",
                "action_kind": "look",
                "verb": "look",
                "commit_policy": "no_commit",
            },
            "turn_number": TURN,
            "current_scene_id": "salon",
            "player_local_context": {"current_area": "salon", "current_location_id": "salon"},
            "environment_state": {"current_room_id": "salon"},
            "actor_lane_context": {
                "human_actor_id": "annette_reille",
                "selected_player_role": "annette_reille",
                "npc_actor_ids": [],
                "actor_lanes": {"annette_reille": "human"},
            },
        }
    )

    framing = update["w5_location_framing"]
    diagnostics = update["graph_diagnostics"]["w5_location_framing"]

    assert framing["source"] == "legacy_fallback"
    assert framing["fallback_reason"] == "missing_w5"
    assert framing["current_location"] == "salon"
    assert diagnostics["w5_location_framing_used"] is False
    assert diagnostics["w5_location_framing_failed"] is True
    assert diagnostics["w5_location_framing_fallback_reason"] == "missing_w5"
    assert diagnostics["location_framing_authority"] == "legacy_fallback"
    assert diagnostics["local_context_transition_source"] == "legacy"
    assert diagnostics["legacy_area_compat_source"] == "legacy_fallback"
    assert update["local_context_transition"]["current_area"] == "salon"


def test_graph_sensory_derivation_receives_synthesized_w5_location_framing() -> None:
    text = (
        REPO_ROOT
        / "ai_stack"
        / "langgraph"
        / "runtime_executor"
        / "executor_symbolic_meta_genre_derivation.py"
    ).read_text(encoding="utf-8")

    assert 'w5_location_framing=state.get("w5_location_framing")' in text
    assert 'derive_sensory_context(' in text
