from __future__ import annotations

import copy
from typing import Any

from ai_stack.contracts.expectation_variation_contracts import (
    EXPECTATION_VARIATION_BOUNDED_REVEAL,
    EXPECTATION_VARIATION_SCHEMA_VERSION,
)
from ai_stack.contracts.narrative_momentum_contracts import NARRATIVE_MOMENTUM_SCHEMA_VERSION
from ai_stack.contracts.npc_agency_contracts import NPC_AGENCY_CLAIM_BOUNDED_RUNTIME_STATUS
from ai_stack.contracts.sensory_context_contracts import SENSORY_CONTEXT_SCHEMA_VERSION

RUNTIME_ASPECT_MATRIX_TRACE_PAYLOAD = {
    "id": "trace-aspect-matrix",
    "name": "world-engine.turn.execute",
    "environment": "staging",
    "output": {
        "contract": "story_runtime_path_observability.v1",
        "session_id": "session-aspect",
        "canonical_turn_id": "session-aspect:turn:1",
        "turn_number": 1,
        "raw_player_input": "Ich nehme ein Bier aus dem Kuehlschrank",
        "turn_aspect_ledger": {
            "session_id": "session-aspect",
            "canonical_turn_id": "session-aspect:turn:1",
            "turn_number": 1,
            "turn_aspect_ledger": {
                "input": {
                    "status": "passed",
                    "actual": {
                        "raw_player_input": "Ich nehme ein Bier aus dem Kuehlschrank",
                        "input_kind": "action",
                    },
                },
                "action_resolution": {
                    "status": "passed",
                    "actual": {"action_kind": "object_interaction"},
                },
                "beat": {
                    "status": "partial",
                    "selected": {"selected_beat_id": "domestic_disruption"},
                    "actual": {"realized": False},
                    "failure_reason": "beat_realization_not_visible",
                },
                "narrator_authority": {
                    "status": "passed",
                    "expected": {"required": True},
                    "actual": {"narrator_block_present": True},
                },
                "npc_authority": {
                    "status": "passed",
                    "expected": {"policy": "social_reaction_only"},
                    "actual": {"npc_takeover_detected": False},
                },
                "npc_agency": {
                    "status": "passed",
                    "actual": {
                        "independent_planning_used": True,
                        "candidate_actor_ids": ["npc_primary", "npc_secondary"],
                        "missing_required_actor_ids": [],
                        "carry_forward_actor_ids": [],
                        "multi_npc_initiative_realized": True,
                        "forbidden_planned_actor_ids": [],
                        "forbidden_realized_actor_ids": [],
                        "long_horizon_state_present": True,
                        "intention_threads_active": 3,
                        "private_plan_resolution_present": True,
                        "private_plan_visibility_respected": True,
                        "unrealized_selected_private_plan_actor_ids": [],
                    },
                },
                "capability_selection": {
                    "status": "passed",
                    "selected": {"selected_capabilities": ["player.object_interaction.request"]},
                    "actual": {
                        "realized_capabilities": ["player.object_interaction.request"],
                        "forbidden_capability_realized": False,
                    },
                },
                "visible_projection": {
                    "status": "passed",
                    "actual": {"visible_block_origin_present": True},
                },
                "information_disclosure": {
                    "status": "passed",
                    "expected": {
                        "policy_present": True,
                        "policy_enabled": True,
                        "max_visible_units_per_turn": 1,
                        "commit_impact": "recover",
                    },
                    "selected": {
                        "selected_unit_ids": ["unit_alpha"],
                        "allowed_unit_ids": ["unit_alpha"],
                        "withheld_unit_ids": ["unit_beta"],
                        "forbidden_unit_ids": ["unit_beta"],
                    },
                    "actual": {
                        "contract_pass": True,
                        "visible_unit_ids": ["unit_alpha"],
                        "budget_used": 1,
                        "failure_codes": [],
                    },
                },
                "expectation_variation": {
                    "status": "passed",
                    "expected": {
                        "schema_version": EXPECTATION_VARIATION_SCHEMA_VERSION,
                        "policy_present": True,
                        "policy_enabled": True,
                        "commit_impact": "recover",
                        "require_structured_events": True,
                        "max_variation_units_per_turn": 1,
                    },
                    "selected": {
                        "selected_variation_ids": ["variation_alpha"],
                        "selected_variation_types": [EXPECTATION_VARIATION_BOUNDED_REVEAL],
                        "required_setup_refs": [
                            {
                                "source": "information_disclosure_target",
                                "field": "selected_unit_ids",
                                "value": "unit_alpha",
                            }
                        ],
                    },
                    "actual": {
                        "contract_pass": True,
                        "structured_events_present": True,
                        "event_count": 1,
                        "budget_used": 1,
                        "realized_variation_ids": ["variation_alpha"],
                        "realized_variation_types": [EXPECTATION_VARIATION_BOUNDED_REVEAL],
                        "failure_codes": [],
                    },
                },
                "narrative_momentum": {
                    "status": "passed",
                    "expected": {
                        "schema_version": NARRATIVE_MOMENTUM_SCHEMA_VERSION,
                        "policy_present": True,
                        "policy_enabled": True,
                        "commit_impact": "recover",
                        "require_structured_events": True,
                    },
                    "selected": {
                        "target_state": "building",
                        "target_score": 0.62,
                        "allowed_next_states": ["building", "driving"],
                        "requires_forward_motion": True,
                        "release_allowed": False,
                        "min_progress_event_count": 1,
                        "selected_driver_refs": [
                            {
                                "source": "scene_energy_transition",
                                "field": "target_transition",
                                "value": "rise",
                            }
                        ],
                    },
                    "actual": {
                        "contract_pass": True,
                        "current_state": "building",
                        "current_score": 0.62,
                        "trend": "rising",
                        "velocity": 0.2,
                        "transition_allowed": True,
                        "structured_events_present": True,
                        "event_count": 1,
                        "progress_event_count": 1,
                        "stall_turn_count": 0,
                        "stall_budget_respected": True,
                        "source_refs_valid": True,
                        "failure_codes": [],
                    },
                },
                "pacing_rhythm": {
                    "status": "passed",
                    "expected": {
                        "schema_version": "pacing_rhythm.v1",
                        "policy_present": True,
                        "policy_enabled": True,
                    },
                    "selected": {
                        "target": {
                            "schema_version": "pacing_rhythm.v1",
                            "cadence": "press",
                            "tempo_arc": "accelerating",
                            "response_shape": "exchange",
                            "turn_change_policy": "prefer_actor_turn_change",
                            "min_visible_blocks": 1,
                            "max_visible_blocks": 5,
                            "requires_pause": False,
                            "blocks_forced_speech": False,
                        }
                    },
                    "actual": {
                        "contract_pass": True,
                        "visible_block_count": 2,
                        "actor_turn_count": 1,
                        "failure_codes": [],
                    },
                },
                "sensory_context": {
                    "status": "passed",
                    "expected": {
                        "schema_version": SENSORY_CONTEXT_SCHEMA_VERSION,
                        "policy_present": True,
                        "policy_enabled": True,
                    },
                    "selected": {
                        "target": {
                            "schema_version": SENSORY_CONTEXT_SCHEMA_VERSION,
                            "intensity": "high",
                            "location_id": "room_alpha",
                            "object_id": "object_alpha",
                            "mood_key": "mid_tension",
                            "selected_layers": [
                                {
                                    "layer_id": "room:room_alpha:ambient",
                                    "source_ref": "narrator_sensory_palette.rooms.room_alpha.ambient",
                                }
                            ],
                            "required_layer_ids": ["room:room_alpha:ambient"],
                            "min_layers_per_turn": 1,
                            "max_layers_per_turn": 3,
                        }
                    },
                    "actual": {
                        "contract_pass": True,
                        "event_count": 1,
                        "realized_layer_ids": ["room:room_alpha:ambient"],
                        "required_layer_ids": ["room:room_alpha:ambient"],
                        "selected_layer_ids": ["room:room_alpha:ambient"],
                        "failure_codes": [],
                    },
                },
                "improvisational_coherence": {
                    "status": "passed",
                    "expected": {
                        "schema_version": "improvisational_coherence.v1",
                        "policy_present": True,
                        "policy_enabled": True,
                        "commit_impact": "recover",
                        "require_structured_events": True,
                        "min_anchor_refs": 1,
                    },
                    "selected": {
                        "contribution_id": "turn_contribution:alpha",
                        "contribution_kind": "object_interaction",
                        "acceptance_mode": "accept",
                        "min_anchor_refs": 1,
                        "selected_scene_function": "domestic_disruption",
                        "required_anchor_refs": [
                            {
                                "source": "scene_plan_record",
                                "field": "selected_scene_function",
                                "value": "domestic_disruption",
                            }
                        ],
                        "requires_playable_boundary_reason": False,
                        "boundary_reason_code": None,
                    },
                    "actual": {
                        "contribution_acknowledged": True,
                        "acceptance_mode": "accept",
                        "advance_class": "pressure_raise",
                        "anchor_refs": [
                            {
                                "source": "scene_plan_record",
                                "field": "selected_scene_function",
                                "value": "domestic_disruption",
                            }
                        ],
                        "boundary_reason_code": None,
                        "contract_pass": True,
                        "failure_codes": [],
                    },
                },
                "social_pressure": {
                    "status": "passed",
                    "expected": {
                        "schema_version": "social_pressure.v1",
                        "policy_present": True,
                        "policy_enabled": True,
                    },
                    "selected": {
                        "target": {
                            "schema_version": "social_pressure.v1",
                            "target_score": 0.74,
                            "target_band": "high",
                            "trend": "rising",
                            "pressure_floor": 0.67,
                            "requires_visible_pressure": True,
                            "release_allowed": False,
                        }
                    },
                    "actual": {
                        "contract_pass": True,
                        "current_score": 0.74,
                        "current_band": "high",
                        "trend": "rising",
                        "velocity": 0.22,
                        "failure_codes": [],
                    },
                },
                "dramatic_irony": {
                    "status": "passed",
                    "expected": {
                        "policy_present": True,
                        "policy_enabled": True,
                        "allowed_surface_modes": ["misread_reaction"],
                        "direct_reveal_allowed": False,
                    },
                    "selected": {
                        "selected_opportunity_ids": ["opportunity_alpha"],
                        "selected_fact_ids": ["fact_alpha"],
                    },
                    "actual": {
                        "status": "selected",
                        "fact_count": 1,
                        "opportunity_count": 1,
                        "selected_opportunity_count": 1,
                        "realization_status": "realized",
                        "realized_opportunity_ids": ["opportunity_alpha"],
                        "visible_anchor_refs": ["opportunity_alpha"],
                        "leak_blocked": False,
                        "violation_codes": [],
                        "contract_pass": True,
                        "surface_mode_contract_pass": True,
                        "hidden_fact_echo_absent": True,
                    },
                },
                "narrative_aspect": {
                    "status": "passed",
                    "expected": {
                        "policy_present": True,
                        "candidate_aspects": ["aspect_alpha"],
                        "theme_tracking_policy_present": True,
                        "semantic_tracking_enabled": True,
                        "semantic_profile_aspects": ["aspect_alpha"],
                    },
                    "selected": {
                        "selected_aspects": ["aspect_alpha"],
                        "selected_theme_aspects": ["aspect_alpha"],
                    },
                    "actual": {
                        "realized_aspects": ["aspect_alpha"],
                        "realized_theme_aspects": ["aspect_alpha"],
                        "visible_when_required": True,
                        "semantic_classification_count": 1,
                        "semantic_weak_alignment_count": 0,
                        "semantic_classifications": [
                            {
                                "aspect_id": "aspect_alpha",
                                "status": "passed",
                                "table_b_refs": ["pi_12"],
                            }
                        ],
                    },
                },
                "voice_consistency": {
                    "status": "passed",
                    "expected": {
                        "policy_present": True,
                        "semantic_classification_enabled": True,
                    },
                    "actual": {
                        "spoken_line_count": 1,
                        "finding_count": 0,
                        "blocking_finding_count": 0,
                        "drift_class_counts": {},
                        "semantic_classification_count": 1,
                        "semantic_cross_actor_confusion_count": 0,
                    },
                },
                "hierarchical_memory": {
                    "status": "passed",
                    "expected": {"policy_present": True, "policy_enabled": True},
                    "selected": {
                        "selected_tiers": ["turn", "session"],
                        "source_canonical_turn_id": "session-aspect:turn:1",
                    },
                    "actual": {
                        "write_allowed": True,
                        "written_item_count": 2,
                        "memory_present": True,
                        "context_item_count": 2,
                        "context_bounded": True,
                        "uncommitted_write_detected": False,
                    },
                },
            },
        },
    },
    "scores": [
        {"name": "beat_realized", "value": 0.0},
        {"name": "npc_independent_planning_used", "value": 1.0},
        {"name": "npc_long_horizon_state_present", "value": 1.0},
        {"name": "npc_private_plan_resolution_present", "value": 1.0},
        {"name": "npc_private_plan_visibility_respected", "value": 1.0},
        {"name": "npc_intention_threads_carried_forward", "value": 1.0},
        {"name": "npc_required_initiatives_realized", "value": 1.0},
        {"name": "npc_carry_forward_closed", "value": 1.0},
        {"name": "information_disclosure_policy_present", "value": 1.0},
        {"name": "information_disclosure_target_selected", "value": 1.0},
        {"name": "information_disclosure_budget_pass", "value": 1.0},
        {"name": "information_disclosure_premature_reveal_absent", "value": 1.0},
        {"name": "information_disclosure_contract_pass", "value": 1.0},
        {"name": "expectation_variation_policy_present", "value": 1.0},
        {"name": "expectation_variation_target_selected", "value": 1.0},
        {"name": "expectation_variation_budget_pass", "value": 1.0},
        {"name": "expectation_variation_setup_supported", "value": 1.0},
        {"name": "expectation_variation_contract_pass", "value": 1.0},
        {"name": "narrative_momentum_policy_present", "value": 1.0},
        {"name": "narrative_momentum_target_selected", "value": 1.0},
        {"name": "narrative_momentum_transition_allowed", "value": 1.0},
        {"name": "narrative_momentum_progress_event_present", "value": 1.0},
        {"name": "narrative_momentum_stall_budget_respected", "value": 1.0},
        {"name": "narrative_momentum_contract_pass", "value": 1.0},
        {"name": "pacing_rhythm_target_present", "value": 1.0},
        {"name": "pacing_rhythm_contract_pass", "value": 1.0},
        {"name": "pacing_rhythm_density_respected", "value": 1.0},
        {"name": "pacing_rhythm_pause_respected", "value": 1.0},
        {"name": "sensory_context_target_present", "value": 1.0},
        {"name": "sensory_context_contract_pass", "value": 1.0},
        {"name": "sensory_context_required_layers_realized", "value": 1.0},
        {"name": "sensory_context_source_refs_valid", "value": 1.0},
        {"name": "improvisational_coherence_policy_present", "value": 1.0},
        {"name": "improvisational_coherence_target_selected", "value": 1.0},
        {"name": "improvisational_coherence_acknowledged", "value": 1.0},
        {"name": "improvisational_coherence_scene_anchor_preserved", "value": 1.0},
        {"name": "improvisational_coherence_contract_pass", "value": 1.0},
        {"name": "social_pressure_target_present", "value": 1.0},
        {"name": "social_pressure_contract_pass", "value": 1.0},
        {"name": "social_pressure_metric_bounded", "value": 1.0},
        {"name": "dramatic_irony_policy_present", "value": 1.0},
        {"name": "dramatic_irony_opportunity_present", "value": 1.0},
        {"name": "dramatic_irony_contract_pass", "value": 1.0},
        {"name": "narrative_aspect_contract_pass", "value": 1.0},
        {"name": "theme_tracking_policy_present", "value": 1.0},
        {"name": "theme_tracking_selected", "value": 1.0},
        {"name": "theme_semantic_classification_present", "value": 1.0},
        {"name": "theme_weak_alignment_absent", "value": 1.0},
        {"name": "theme_tracking_contract_pass", "value": 1.0},
        {"name": "voice_semantic_classification_present", "value": 1.0},
        {"name": "voice_cross_actor_confusion_absent", "value": 1.0},
        {"name": "voice_forbidden_markers_absent", "value": 1.0},
        {"name": "voice_consistency_contract_pass", "value": 1.0},
        {"name": "hierarchical_memory_contract_pass", "value": 1.0},
        {"name": "memory_write_from_committed_turn", "value": 1.0},
    ],
}



def runtime_aspect_matrix_trace_payload() -> dict[str, Any]:
    return copy.deepcopy(RUNTIME_ASPECT_MATRIX_TRACE_PAYLOAD)


def assert_runtime_aspect_matrix_row(row: dict[str, Any]) -> None:
    _assert_runtime_identity_and_npc_agency(row)
    _assert_disclosure_variation_and_momentum(row)
    _assert_runtime_texture_aspects(row)
    _assert_irony_theme_voice_and_memory(row)
    assert row["main_failure"] == "beat_realization_not_visible"


def _assert_runtime_identity_and_npc_agency(row: dict[str, Any]) -> None:
    assert row["session_id"] == "session-aspect"
    assert row["canonical_turn_id"] == "session-aspect:turn:1"
    assert row["environment"] == "staging"
    assert row["turn_aspect_ledger_present"] is True
    assert row["raw_input"].startswith("Ich nehme")
    assert row["action_kind"] == "object_interaction"
    assert row["selected_beat"] == "domestic_disruption"
    assert row["beat_realized"] is False
    assert row["npc_independent_planning_used"] is True
    assert row["npc_long_horizon_state_present"] is True
    assert row["npc_private_plan_resolution_present"] is True
    assert row["npc_private_plan_visibility_respected"] is True
    assert row["npc_intention_threads_carried_forward"] is True
    assert row["npc_required_initiatives_realized"] is True
    assert row["npc_carry_forward_closed"] is True
    assert row["npc_agency_candidate_actor_ids"] == ["npc_primary", "npc_secondary"]
    assert row["npc_agency_claim_readiness_status"] == NPC_AGENCY_CLAIM_BOUNDED_RUNTIME_STATUS
    assert row["npc_agency_full_claim_allowed"] is False


def _assert_disclosure_variation_and_momentum(row: dict[str, Any]) -> None:
    assert row["information_disclosure_policy_present"] is True
    assert row["information_disclosure_selected_units"] == ["unit_alpha"]
    assert row["information_disclosure_visible_units"] == ["unit_alpha"]
    assert row["information_disclosure_withheld_units"] == ["unit_beta"]
    assert row["information_disclosure_budget_pass"] is True
    assert row["information_disclosure_contract_pass"] == 1.0
    assert row["expectation_variation_policy_present"] is True
    assert row["expectation_variation_target_selected"] is True
    assert row["expectation_variation_selected_ids"] == ["variation_alpha"]
    assert row["expectation_variation_selected_types"] == [EXPECTATION_VARIATION_BOUNDED_REVEAL]
    assert row["expectation_variation_realized_ids"] == ["variation_alpha"]
    assert row["expectation_variation_realized_types"] == [EXPECTATION_VARIATION_BOUNDED_REVEAL]
    assert row["expectation_variation_budget_used"] == 1
    assert row["expectation_variation_budget_pass"] is True
    assert row["expectation_variation_setup_supported"] is True
    assert row["expectation_variation_contract_pass"] is True
    assert row["expectation_variation_failure_codes"] == []
    assert row["narrative_momentum_policy_present"] is True
    assert row["narrative_momentum_target_selected"] is True
    assert row["narrative_momentum_current_state"] == "building"
    assert row["narrative_momentum_current_score"] == 0.62
    assert row["narrative_momentum_target_state"] == "building"
    assert row["narrative_momentum_target_score"] == 0.62
    assert row["narrative_momentum_trend"] == "rising"
    assert row["narrative_momentum_velocity"] == 0.2
    assert row["narrative_momentum_transition_allowed"] is True
    assert row["narrative_momentum_progress_event_present"] is True
    assert row["narrative_momentum_stall_budget_respected"] is True
    assert row["narrative_momentum_contract_pass"] is True
    assert row["narrative_momentum_failure_codes"] == []


def _assert_runtime_texture_aspects(row: dict[str, Any]) -> None:
    assert row["pacing_rhythm_target_present"] is True
    assert row["pacing_rhythm_cadence"] == "press"
    assert row["pacing_rhythm_response_shape"] == "exchange"
    assert row["pacing_rhythm_density_respected"] is True
    assert row["pacing_rhythm_contract_pass"] is True
    assert row["sensory_context_target_present"] is True
    assert row["sensory_context_intensity"] == "high"
    assert row["sensory_context_location_id"] == "room_alpha"
    assert row["sensory_context_object_id"] == "object_alpha"
    assert row["sensory_context_required_layers_realized"] is True
    assert row["sensory_context_source_refs_valid"] is True
    assert row["sensory_context_contract_pass"] is True
    assert row["sensory_context_failure_codes"] == []
    assert row["improvisational_coherence_policy_present"] is True
    assert row["improvisational_coherence_target_selected"] is True
    assert row["improvisational_coherence_contribution_id"] == "turn_contribution:alpha"
    assert row["improvisational_coherence_contribution_kind"] == "object_interaction"
    assert row["improvisational_coherence_acceptance_mode"] == "accept"
    assert row["improvisational_coherence_advance_class"] == "pressure_raise"
    assert row["improvisational_coherence_acknowledged"] is True
    assert row["improvisational_coherence_scene_anchor_preserved"] is True
    assert row["improvisational_coherence_contract_pass"] is True
    assert row["improvisational_coherence_failure_codes"] == []
    assert row["social_pressure_target_present"] is True
    assert row["social_pressure_score"] == 0.74
    assert row["social_pressure_band"] == "high"
    assert row["social_pressure_trend"] == "rising"
    assert row["social_pressure_metric_bounded"] is True
    assert row["social_pressure_contract_pass"] is True


def _assert_irony_theme_voice_and_memory(row: dict[str, Any]) -> None:
    assert row["dramatic_irony_policy_present"] is True
    assert row["dramatic_irony_opportunity_present"] is True
    assert row["dramatic_irony_selected_opportunities"] == ["opportunity_alpha"]
    assert row["dramatic_irony_realized_opportunities"] == ["opportunity_alpha"]
    assert row["dramatic_irony_realization_status"] == "realized"
    assert row["dramatic_irony_leak_blocked"] is False
    assert row["dramatic_irony_contract_pass"] is True
    assert row["dramatic_irony_violation_codes"] == []
    assert row["narrative_aspect_policy_present"] is True
    assert row["selected_narrative_aspects"] == ["aspect_alpha"]
    assert row["realized_narrative_aspects"] == ["aspect_alpha"]
    assert row["narrative_aspect_contract_pass"] == 1.0
    assert row["theme_tracking_policy_present"] is True
    assert row["selected_theme_aspects"] == ["aspect_alpha"]
    assert row["realized_theme_aspects"] == ["aspect_alpha"]
    assert row["theme_semantic_classification_present"] == 1.0
    assert row["theme_semantic_classification_count"] == 1
    assert row["theme_weak_alignment_count"] == 0
    assert row["theme_tracking_contract_pass"] == 1.0
    assert row["voice_consistency_policy_present"] is True
    assert row["voice_semantic_classification_enabled"] is True
    assert row["voice_semantic_classification_count"] == 1
    assert row["voice_cross_actor_confusion_absent"] is True
    assert row["voice_consistency_contract_pass"] == 1.0
    assert row["hierarchical_memory_present"] is True
    assert row["selected_memory_tiers"] == ["turn", "session"]
    assert row["memory_written_item_count"] == 2
    assert row["memory_context_bounded"] is True
    assert row["hierarchical_memory_contract_pass"] == 1.0



__all__ = [
    "assert_runtime_aspect_matrix_row",
    "runtime_aspect_matrix_trace_payload",
]
