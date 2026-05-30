"""W5 Phase 6A — non-failing inventory reporter for legacy localization consumers.

Scans the working tree for the legacy localization / current-room surfaces
listed in ``docs/MVPs/w5_legacy_consumer_removal_inventory.md`` and prints a
summary by surface. **Always exits 0** — this is a planning aid, not a gate.

Usage:

    python scripts/inventory_w5_legacy_consumers.py
    python scripts/inventory_w5_legacy_consumers.py --json
    python scripts/inventory_w5_legacy_consumers.py --root D:/WorldOfShadows

The script is intentionally minimal: it greps the working tree for known
substrings, deduplicates by ``(path, line_number)``, and groups by surface.
Phase-specific planning helpers may add curated, non-failing readiness or
inventory sections. The inventory doc remains the authoritative classification
artifact.

Excluded directories: ``.git``, ``__pycache__``, ``node_modules``,
``'fy'-suites/delagecy``, ``'fy'-suites/docify``, and every ``audit_*.json``
or ``*.log`` artifact at the repository root.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path


# Each entry: (key, regex pattern). Regexes use word boundaries where useful.
LEGACY_SURFACES: list[tuple[str, str]] = [
    ("current_room", r"\bcurrent_room\b"),
    ("current_room_id", r"\bcurrent_room_id\b"),
    ("current_area", r"\bcurrent_area\b"),
    ("previous_room_id", r"\bprevious_room_id\b"),
    ("actor_locations", r"\bactor_locations\b"),
    ("visible_room_ids", r"\bvisible_room_ids\b"),
    ("visible_occupants", r"\bvisible_occupants\b"),
    ("RuntimeVisibilityPolicy", r"\bRuntimeVisibilityPolicy\b"),
    ("complete_actor_locations_for_gathering", r"complete_actor_locations_for_gathering"),
    ("gathering_scene_id", r"\bgathering_scene_id\b"),
    ("derived_gathering_room_id", r"derived_gathering_room_id"),
    ("transition_from_previous", r"\btransition_from_previous\b"),
    ("location_changed", r"\blocation_changed\b"),
    # Phase 6C-0 — narrator consequence / sensory-engine location framing
    # surfaces. These are planning/inventory signals only; Phase 6C-0 does not
    # migrate runtime behavior.
    ("from_area", r"\bfrom_area\b"),
    ("to_area", r"\bto_area\b"),
    ("scene_changed", r"\bscene_changed\b"),
    ("narrator_consequence", r"\bnarrator_consequence\b"),
    ("sensory_context", r"\bsensory_context\b"),
    ("language_adapter", r"\blanguage_adapter\b"),
    ("movement_framing", r"\bmovement[_ -]framing\b"),
    ("transition_framing", r"\btransition[_ -]framing\b"),
    ("forbidden_ai_stack_actor_situation", r"ai_stack[\\/]actor_situation\b"),
    ("forbidden_ai_stack_w5_actor_situation", r"ai_stack[\\/]w5_actor_situation\b"),
    ("w5_actor_situation_term", r"w5_actor_situation"),
    # Phase 6B-0 rename items. These should now be present (R1/R2) — they are
    # the new names — and the old names (validate_w5_actor_situation,
    # "w5_actor_situation_validation") should only appear in inventory/audit
    # artifacts after the rename lands. The scanner reports both so future
    # audits can confirm the rename did not regress.
    ("validate_w5_actor_situation_old", r"\bvalidate_w5_actor_situation\b"),
    ("validate_w5_actor_tracking_new", r"\bvalidate_w5_actor_tracking\b"),
    ("w5_actor_situation_validation_old", r"\bw5_actor_situation_validation\b"),
    ("w5_actor_tracking_validation_new", r"\bw5_actor_tracking_validation\b"),
    # Phase 6B-6A — diagnostics flag retirement surface.
    # These symbols are slated for removal in Phase 6B-6B (ADR-0066).
    # The scanner reports all occurrences so the retirement audit can verify
    # that every reference is addressed before Phase 6B-6B begins.
    ("narrator_legacy_compat_diag_flag", r"W5_AST_NARRATOR_LEGACY_COMPAT_DIAGNOSTICS_ENABLED"),
    ("narrator_legacy_compat_diag_fn", r"\bw5_ast_narrator_legacy_compat_diagnostics_enabled\b"),
    ("narrator_legacy_compat_diag_key", r"\bnarrator_legacy_compat_diagnostics\b"),
    ("legacy_compat_transition_write", r'_legacy_compat\[.transition_from_previous.\]'),
    ("demoted_to_legacy_compat", r"\bdemoted_to_legacy_compat\b"),
    ("removed_by_6b5e_policy", r"\bremoved_by_6b5e_policy\b"),
    ("legacy_transition_parity", r"\blegacy_transition_parity\b"),
    # Phase 6B-9 — public payload alias migration surfaces (ADR-0069).
    # viewer_room_id is a public WS RuntimeSnapshot compat alias slated for
    # Phase 6B-11 deprecation once Phase 6B-10 wires w5_player_view into WS.
    # w5_player_view is the W5 player-shell projection surface (current authority).
    ("viewer_room_id", r"\bviewer_room_id\b"),
    ("w5_player_view", r"\bw5_player_view\b"),
]


# Phase 6B-2 classification labels per surface. Informational only — the
# authoritative classification lives in the inventory doc's per-branch table.
# This map exists so the human-readable scan output can hint which surfaces
# fire under explicit opt-out (`O`), missing/malformed W5 (`M`), substrate
# reads (`S`), compatibility aliases for legacy clients (`L`), or are pure
# documentation/comment mentions (`D`).
PHASE_6B2_CLASSIFICATION: dict[str, str] = {
    "current_room": "deprecated_public_client_alias_keep/S — compatibility alias on player-shell + WS payloads; also substrate read in runtime_world/environment_state",
    "current_room_id": "deprecated_public_client_alias_keep/S — HTTP/player-shell alias + Participant/runtime_world/environment_state substrate field",
    "current_area": "S/L — substrate field; read by C5/C8 affordance + sensory engines (migrate_to_w5_first_before_removal)",
    "previous_room_id": "S — substrate field on environment_state",
    "actor_locations": "S — substrate field on environment_state; read by W5 extractor + Director baseline completion",
    "visible_room_ids": "S — substrate field on environment_state.visible_room_ids",
    "visible_occupants": "S — RuntimeVisibilityPolicy substrate field",
    "RuntimeVisibilityPolicy": "S — engine-level visibility substrate",
    "complete_actor_locations_for_gathering": "S — Director baseline completion algorithm; called by F1/F4/F5",
    "gathering_scene_id": "S — derived from actor_locations by F5; consumed by ADR-0061 pause predicate",
    "derived_gathering_room_id": "S — Director alias (also produced by F5)",
    "transition_from_previous": "removed_by_adr_0068 (Phase 6B-8) — strict-off rollback path removed; transition_from_previous no longer emitted by narrator source_facts; any remaining hits are doc/test/historical references only",
    "location_changed": "S — W5 where_summary location-shift signal; not a narrator strict-off rollback surface",
    "from_area": "w5_first_migration_candidate — narrator consequence LocalContextTransition legacy movement-framing field",
    "to_area": "w5_first_migration_candidate — narrator consequence LocalContextTransition legacy movement-framing field",
    "scene_changed": "unrelated_domain_use / backend session-history signal unless tied to narrator location framing",
    "narrator_consequence": "w5_first_migration_candidate — C7 consequence movement/location framing needs W5-first replacement",
    "sensory_context": "w5_first_migration_candidate — C8 sensory location selection should consume W5 location framing",
    "language_adapter": "w5_first_migration_candidate / doc_only_update depending on callsite — current_area seed remains a legacy framing source",
    "movement_framing": "doc_only_update / planning term",
    "transition_framing": "doc_only_update / planning term",
    "forbidden_ai_stack_actor_situation": "FORBIDDEN — must be zero outside inventory docs/scripts",
    "forbidden_ai_stack_w5_actor_situation": "FORBIDDEN — must be zero outside inventory docs/scripts",
    "w5_actor_situation_term": "D/historical — only inventory/audit artifacts may mention this term",
    "validate_w5_actor_situation_old": "D/historical — old function name; only inventory/audit artifacts may reference it (R1 in 6B-0)",
    "validate_w5_actor_tracking_new": "current — Phase 6B-0 R1 rename target",
    "w5_actor_situation_validation_old": "D/historical — old failure_class string (R2 in 6B-0)",
    "w5_actor_tracking_validation_new": "current — Phase 6B-0 R2 rename target",
    # Phase 6B-6A diagnostics flag retirement surfaces
    "narrator_legacy_compat_diag_flag": "retired_phase_6b6b — env-var name; historical/docs only after ADR-0066.",
    "narrator_legacy_compat_diag_fn": "retired_phase_6b6b — Python function + public export removed by ADR-0066.",
    "narrator_legacy_compat_diag_key": "retired_phase_6b6b — flag-states/admin metadata key removed by ADR-0066.",
    "legacy_compat_transition_write": "retired_phase_6b6b — _legacy_compat insertion branch removed by ADR-0066.",
    "demoted_to_legacy_compat": "retired_phase_6b6b — former w5.legacy_transition_parity diagnostics value; historical/docs only after ADR-0066.",
    "removed_by_6b5e_policy": "removed_by_adr_0068_admin_metadata — former w5.legacy_transition_parity value; historical/docs/tests only.",
    "legacy_transition_parity": "removed_by_adr_0068_admin_metadata — admin metadata key removed; historical/docs/tests only.",
    # Phase 6B-9 surfaces
    "viewer_room_id": "deprecated_public_client_alias_keep — public WS RuntimeSnapshot compat alias; keep during ADR-0069 Phase 6B-12 compatibility window; needs_dedicated_adr_before_removal",
    "w5_player_view": "public_authority — W5 player-shell projection surface; w5_first_already_migrated in Phase 6B-1",
}


# Phase 6B-4 — Fresh post-migration classification taxonomy after F1/F21/F22/
# F8/F18/F19/F20/F11 were migrated. The labels below describe the *reachability
# class* a surface still falls into under the Phase 6B-3A/B/C migration state:
#
#   - still_needed_explicit_opt_out      — branch fires only under W5_AST_*=0/false/no/off
#   - still_needed_malformed_w5_safety   — branch fires only on missing/malformed W5 snapshot
#   - still_needed_old_payload_compat    — branch fires only on legacy sessions without W5 wire-in
#   - still_needed_public_client_compat  — branch fires because WS/frontend payload contract requires it
#   - substrate_keep_future_adr          — substrate writer/reader; consolidation deferred to a later ADR
#   - w5_first_migrated_keep_temporarily — Phase 6B-3A/B/C migrated this; helper/legacy code retained
#                                          as the malformed-W5 / opt-out / old-payload safety net
#   - newly_dead_candidate_for_6b5       — Phase 6B-4 candidate for targeted Phase 6B-5 removal
#                                          (default-on does not execute the branch AND O/M/L are
#                                          covered by a *different* branch AND removal does not
#                                          touch a public payload contract). Phase 6B-4 finds none.
#   - needs_dedicated_adr_before_removal — branch fires under D but is part of a public payload
#                                          contract that requires a separately-scoped ADR + client
#                                          upgrade before removal (e.g., player-shell current_room_id,
#                                          WS viewer_room_id, narrator_consequence area metadata).
#   - test_only_update                   — test fixture / assertion; updates in lockstep with producer
#   - doc_only_update                    — docstring/comment/prompt-text-only legacy reference
#   - unknown_needs_runtime_trace        — coverage cannot be proven statically; needs a live trace
#
# Every label below is informational only. The authoritative per-branch table
# lives in docs/MVPs/w5_legacy_consumer_removal_inventory.md §"Phase 6B-4".
PHASE_6B4_CLASSIFICATION: dict[str, str] = {
    "current_room": (
        "deprecated_public_client_alias_keep + substrate_keep_future_adr + "
        "needs_dedicated_adr_before_removal — public player-shell + WS "
        "payload alias; frontend/WS clients still read it. Substrate reads "
        "remain in runtime_world/environment_state and require a future ADR"
    ),
    "current_room_id": (
        "deprecated_public_client_alias_keep + substrate_keep_future_adr + "
        "needs_dedicated_adr_before_removal — HTTP/player-shell public alias "
        "AND Participant.current_room_id substrate field. runtime_world.current_room_id "
        "and environment_state.current_room_id are substrate_keep_future_adr"
    ),
    "current_area": (
        "substrate_keep_future_adr — C5 player_action_resolution / C7 "
        "narrator_consequence_contracts / C8 sensory_context_engine reads "
        "still primary; needs_dedicated_adr_before_removal for the W5-first "
        "movement-framing / stage-area builder"
    ),
    "previous_room_id": (
        "substrate_keep_future_adr — environment_state substrate field only"
    ),
    "actor_locations": (
        "substrate_keep_future_adr — environment_state substrate field; "
        "W5 extractor input; F1 / F4 / F5 / F21 / F22 still call it on O/M/L"
    ),
    "visible_room_ids": (
        "substrate_keep_future_adr — environment_state visibility substrate"
    ),
    "visible_occupants": (
        "substrate_keep_future_adr — RuntimeVisibilityPolicy substrate field"
    ),
    "RuntimeVisibilityPolicy": (
        "substrate_keep_future_adr — engine-level visibility substrate"
    ),
    "complete_actor_locations_for_gathering": (
        "substrate_keep_future_adr + w5_first_migrated_keep_temporarily — "
        "Director baseline completion algorithm called by F1 (opt-out + "
        "malformed-W5 branches) and F4 (W5-success branch over W5-derived "
        "actor_locations); single source of truth for NPC fallback voting + "
        "gathering_scene_id derivation"
    ),
    "gathering_scene_id": (
        "substrate_keep_future_adr — derived inside complete_actor_locations_"
        "for_gathering; consumed by ADR-0061 pause predicate"
    ),
    "derived_gathering_room_id": (
        "substrate_keep_future_adr — Director alias produced by F5"
    ),
    "transition_from_previous": (
        "removed_by_adr_0068 (Phase 6B-8) — strict-off rollback path removed; "
        "transition_from_previous is no longer emitted by the narrator path. "
        "Any remaining hits are doc/test-historical or the location_changed "
        "W5 mirror (which is a separate substrate keep). "
        "W5 where_summary.location_changed is the sole location-shift authority."
    ),
    "location_changed": (
        "substrate_keep_future_adr — W5 where_summary location-shift signal; "
        "admin diagnostics read W5 history and do not consult "
        "transition_from_previous"
    ),
    # Phase 6C-0 narrator consequence / sensory-engine location-framing surfaces.
    "from_area": (
        "w5_first_migration_candidate — LocalContextTransition legacy field; "
        "future replacement is W5 narrator projection where_summary previous/"
        "current location framing, with compatibility output staged separately"
    ),
    "to_area": (
        "w5_first_migration_candidate — LocalContextTransition legacy field; "
        "future replacement is W5 narrator projection where_summary current "
        "location / location_changed framing"
    ),
    "scene_changed": (
        "unrelated_domain_use unless tied to language-adapter or narrator "
        "movement framing; backend session-history/presenter uses remain out "
        "of Phase 6C-0 runtime migration"
    ),
    "narrator_consequence": (
        "w5_first_migration_candidate — consequence movement/location framing "
        "currently consumes current_area/from_area/to_area-compatible state"
    ),
    "sensory_context": (
        "w5_first_migration_candidate — sensory_context_engine currently "
        "derives room layers from LocalContextTransition and scene_affordances "
        "before W5 location framing"
    ),
    "language_adapter": (
        "w5_first_migration_candidate — interaction surface seeds current_area "
        "from authored content; future runtime overlay should prefer W5 "
        "location framing while preserving authored fallback"
    ),
    "movement_framing": (
        "doc_only_update / planning term — use for Phase 6C-0 inventory "
        "and ADR prose, not an active runtime symbol"
    ),
    "transition_framing": (
        "doc_only_update / planning term — use for Phase 6C-0 inventory "
        "and ADR prose, not an active runtime symbol"
    ),
    "forbidden_ai_stack_actor_situation": (
        "FORBIDDEN — must be zero outside inventory docs/scripts/tests"
    ),
    "forbidden_ai_stack_w5_actor_situation": (
        "FORBIDDEN — must be zero outside inventory docs/scripts/tests"
    ),
    "w5_actor_situation_term": (
        "doc_only_update / historical — only inventory/audit artifacts may "
        "mention this term"
    ),
    "validate_w5_actor_situation_old": (
        "doc_only_update / historical — old function name; only inventory/"
        "audit artifacts may reference it (R1 done in 6B-0)"
    ),
    "validate_w5_actor_tracking_new": "current — Phase 6B-0 R1 rename target",
    "w5_actor_situation_validation_old": (
        "doc_only_update / historical — old failure_class string (R2 done "
        "in 6B-0)"
    ),
    "w5_actor_tracking_validation_new": "current — Phase 6B-0 R2 rename target",
    # Phase 6B-6B diagnostics flag retirement surfaces — classified for completeness.
    # Authoritative removal record: ADR-0066.
    "narrator_legacy_compat_diag_flag": (
        "retired_phase_6b6b — runtime_flag_resolver removed by ADR-0066."
    ),
    "narrator_legacy_compat_diag_fn": (
        "retired_phase_6b6b — runtime_flag_resolver + public export removed "
        "by ADR-0066."
    ),
    "narrator_legacy_compat_diag_key": (
        "retired_phase_6b6b — diagnostics_metadata key removed from "
        "w5_projection_flag_states() by ADR-0066."
    ),
    "legacy_compat_transition_write": (
        "retired_phase_6b6b — runtime_branch in "
        "god_of_carnage_narrator_path._block() removed by ADR-0066."
    ),
    "demoted_to_legacy_compat": (
        "retired_phase_6b6b — former admin_view parity label value; "
        "historical/docs only after ADR-0066."
    ),
    "removed_by_6b5e_policy": (
        "removed_by_adr_0068_admin_metadata — former admin_view parity label; "
        "historical/docs/tests only."
    ),
    "legacy_transition_parity": (
        "removed_by_adr_0068_admin_metadata — admin metadata key removed by "
        "ADR-0068; historical/docs/tests only."
    ),
    # Phase 6B-9 surfaces (ADR-0069)
    "viewer_room_id": (
        "deprecated_public_client_alias_keep + still_needed_public_client_compatibility + "
        "needs_dedicated_adr_before_removal — deprecated public WS RuntimeSnapshot "
        "field. Phase 6B-12 adds public deprecation metadata and one-time "
        "client fallback warnings while preserving the alias. Removal requires "
        "a future ADR + proven client migration (ADR-0069)"
    ),
    "w5_player_view": (
        "public_authority + w5_first_already_migrated — W5 player-shell "
        "projection surface; wired in Phase 6B-1; public authority for "
        "player-facing actor-situation/location (ADR-0069)"
    ),
}


# Phase 6B-4 — closed taxonomy enum. The script lists this so downstream tests
# can cross-check the labels in ``PHASE_6B4_CLASSIFICATION`` against the
# canonical inventory taxonomy. Phase 6B-4 introduces no new failure modes —
# the script remains non-failing. Phase 6B-5 may promote a candidate from
# ``newly_dead_candidate_for_6b5`` into the deletion plan, but only after a
# dedicated ADR records the safety contract.
PHASE_6B4_TAXONOMY: tuple[str, ...] = (
    "still_needed_explicit_opt_out",
    "still_needed_malformed_w5_safety",
    "still_needed_old_payload_compatibility",
    "still_needed_public_client_compatibility",
    "substrate_keep_future_adr",
    "w5_first_migrated_keep_temporarily",
    "newly_dead_candidate_for_6b5",
    "needs_dedicated_adr_before_removal",
    "test_only_update",
    "doc_only_update",
    "unknown_needs_runtime_trace",
    # Phase 6B-8 additions
    "removed_by_adr_0068",
    "retired_phase_6b6b",
    "removed_by_adr_0068_admin_metadata",
    # Phase 6B-9 additions
    "w5_first_already_migrated",
    # Phase 6B-12 additions
    "deprecated_public_client_alias_keep",
    "public_authority",
    # Phase 6C-0 additions
    "w5_first_migration_candidate",
    "public_compatibility_keep",
    "unrelated_domain_use",
    "needs_dedicated_adr",
)


PHASE_6B13_READINESS_REPORT: dict[str, object] = {
    "phase": "6B-13",
    "public_aliases_still_emitted": True,
    "w5_player_view_authority_present": True,
    "frontend_helpers_prefer_w5": True,
    "legacy_fallback_still_tested": True,
    "internal_alias_authority_consumers": "not_proven_zero_static_inventory_required",
    "docs_describe_aliases_as_primary": False,
    "removal_ready": False,
    "reason": "client_readiness_window_active",
    "required_evidence_before_removal_adr": [
        "production_like_ws_payloads_include_w5_player_view",
        "frontend_and_supported_clients_read_w5_before_aliases",
        "alias_fallback_warning_or_telemetry_window_shows_no_supported_client_dependency",
        "docs_describe_aliases_only_as_deprecated_compatibility",
    ],
}


def phase_6b13_readiness_report() -> dict[str, object]:
    """Return the non-failing public room alias readiness gate result."""

    required_evidence = PHASE_6B13_READINESS_REPORT["required_evidence_before_removal_adr"]
    return {
        **PHASE_6B13_READINESS_REPORT,
        "required_evidence_before_removal_adr": list(required_evidence)
        if isinstance(required_evidence, list)
        else [],
    }


PHASE_6C0_LOCATION_FRAMING_INVENTORY: tuple[dict[str, object], ...] = (
    {
        "file_path": "ai_stack/contracts/narrator_consequence_contracts.py",
        "line": 106,
        "symbol": "_current_context_area",
        "classification": "w5_first_migration_candidate",
        "surface_kind": "runtime",
        "current_role": (
            "Selects the current narrative area from player_local_context.current_location_id, "
            "player_local_context.current_area, or scene_affordances.current_area."
        ),
        "legacy_fields": ["current_area", "current_location_id"],
        "w5_replacement_surface": (
            "W5Projection(target_consumer='narrator').where_summary.current_location "
            "or scene_location.value, with legacy local context only as fallback."
        ),
        "migration_risk": (
            "High: feeds LocalContextTransition and can alter committed narrator "
            "consequence metadata."
        ),
        "tests_required": [
            "ai_stack/tests/test_narrator_consequence_contract.py",
            "ai_stack/tests/test_w5_actor_tracking_projection.py",
            "world-engine/tests/test_story_runtime_w5_narrator_projection.py",
        ],
    },
    {
        "file_path": "ai_stack/contracts/narrator_consequence_contracts.py",
        "line": 123,
        "symbol": "_base_local_context_transition",
        "classification": "w5_first_migration_candidate",
        "surface_kind": "runtime",
        "current_role": "Emits from_area/to_area and from_location_id/to_location_id transition fields.",
        "legacy_fields": ["from_area", "to_area", "current_area"],
        "w5_replacement_surface": (
            "A W5 location-framing helper derived from narrator where_summary "
            "previous_location/current_location/location_changed."
        ),
        "migration_risk": (
            "High: these keys are consumed by narrator_consequence_plan, sensory_context, "
            "player_local_context, tests, and debug surfaces."
        ),
        "tests_required": [
            "ai_stack/tests/test_narrator_consequence_contract.py",
            "ai_stack/tests/test_sensory_context_engine.py",
            "ai_stack/tests/test_langgraph_runtime.py",
        ],
    },
    {
        "file_path": "ai_stack/contracts/narrator_consequence_contracts.py",
        "line": 231,
        "symbol": "build_narrator_consequence_plan",
        "classification": "w5_first_migration_candidate",
        "surface_kind": "runtime",
        "current_role": (
            "Builds consequence_type and area-transition text from LocalContextTransition "
            "plus authored scene-affordance detail."
        ),
        "legacy_fields": ["to_area", "transition_type"],
        "w5_replacement_surface": (
            "W5-first location framing for movement/transition selection, while authored "
            "scene affordance detail remains the text source."
        ),
        "migration_risk": (
            "Medium-high: should not change authored detail selection except where W5 "
            "proves a different committed location authority."
        ),
        "tests_required": [
            "ai_stack/tests/test_narrator_consequence_contract.py",
            "ai_stack/tests/test_pr_b_narrator_consequence_realization_contract.py",
        ],
    },
    {
        "file_path": "ai_stack/contracts/narrator_consequence_contracts.py",
        "line": 308,
        "symbol": "build_updated_player_local_context",
        "classification": "w5_first_migration_candidate",
        "surface_kind": "runtime",
        "current_role": (
            "Persists current_area/current_location_id/previous_area after a committed "
            "local context transition."
        ),
        "legacy_fields": ["current_area", "current_location_id", "previous_area"],
        "w5_replacement_surface": (
            "W5 location framing writes only compatibility local-context aliases after "
            "the W5-derived authority is accepted by tests."
        ),
        "migration_risk": (
            "High: touches carried player_local_context state and therefore later turns."
        ),
        "tests_required": [
            "ai_stack/tests/test_narrator_consequence_contract.py",
            "tests/test_pr_b_live_effect_propagation.py",
        ],
    },
    {
        "file_path": "ai_stack/story_runtime/narrative/sensory_context_engine.py",
        "line": 136,
        "symbol": "_current_location_id",
        "classification": "w5_first_migration_candidate",
        "surface_kind": "runtime",
        "current_role": (
            "Selects sensory room location from LocalContextTransition to_area/current_area/"
            "from_area, then prior sensory state, current scene id, then scene_affordances.current_area."
        ),
        "legacy_fields": ["to_area", "current_area", "from_area"],
        "w5_replacement_surface": (
            "W5-first location framing current_location_id with legacy transition and "
            "scene-affordance fallbacks retained for malformed-W5 safety."
        ),
        "migration_risk": (
            "Medium-high: changes selected sensory room layers and validation evidence."
        ),
        "tests_required": [
            "ai_stack/tests/test_sensory_context_engine.py",
            "tests/gates/test_goc_mvp04_observability_diagnostics_gate.py",
        ],
    },
    {
        "file_path": "ai_stack/story_runtime/narrative/sensory_context_engine.py",
        "line": 322,
        "symbol": "_append_location_layers",
        "classification": "w5_first_migration_candidate",
        "surface_kind": "runtime",
        "current_role": "Builds room ambient and location-entry sensory layers for the selected location_id.",
        "legacy_fields": ["local_context_transition"],
        "w5_replacement_surface": (
            "W5 location framing source attribution should decide whether entry layers "
            "are movement-required; authored palette/detail remains the sensory text source."
        ),
        "migration_risk": "Medium: layer requiredness and evidence refs may change.",
        "tests_required": [
            "ai_stack/tests/test_sensory_context_engine.py",
            "ai_stack/tests/test_runtime_aspect_ledger.py",
        ],
    },
    {
        "file_path": "ai_stack/language_io/language_adapter.py",
        "line": 320,
        "symbol": "_interaction_surface_cached",
        "classification": "w5_first_migration_candidate",
        "surface_kind": "runtime",
        "current_role": (
            "Seeds semantic interaction surface current_area from authored layout "
            "narrative_anchor_area_id/live_play_default_location_id."
        ),
        "legacy_fields": ["current_area"],
        "w5_replacement_surface": (
            "Runtime overlay should prefer W5 narrator/player location framing while "
            "the cached authored surface remains content fallback."
        ),
        "migration_risk": (
            "Medium: adapter cache is content-derived; runtime W5 data must not poison "
            "module-level cached surfaces."
        ),
        "tests_required": [
            "ai_stack/tests/test_free_player_action_resolution_contract.py",
            "tests/smoke/test_template_module_structure_smoke.py",
            "tests/smoke/test_goc_module_structure_smoke.py",
        ],
    },
    {
        "file_path": "ai_stack/langgraph/runtime_executor/executor_action_resolution_commit.py",
        "line": 153,
        "symbol": "_resolve_player_action SOURCE_LINES",
        "classification": "w5_first_migration_candidate",
        "surface_kind": "runtime",
        "current_role": (
            "LangGraph commit node calls build_local_context_transition and "
            "build_narrator_consequence_plan with legacy scene affordance/local context inputs."
        ),
        "legacy_fields": ["local_context_transition", "current_area", "from_area", "to_area"],
        "w5_replacement_surface": (
            "Thread a W5 location-framing object into narrator consequence contracts "
            "after W5 projection is available in RuntimeTurnState."
        ),
        "migration_risk": (
            "High: graph state updates become committed turn metadata and must remain additive first."
        ),
        "tests_required": [
            "ai_stack/tests/test_langgraph_runtime.py",
            "tests/gates/test_goc_mvp03_live_dramatic_scene_simulator_gate.py",
        ],
    },
    {
        "file_path": "ai_stack/langgraph/runtime_executor/executor_symbolic_meta_genre_derivation.py",
        "line": 152,
        "symbol": "_derive_sensory_context SOURCE_LINES",
        "classification": "w5_first_migration_candidate",
        "surface_kind": "runtime",
        "current_role": "Passes action_actual.local_context_transition into derive_sensory_context.",
        "legacy_fields": ["local_context_transition"],
        "w5_replacement_surface": (
            "Pass W5 location framing to derive_sensory_context before falling back "
            "to LocalContextTransition."
        ),
        "migration_risk": "Medium-high: affects sensory context target and aspect ledger diagnostics.",
        "tests_required": [
            "ai_stack/tests/test_sensory_context_engine.py",
            "ai_stack/tests/test_runtime_aspect_ledger.py",
        ],
    },
    {
        "file_path": "ai_stack/contracts/environment_state_contracts.py",
        "line": 414,
        "symbol": "_apply_environment_movement / apply_action_to_environment_state",
        "classification": "substrate_keep_future_adr",
        "surface_kind": "substrate",
        "current_role": (
            "Writes current_room_id/current_area/previous_room_id/previous_area and "
            "actor_locations after committed movement."
        ),
        "legacy_fields": ["current_room_id", "current_area", "previous_room_id", "previous_area", "actor_locations"],
        "w5_replacement_surface": (
            "Out of scope for Phase 6C-0; remains substrate input for W5 extraction "
            "until a future substrate ADR."
        ),
        "migration_risk": "Very high: substrate writer, committed events, and W5 extractor input.",
        "tests_required": [
            "ai_stack/tests/test_w5_actor_tracking_validation.py",
            "backend/tests/runtime/test_runtime_core.py",
        ],
    },
    {
        "file_path": "backend/app/runtime/models.py",
        "line": 146,
        "symbol": "RuntimeSnapshot.viewer_room_id/current_room",
        "classification": "public_compatibility_keep",
        "surface_kind": "public_api",
        "current_role": "Deprecated public WS room aliases preserved by ADR-0069.",
        "legacy_fields": ["viewer_room_id", "current_room"],
        "w5_replacement_surface": "w5_player_view.where_summary.current_visible_location / where_summary",
        "migration_risk": "Public compatibility risk; removal remains blocked by 6B-13 readiness gate.",
        "tests_required": [
            "world-engine/tests/test_story_runtime_w5_ws_snapshot_population.py",
            "backend/tests/test_w5_player_shell_payload.py",
        ],
    },
    {
        "file_path": "backend/app/api/v1/game/player_shell_state_projection.py",
        "line": 66,
        "symbol": "build_player_shell_state_view",
        "classification": "public_compatibility_keep",
        "surface_kind": "public_api",
        "current_role": "Emits deprecated HTTP/player-shell current_room_id alias and alias telemetry.",
        "legacy_fields": ["current_room_id"],
        "w5_replacement_surface": "w5_player_view.where_summary.current_visible_location",
        "migration_risk": "Public compatibility risk; do not remove in narrator/sensory migration.",
        "tests_required": ["backend/tests/test_w5_player_shell_payload.py"],
    },
    {
        "file_path": "world-engine/app/story_runtime/manager/dramatic_context_authority.py",
        "line": 213,
        "symbol": "_phase1_canonical_context_for_session",
        "classification": "needs_dedicated_adr",
        "surface_kind": "runtime",
        "current_role": (
            "Uses session.environment_state.current_room_id as live scene input for "
            "Director-Pause canonical context."
        ),
        "legacy_fields": ["current_room_id"],
        "w5_replacement_surface": (
            "Future Director/canonical-path ADR should decide whether W5 director "
            "projection replaces this substrate read."
        ),
        "migration_risk": "High: Director-Pause and canonical-path readiness semantics.",
        "tests_required": ["world-engine/tests/test_runtime_manager.py"],
    },
    {
        "file_path": "backend/app/runtime/narrative/short_term_context.py",
        "line": 152,
        "symbol": "ShortTermContext.build",
        "classification": "unrelated_domain_use",
        "surface_kind": "runtime",
        "current_role": "Computes backend session-history scene_changed from prior and updated scene ids.",
        "legacy_fields": ["scene_changed"],
        "w5_replacement_surface": "None for Phase 6C-0; not narrator consequence/sensory location framing.",
        "migration_risk": "Low for this phase; do not fold into W5 narrator migration.",
        "tests_required": [
            "backend/tests/runtime/test_short_term_context.py",
            "backend/tests/runtime/test_session_history.py",
        ],
    },
    {
        "file_path": "ai_stack/tests/test_narrator_consequence_contract.py",
        "line": 112,
        "symbol": "LocalContextTransition assertions",
        "classification": "test_only_update",
        "surface_kind": "test",
        "current_role": "Locks current from_area/to_area/current_area transition contract.",
        "legacy_fields": ["from_area", "to_area", "current_area"],
        "w5_replacement_surface": (
            "Update in the implementation phase to assert W5-first helper output "
            "and retained compatibility fields."
        ),
        "migration_risk": "Medium: tests reveal intended contract changes.",
        "tests_required": ["ai_stack/tests/test_narrator_consequence_contract.py"],
    },
    {
        "file_path": "docs/ADR/adr-0069-w5-player-view-replaces-current-room-aliases.md",
        "line": 1,
        "symbol": "ADR-0069",
        "classification": "doc_only_update",
        "surface_kind": "doc",
        "current_role": "Documents public player-room alias compatibility window.",
        "legacy_fields": ["current_room", "current_room_id", "viewer_room_id"],
        "w5_replacement_surface": "ADR-0070 should reference ADR-0069 and keep public alias removal out of scope.",
        "migration_risk": "Low documentation drift risk.",
        "tests_required": ["tests/test_inventory_w5_legacy_consumers.py"],
    },
)


PHASE_6C0_IMPLEMENTATION_PLAN: dict[str, object] = {
    "phase": "6C-0",
    "adr": "ADR-0070",
    "runtime_implementation_in_phase_6c0": False,
    "implementation_deferred_reason": (
        "The migration touches committed LocalContextTransition/NarratorConsequencePlan "
        "metadata, sensory_context target derivation, LangGraph SOURCE_LINES callsites, "
        "and carried player_local_context. It should land as a dedicated implementation "
        "phase with parity fixtures instead of changing runtime behavior inside the ADR/inventory task."
    ),
    "proposed_helper_module": "ai_stack/actor_tracking/location_framing.py",
    "proposed_helper_functions": [
        "build_w5_location_framing(projection, *, previous_projection=None, legacy_fallback=None)",
        "location_framing_to_local_context_transition(framing, *, legacy_transition=None)",
    ],
    "input_contract": (
        "W5Projection(target_consumer='narrator') or dict with where_summary/how_summary/"
        "why_summary/source_attribution/truth_attribution plus optional legacy fallback."
    ),
    "output_contract": (
        "w5_location_framing.v1 dict containing current_location_id, previous_location_id, "
        "from_location_id, to_location_id, location_changed, transition_type, "
        "how_summary, why_summary, truth_attribution, source_attribution, "
        "legacy_fallback_used."
    ),
    "files_to_touch_next": [
        "ai_stack/actor_tracking/location_framing.py",
        "ai_stack/actor_tracking/__init__.py",
        "ai_stack/contracts/narrator_consequence_contracts.py",
        "ai_stack/story_runtime/narrative/sensory_context_engine.py",
        "ai_stack/langgraph/runtime_executor/executor_action_resolution_commit.py",
        "ai_stack/langgraph/runtime_executor/executor_symbolic_meta_genre_derivation.py",
        "ai_stack/langgraph/langgraph_synthetic_action_resolution.py",
        "ai_stack/tests/test_narrator_consequence_contract.py",
        "ai_stack/tests/test_sensory_context_engine.py",
    ],
    "fallback_posture": (
        "W5-first when valid narrator projection location exists; legacy current_area/"
        "from_area/to_area remains malformed-W5 safety fallback; public aliases and "
        "substrate writers are untouched."
    ),
    "feature_flag": (
        "Prefer default-on diagnostic flag only if parity rollout needs live comparison; "
        "do not add a strict-off runtime rollback unless a follow-up ADR requires it."
    ),
    "docs_to_update_next": [
        "docs/MVPs/w5_actor_tracking_migration.md",
        "docs/MVPs/w5_legacy_consumer_removal_inventory.md",
        "docs/ADR/adr-0070-w5-actor-tracking-replaces-narrator-consequence-location-framing.md",
    ],
}


PHASE_6C1_LOCATION_FRAMING_REPORT: dict[str, object] = {
    "phase": "6C-1",
    "helper_module": "ai_stack/actor_tracking/location_framing.py",
    "helper_schema_version": "w5_location_framing.v1",
    "helper_functions": [
        "build_w5_location_framing",
        "location_framing_to_local_context_transition",
    ],
    "typed_coercion_required": True,
    "raw_w5_history_emitted": False,
    "how_first_class": True,
    "inferred_why_soft_truth": True,
    "legacy_fallback_retained": True,
    "public_aliases_removed": False,
    "substrate_fields_removed": False,
    "default_graph_synthesizes_w5_location_framing": False,
    "additive_integration_points": [
        "ai_stack/contracts/narrator_consequence_contracts.py",
        "ai_stack/story_runtime/narrative/sensory_context_engine.py",
        "ai_stack/langgraph/runtime_executor/executor_action_resolution_commit.py",
        "ai_stack/langgraph/runtime_executor/executor_symbolic_meta_genre_derivation.py",
    ],
    "deferred_to_phase_6c2": [
        "graph-owned construction of state['w5_location_framing'] from narrator W5 projection",
        "default W5 source switch for narrator consequence transition framing",
        "language-adapter runtime overlay that does not poison cached authored current_area",
    ],
}


PHASE_6C2_LOCATION_FRAMING_REPORT: dict[str, object] = {
    "phase": "6C-2",
    "graph_owned_synthesis": True,
    "synthesis_point": "ai_stack/langgraph/runtime_executor/executor_action_resolution_commit.py",
    "synthesis_symbol": "_resolve_player_action SOURCE_LINES",
    "state_field": "w5_location_framing",
    "source": "w5_latest_snapshot via build_w5_location_framing",
    "typed_coercion_required": True,
    "raw_w5_history_emitted": False,
    "committed_events_mutated": False,
    "legacy_fallback_retained": True,
    "current_area_from_area_to_area_removed": False,
    "public_aliases_removed": False,
    "substrate_fields_removed": False,
    "default_authority_switch_complete": False,
    "diagnostics": [
        "w5_location_framing_used",
        "w5_location_framing_failed",
        "w5_location_framing_source",
        "w5_location_framing_fallback_reason",
        "w5_location_changed",
        "w5_current_location",
        "w5_previous_location",
    ],
    "parity_evidence": [
        "legacy movement target is preserved when pre-commit W5 location has location_changed=false",
        "W5 location_changed=true maps to scene_changed/location_changed compatibility fields",
        "sensory context same-location resolution matches legacy current_area resolution",
        "missing/malformed W5 remains fallback-compatible and non-crashing",
    ],
    "deferred_to_phase_6c3": [
        "switch narrator consequence transition authority to W5-first by default",
        "switch sensory-context location authority to graph-owned W5 framing by default",
        "language-adapter runtime overlay for current_area without cache poisoning",
    ],
}


PHASE_6C3_LOCATION_FRAMING_AUTHORITY_REPORT: dict[str, object] = {
    "phase": "6C-3",
    "w5_first_authority_switch": True,
    "authority_surface": "ai_stack/actor_tracking/location_framing.py",
    "narrator_consequence_surface": "ai_stack/contracts/narrator_consequence_contracts.py",
    "sensory_context_surface": "ai_stack/story_runtime/narrative/sensory_context_engine.py",
    "valid_w5_authority_condition": "source == 'w5_projection' and a current/scene/to location is present",
    "legacy_fallback_conditions": [
        "missing_w5",
        "malformed_w5",
        "incomplete_w5_location",
        "pre_commit_w5_no_location_change_with_fresh_legacy_movement_target",
        "old_payload_without_w5_location_framing",
    ],
    "legacy_fallback_retained": True,
    "current_area_from_area_to_area_removed": False,
    "public_aliases_removed": False,
    "substrate_fields_removed": False,
    "committed_events_mutated": False,
    "diagnostics": [
        "w5_location_framing_used",
        "w5_location_framing_source",
        "w5_location_framing_fallback_reason",
        "w5_location_changed",
        "w5_current_location",
        "w5_previous_location",
        "location_framing_authority",
        "local_context_transition_source",
    ],
    "parity_evidence": [
        "valid W5 current location maps to current_area/current_room compatibility",
        "valid W5 previous/current maps to from_area/to_area compatibility",
        "W5 location_changed=true drives scene/location shift behavior",
        "W5 location_changed=false does not force a shift",
        "missing/malformed W5 and old payloads keep legacy fallback",
        "sensory context resolves the same location_id when W5 and legacy agree",
        "How remains first-class and inferred Why remains soft truth",
    ],
    "next_phase": "6C-4 fresh inventory and targeted cleanup planning only",
}


PHASE_6C4_POST_AUTHORITY_INVENTORY: tuple[dict[str, object], ...] = (
    {
        "file_path": "ai_stack/actor_tracking/location_framing.py",
        "symbol": "location_framing_is_valid_w5",
        "classification": "w5_first_authority",
        "surface_kind": "runtime",
        "current_role": (
            "Defines valid W5 location authority as source == 'w5_projection' "
            "with a usable current/scene/to location."
        ),
        "legacy_fields": [],
        "w5_replacement_exists": True,
        "used_in_default_happy_path": True,
        "removal_would_break_fallback": False,
        "recommended_action": "Keep as the central authority predicate.",
        "tests_required_before_future_removal": [
            "ai_stack/tests/test_w5_actor_tracking_location_framing.py",
        ],
    },
    {
        "file_path": "ai_stack/actor_tracking/location_framing.py",
        "symbol": "location_framing_to_local_context_transition",
        "classification": "w5_first_authority",
        "surface_kind": "runtime",
        "current_role": (
            "Projects valid W5 current/previous/location_changed into the "
            "LocalContextTransition compatibility shape."
        ),
        "legacy_fields": ["current_area", "from_area", "to_area", "scene_changed"],
        "w5_replacement_exists": True,
        "used_in_default_happy_path": True,
        "removal_would_break_fallback": True,
        "recommended_action": (
            "Keep compatibility fields until a future ADR proves all consumers "
            "read W5 authority diagnostics or W5-native fields."
        ),
        "tests_required_before_future_removal": [
            "ai_stack/tests/test_w5_actor_tracking_location_framing.py",
            "ai_stack/tests/test_narrator_consequence_contract.py",
            "ai_stack/tests/test_sensory_context_engine.py",
        ],
    },
    {
        "file_path": "ai_stack/contracts/narrator_consequence_contracts.py",
        "symbol": "_current_context_area",
        "classification": "w5_first_authority",
        "surface_kind": "runtime",
        "current_role": (
            "Chooses valid W5 current/scene location before legacy "
            "player_local_context or scene affordance current_area."
        ),
        "legacy_fields": ["current_area", "current_location_id"],
        "w5_replacement_exists": True,
        "used_in_default_happy_path": True,
        "removal_would_break_fallback": True,
        "recommended_action": (
            "Keep legacy reads as fallback; future removal requires old-payload "
            "and malformed-W5 evidence."
        ),
        "tests_required_before_future_removal": [
            "ai_stack/tests/test_w5_actor_tracking_location_framing.py",
            "ai_stack/tests/test_narrator_consequence_contract.py",
        ],
    },
    {
        "file_path": "ai_stack/contracts/narrator_consequence_contracts.py",
        "symbol": "build_local_context_transition",
        "classification": "w5_first_authority",
        "surface_kind": "runtime",
        "current_role": (
            "Builds the transition through W5-first location framing when a "
            "valid graph-owned framing object is present."
        ),
        "legacy_fields": ["current_area", "from_area", "to_area", "local_context_transition"],
        "w5_replacement_exists": True,
        "used_in_default_happy_path": True,
        "removal_would_break_fallback": True,
        "recommended_action": (
            "Keep transition compatibility keys; classify them as output "
            "compatibility/fallback rather than location authority."
        ),
        "tests_required_before_future_removal": [
            "ai_stack/tests/test_w5_actor_tracking_location_framing.py",
            "ai_stack/tests/test_langgraph_runtime.py",
        ],
    },
    {
        "file_path": "ai_stack/contracts/narrator_consequence_contracts.py",
        "symbol": "build_narrator_consequence_plan",
        "classification": "w5_first_authority",
        "surface_kind": "runtime",
        "current_role": (
            "Records W5 location-framing diagnostics and consumes the effective "
            "local_context_transition."
        ),
        "legacy_fields": ["to_area", "transition_type", "local_context_transition"],
        "w5_replacement_exists": True,
        "used_in_default_happy_path": True,
        "removal_would_break_fallback": True,
        "recommended_action": (
            "Keep legacy transition text inputs until consequence realization "
            "has W5-native fixtures."
        ),
        "tests_required_before_future_removal": [
            "ai_stack/tests/test_w5_actor_tracking_location_framing.py",
            "ai_stack/tests/test_pr_b_narrator_consequence_realization_contract.py",
        ],
    },
    {
        "file_path": "ai_stack/contracts/narrator_consequence_contracts.py",
        "symbol": "build_updated_player_local_context",
        "classification": "legacy_fallback_keep",
        "surface_kind": "runtime",
        "current_role": (
            "Carries current_area/current_location_id compatibility context into "
            "later turns after the W5-first transition has been resolved."
        ),
        "legacy_fields": ["current_area", "current_location_id", "previous_area"],
        "w5_replacement_exists": True,
        "used_in_default_happy_path": False,
        "removal_would_break_fallback": True,
        "recommended_action": (
            "Keep until a future ADR defines W5-native carried local context "
            "and old-payload fallback behavior."
        ),
        "tests_required_before_future_removal": [
            "ai_stack/tests/test_narrator_consequence_contract.py",
            "tests/test_pr_b_live_effect_propagation.py",
        ],
    },
    {
        "file_path": "ai_stack/story_runtime/narrative/sensory_context_engine.py",
        "symbol": "_current_location_id",
        "classification": "w5_first_authority",
        "surface_kind": "runtime",
        "current_role": (
            "Resolves sensory location_id from valid W5 location framing before "
            "legacy transition/current-area fallbacks."
        ),
        "legacy_fields": ["to_area", "current_area", "from_area"],
        "w5_replacement_exists": True,
        "used_in_default_happy_path": True,
        "removal_would_break_fallback": True,
        "recommended_action": (
            "Keep legacy fallback order for malformed W5 and old payloads; do "
            "not remove until sensory parity covers live graph fixtures."
        ),
        "tests_required_before_future_removal": [
            "ai_stack/tests/test_w5_actor_tracking_location_framing.py",
            "ai_stack/tests/test_sensory_context_engine.py",
            "tests/gates/test_goc_mvp04_observability_diagnostics_gate.py",
        ],
    },
    {
        "file_path": "ai_stack/story_runtime/narrative/sensory_context_engine.py",
        "symbol": "_append_location_layers",
        "classification": "legacy_fallback_keep",
        "surface_kind": "runtime",
        "current_role": (
            "Uses the already-resolved effective location transition to select "
            "authored room/layer details."
        ),
        "legacy_fields": ["local_context_transition"],
        "w5_replacement_exists": True,
        "used_in_default_happy_path": True,
        "removal_would_break_fallback": True,
        "recommended_action": (
            "Keep authored detail selection stable; only migrate requiredness "
            "after W5-native sensory fixtures exist."
        ),
        "tests_required_before_future_removal": [
            "ai_stack/tests/test_sensory_context_engine.py",
            "ai_stack/tests/test_runtime_aspect_ledger.py",
        ],
    },
    {
        "file_path": "ai_stack/langgraph/runtime_executor/executor_action_resolution_commit.py",
        "symbol": "_resolve_player_action SOURCE_LINES",
        "classification": "w5_first_authority",
        "surface_kind": "runtime",
        "current_role": (
            "Synthesizes state['w5_location_framing'] and threads it through "
            "local context and narrator consequence planning."
        ),
        "legacy_fields": ["local_context_transition", "current_area", "from_area", "to_area"],
        "w5_replacement_exists": True,
        "used_in_default_happy_path": True,
        "removal_would_break_fallback": True,
        "recommended_action": (
            "Keep graph diagnostics and fallback values; next cleanup should "
            "target stale docs/tests, not runtime deletion."
        ),
        "tests_required_before_future_removal": [
            "ai_stack/tests/test_langgraph_runtime.py",
            "tests/gates/test_goc_mvp03_live_dramatic_scene_simulator_gate.py",
        ],
    },
    {
        "file_path": "ai_stack/langgraph/runtime_executor/executor_symbolic_meta_genre_derivation.py",
        "symbol": "_derive_sensory_context SOURCE_LINES",
        "classification": "w5_first_authority",
        "surface_kind": "runtime",
        "current_role": (
            "Passes graph-owned w5_location_framing into derive_sensory_context "
            "alongside the legacy action_actual transition."
        ),
        "legacy_fields": ["local_context_transition"],
        "w5_replacement_exists": True,
        "used_in_default_happy_path": True,
        "removal_would_break_fallback": True,
        "recommended_action": (
            "Keep the legacy transition argument until sensory-context old-payload "
            "fallback has a dedicated removal ADR."
        ),
        "tests_required_before_future_removal": [
            "ai_stack/tests/test_sensory_context_engine.py",
            "ai_stack/tests/test_runtime_aspect_ledger.py",
        ],
    },
    {
        "file_path": "ai_stack/language_io/language_adapter.py",
        "symbol": "_interaction_surface_cached",
        "classification": "legacy_fallback_keep",
        "surface_kind": "runtime",
        "current_role": (
            "Builds authored content fallback current_area from layout defaults; "
            "runtime W5 data must not poison this cache."
        ),
        "legacy_fields": ["current_area"],
        "w5_replacement_exists": False,
        "used_in_default_happy_path": False,
        "removal_would_break_fallback": True,
        "recommended_action": (
            "Keep as content fallback. A runtime overlay, if needed, must be "
            "separate from the cached authored surface."
        ),
        "tests_required_before_future_removal": [
            "ai_stack/tests/test_free_player_action_resolution_contract.py",
            "tests/smoke/test_template_module_structure_smoke.py",
            "tests/smoke/test_goc_module_structure_smoke.py",
        ],
    },
    {
        "file_path": "backend/app/runtime/models.py",
        "symbol": "RuntimeSnapshot.viewer_room_id/current_room",
        "classification": "public_alias_keep",
        "surface_kind": "public_api",
        "current_role": "Emits deprecated public WS room aliases under ADR-0069.",
        "legacy_fields": ["viewer_room_id", "current_room"],
        "w5_replacement_exists": True,
        "used_in_default_happy_path": False,
        "removal_would_break_fallback": True,
        "recommended_action": (
            "Do not touch in 6C; public alias removal remains blocked by "
            "client-readiness evidence."
        ),
        "tests_required_before_future_removal": [
            "world-engine/tests/test_story_runtime_w5_ws_snapshot_population.py",
            "frontend/tests/test_w5_room_alias_helpers.js",
        ],
    },
    {
        "file_path": "backend/app/api/v1/game/player_shell_state_projection.py",
        "symbol": "build_player_shell_state_view",
        "classification": "public_alias_keep",
        "surface_kind": "public_api",
        "current_role": "Emits deprecated HTTP/player-shell current_room_id alias and telemetry.",
        "legacy_fields": ["current_room_id"],
        "w5_replacement_exists": True,
        "used_in_default_happy_path": False,
        "removal_would_break_fallback": True,
        "recommended_action": (
            "Keep under ADR-0069 until the public alias readiness gate reports "
            "removal_ready=true."
        ),
        "tests_required_before_future_removal": [
            "backend/tests/test_w5_player_shell_payload.py",
        ],
    },
    {
        "file_path": "ai_stack/contracts/environment_state_contracts.py",
        "symbol": "_apply_environment_movement / apply_action_to_environment_state",
        "classification": "substrate_keep_future_adr",
        "surface_kind": "substrate",
        "current_role": (
            "Writes current_room_id/current_area/actor_locations substrate used "
            "by commits and W5 extraction."
        ),
        "legacy_fields": ["current_room_id", "current_area", "actor_locations"],
        "w5_replacement_exists": False,
        "used_in_default_happy_path": True,
        "removal_would_break_fallback": True,
        "recommended_action": "Keep; substrate changes require a future ADR.",
        "tests_required_before_future_removal": [
            "ai_stack/tests/test_w5_actor_tracking_validation.py",
            "backend/tests/runtime/test_runtime_core.py",
        ],
    },
    {
        "file_path": "backend/app/runtime/narrative/short_term_context.py",
        "symbol": "ShortTermContext.build",
        "classification": "unrelated_domain_use",
        "surface_kind": "runtime",
        "current_role": "Uses scene_changed for backend session-history scene-id comparison.",
        "legacy_fields": ["scene_changed"],
        "w5_replacement_exists": False,
        "used_in_default_happy_path": True,
        "removal_would_break_fallback": False,
        "recommended_action": "Leave out of narrator/sensory W5 cleanup.",
        "tests_required_before_future_removal": [
            "backend/tests/runtime/test_short_term_context.py",
            "backend/tests/runtime/test_session_history.py",
        ],
    },
    {
        "file_path": "ai_stack/tests/test_w5_actor_tracking_location_framing.py",
        "symbol": "Phase 6C location-framing tests",
        "classification": "test_only_update",
        "surface_kind": "test",
        "current_role": (
            "Proves W5-first authority diagnostics, fallback authority, "
            "compatibility fields, no raw W5 history, How, and soft inferred Why."
        ),
        "legacy_fields": ["current_area", "from_area", "to_area"],
        "w5_replacement_exists": True,
        "used_in_default_happy_path": True,
        "removal_would_break_fallback": False,
        "recommended_action": (
            "Keep and extend as the semantic proof set for any future removal ADR."
        ),
        "tests_required_before_future_removal": [
            "ai_stack/tests/test_w5_actor_tracking_location_framing.py",
        ],
    },
    {
        "file_path": "docs/MVPs/w5_legacy_consumer_removal_inventory.md",
        "symbol": "Phase 6C-4 section",
        "classification": "doc_only_update",
        "surface_kind": "doc",
        "current_role": "Documents post-6C-3 W5-first authority and fallback surfaces.",
        "legacy_fields": ["current_area", "from_area", "to_area", "current_room", "current_room_id"],
        "w5_replacement_exists": True,
        "used_in_default_happy_path": True,
        "removal_would_break_fallback": False,
        "recommended_action": "Keep current; update after the next cleanup inventory.",
        "tests_required_before_future_removal": [
            "tests/test_inventory_w5_legacy_consumers.py",
        ],
    },
)


PHASE_6C4_CLEANUP_PLAN: dict[str, object] = {
    "phase": "6C-4",
    "inventory_method": (
        "Static scan for current_area/from_area/to_area/current_room/current_room_id/"
        "location_changed/scene_changed/local_context_transition/w5_location_framing/"
        "location_framing_authority/local_context_transition_source plus curated "
        "post-6C-3 runtime surface classification."
    ),
    "runtime_legacy_field_removal_in_phase_6c4": False,
    "safe_cleanup_performed": [
        "Updated stale Phase 6C location-framing test wording from additive-only to W5-first authority wording.",
        "Added Phase 6C-4 inventory/report rows and JSON/human report output.",
        "Updated MVP docs and ADR-0070 with post-6C-3 cleanup-plan status.",
    ],
    "cleanup_deliberately_not_performed": [
        "No current_area/from_area/to_area runtime field removal.",
        "No current_room/current_room_id/viewer_room_id public alias removal.",
        "No substrate field or actor_locations removal.",
        "No malformed-W5 or old-payload fallback removal.",
        "No committed event or committed output mutation.",
    ],
    "future_removal_candidates": [
        "LocalContextTransition current_area/from_area/to_area compatibility fields after W5-native consumers exist.",
        "Narrator consequence reliance on transition compatibility text inputs after realization fixtures migrate.",
        "Sensory-context legacy transition fallback after old-payload and malformed-W5 windows close.",
        "Authored language-adapter current_area overlay only if a non-cached W5 runtime overlay is designed.",
    ],
    "required_evidence_before_removal_adr": [
        "Default valid W5 path reports location_framing_authority='w5'.",
        "Missing/malformed W5 reports location_framing_authority='legacy_fallback'.",
        "local_context_transition_source reports w5_location_framing or legacy correctly.",
        "Compatibility fields are proven fallback/compatibility rather than authority when W5 is valid.",
        "No raw W5 history is emitted in narrator/sensory diagnostics.",
        "How remains first-class and inferred Why remains soft truth.",
        "MVP03 and MVP04 gates remain green.",
    ],
    "next_phase": "6C-5 targeted doc/test cleanup or removal-ADR drafting only after fresh parity evidence",
}


def phase_6c0_location_framing_inventory() -> list[dict[str, object]]:
    """Return the curated Phase 6C-0 narrator/sensory location-framing inventory."""

    out: list[dict[str, object]] = []
    for row in PHASE_6C0_LOCATION_FRAMING_INVENTORY:
        copied = dict(row)
        for list_key in ("legacy_fields", "tests_required"):
            value = copied.get(list_key)
            copied[list_key] = list(value) if isinstance(value, list) else []
        out.append(copied)
    return out


def phase_6c1_location_framing_report() -> dict[str, object]:
    """Return the non-failing Phase 6C-1 helper/additive-integration report."""

    out = dict(PHASE_6C1_LOCATION_FRAMING_REPORT)
    for list_key in ("helper_functions", "additive_integration_points", "deferred_to_phase_6c2"):
        value = out.get(list_key)
        out[list_key] = list(value) if isinstance(value, list) else []
    return out


def phase_6c2_location_framing_report() -> dict[str, object]:
    """Return the non-failing Phase 6C-2 graph-synthesis report."""

    out = dict(PHASE_6C2_LOCATION_FRAMING_REPORT)
    for list_key in ("diagnostics", "parity_evidence", "deferred_to_phase_6c3"):
        value = out.get(list_key)
        out[list_key] = list(value) if isinstance(value, list) else []
    return out


def phase_6c3_location_framing_authority_report() -> dict[str, object]:
    """Return the non-failing Phase 6C-3 W5-first authority switch report."""

    out = dict(PHASE_6C3_LOCATION_FRAMING_AUTHORITY_REPORT)
    for list_key in ("legacy_fallback_conditions", "diagnostics", "parity_evidence"):
        value = out.get(list_key)
        out[list_key] = list(value) if isinstance(value, list) else []
    return out


def phase_6c4_post_authority_inventory() -> list[dict[str, object]]:
    """Return the Phase 6C-4 post-authority inventory and cleanup plan rows."""

    out: list[dict[str, object]] = []
    for row in PHASE_6C4_POST_AUTHORITY_INVENTORY:
        copied = dict(row)
        for list_key in ("legacy_fields", "tests_required_before_future_removal"):
            value = copied.get(list_key)
            copied[list_key] = list(value) if isinstance(value, list) else []
        out.append(copied)
    return out


def phase_6c4_classification_summary() -> dict[str, int]:
    """Return counts by Phase 6C-4 classification."""

    summary: dict[str, int] = {}
    for row in PHASE_6C4_POST_AUTHORITY_INVENTORY:
        classification = str(row.get("classification") or "unknown_needs_runtime_trace")
        summary[classification] = summary.get(classification, 0) + 1
    return dict(sorted(summary.items()))


def phase_6c4_cleanup_plan() -> dict[str, object]:
    """Return the non-removal Phase 6C-4 cleanup plan."""

    out = dict(PHASE_6C4_CLEANUP_PLAN)
    for list_key in (
        "safe_cleanup_performed",
        "cleanup_deliberately_not_performed",
        "future_removal_candidates",
        "required_evidence_before_removal_adr",
    ):
        value = out.get(list_key)
        out[list_key] = list(value) if isinstance(value, list) else []
    return out


def phase_6c0_implementation_plan() -> dict[str, object]:
    """Return the non-runtime Phase 6C-0 implementation plan."""

    out = dict(PHASE_6C0_IMPLEMENTATION_PLAN)
    for list_key in ("proposed_helper_functions", "files_to_touch_next", "docs_to_update_next"):
        value = out.get(list_key)
        out[list_key] = list(value) if isinstance(value, list) else []
    return out


EXCLUDED_DIR_NAMES: set[str] = {
    ".git",
    "__pycache__",
    "node_modules",
    ".venv",
    "venv",
    ".pytest_cache",
    ".mypy_cache",
    ".idea",
    ".vscode",
}

# Directory path fragments to exclude (matched against POSIX-style path)
EXCLUDED_PATH_FRAGMENTS: tuple[str, ...] = (
    "'fy'-suites/delagecy/",
    "'fy'-suites/docify/",
    "'fy'-suites/observifyfy/",
    "'fy'-suites/despaghettify/",
    "tests/reports/",
    "world-engine/app/story_runtime/manager/_legacy_sources/",
    # Stale git worktrees are auxiliary workspaces, not active source.
    # Their content may reference historical symbols removed in the main tree.
    ".worktrees/",
    ".claude/worktrees/",
    ".state_tmp/",
)

# Filename patterns to exclude
EXCLUDED_FILENAME_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"^audit_.*\.json$"),
    re.compile(r"^.*\.log$"),
    re.compile(r"^engine_run_last\.txt$"),
    re.compile(r"^failing-tests\.txt$"),
)

INCLUDED_EXTENSIONS: set[str] = {
    ".py",
    ".md",
    ".js",
    ".ts",
    ".tsx",
    ".jsx",
    ".html",
    ".yaml",
    ".yml",
    ".json",
    ".txt",
    ".bak",
}


@dataclass(frozen=True)
class Finding:
    surface: str
    path: str
    line: int
    text: str

    def to_dict(self) -> dict[str, object]:
        return {
            "surface": self.surface,
            "path": self.path,
            "line": self.line,
            "text": self.text[:240],
        }


@dataclass
class ScanReport:
    root: str
    findings: list[Finding] = field(default_factory=list)
    files_scanned: int = 0
    files_skipped: int = 0

    def by_surface(self) -> dict[str, int]:
        counts: dict[str, int] = {key: 0 for key, _ in LEGACY_SURFACES}
        for f in self.findings:
            counts[f.surface] = counts.get(f.surface, 0) + 1
        return counts

    def files_with_findings(self) -> int:
        return len({f.path for f in self.findings})


def _is_excluded_path(path: Path, root: Path) -> bool:
    try:
        rel = path.relative_to(root).as_posix()
    except ValueError:
        return True
    for fragment in EXCLUDED_PATH_FRAGMENTS:
        if fragment in rel:
            return True
    for pat in EXCLUDED_FILENAME_PATTERNS:
        if pat.match(path.name):
            return True
    return False


def _iter_candidate_files(root: Path) -> list[Path]:
    out: list[Path] = []
    for current_dir, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in EXCLUDED_DIR_NAMES]
        for name in files:
            p = Path(current_dir) / name
            if p.suffix.lower() not in INCLUDED_EXTENSIONS:
                continue
            if _is_excluded_path(p, root):
                continue
            out.append(p)
    return out


def scan(root: Path) -> ScanReport:
    report = ScanReport(root=str(root))
    compiled = [(key, re.compile(pattern)) for key, pattern in LEGACY_SURFACES]
    for path in _iter_candidate_files(root):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            report.files_skipped += 1
            continue
        report.files_scanned += 1
        for line_no, line in enumerate(text.splitlines(), start=1):
            for key, regex in compiled:
                if regex.search(line):
                    rel_path = path.relative_to(root).as_posix()
                    report.findings.append(
                        Finding(surface=key, path=rel_path, line=line_no, text=line.strip())
                    )
    return report


def _format_human(report: ScanReport) -> str:
    out: list[str] = []
    out.append("W5 Phase 6A — legacy localization surface scan")
    out.append("=" * 50)
    out.append(f"root: {report.root}")
    out.append(f"files scanned: {report.files_scanned}")
    out.append(f"files skipped: {report.files_skipped}")
    out.append(f"files with findings: {report.files_with_findings()}")
    out.append(f"total findings: {len(report.findings)}")
    out.append("")
    out.append("Count by surface:")
    for key, count in report.by_surface().items():
        out.append(f"  {key:48s} {count:5d}")
    out.append("")
    out.append("Phase 6B-2 classification (informational; authoritative table in")
    out.append("docs/MVPs/w5_legacy_consumer_removal_inventory.md §'Phase 6B-2'):")
    out.append("  S = substrate_keep  O = opt-out fallback  M = malformed-W5 safety")
    out.append("  L = compatibility alias  D = doc/comment only")
    for key, _ in LEGACY_SURFACES:
        label = PHASE_6B2_CLASSIFICATION.get(key, "—")
        out.append(f"  {key:48s} {label}")
    out.append("")
    out.append("Phase 6B-4 classification (informational; authoritative table in")
    out.append("docs/MVPs/w5_legacy_consumer_removal_inventory.md §'Phase 6B-4'):")
    out.append(
        "  closed taxonomy: " + ", ".join(PHASE_6B4_TAXONOMY)
    )
    for key, _ in LEGACY_SURFACES:
        label = PHASE_6B4_CLASSIFICATION.get(key, "—")
        out.append(f"  {key:48s} {label}")
    out.append("")
    out.append(
        "Phase 6B-4 conclusion: no surface is a newly_dead_candidate_for_6b5; every"
    )
    out.append(
        "branch still fires under at least one of D / O / M / L. See the per-branch"
    )
    out.append(
        "matrix in the inventory doc for the full reachability proof."
    )
    out.append("")
    out.append("Phase 6B-6A diagnostics flag retirement surface (informational; authoritative")
    out.append("removal plan in docs/ADR/adr-0066-retire-narrator-legacy-compat-diagnostics-flag.md):")
    _6b6a_keys = (
        "narrator_legacy_compat_diag_flag",
        "narrator_legacy_compat_diag_fn",
        "narrator_legacy_compat_diag_key",
        "legacy_compat_transition_write",
        "demoted_to_legacy_compat",
        "removed_by_6b5e_policy",
        "legacy_transition_parity",
    )
    for key in _6b6a_keys:
        count = sum(1 for f in report.findings if f.surface == key)
        label = PHASE_6B4_CLASSIFICATION.get(key, "—")
        out.append(f"  {key:48s} {count:3d}  {label[:60]}")
    out.append("")
    out.append("Phase 6B-8 — ADR-0068 EXECUTED (operator waiver, 2026-05-28):")
    out.append("  transition_from_previous strict-off rollback path REMOVED.")
    out.append("  w5_ast_narrator_strict_enabled() API REMOVED.")
    out.append("  NarratorStrictOffDeprecationWarning REMOVED; no tombstone retained.")
    out.append("  w5.legacy_transition_parity admin metadata REMOVED.")
    _6b7_keys = ("transition_from_previous", "location_changed")
    for key in _6b7_keys:
        count = sum(1 for f in report.findings if f.surface == key)
        label = PHASE_6B4_CLASSIFICATION.get(key, "—")
        out.append(f"  {key:48s} {count:3d}  {label[:70]}")
    out.append("")
    out.append("ADR-0068 execution checklist (Phase 6B-8, 2026-05-28):")
    tfp_count = sum(1 for f in report.findings if f.surface == "transition_from_previous")
    lc_count = sum(1 for f in report.findings if f.surface == "location_changed")
    out.append(
        "  1. Runtime removal: COMPLETE — _transition_facts() removed, strict-off branch removed."
    )
    out.append(
        "  2. Operator waiver: GRANTED — repo-local config clean; release-cycle waived."
    )
    out.append(
        "  3. Parity tests: COMPLETE — all strict-off test functions rewritten or removed."
    )
    out.append(
        f"  4. Inventory: COMPLETE — transition_from_previous ({tfp_count} refs) reclassified"
        " as removed_by_adr_0068."
    )
    out.append(
        "  5. ADR-0068: ACCEPTED — see docs/ADR/adr-0068-remove-narrator-strict-off-transition-rollback.md."
    )
    out.append("")
    out.append("  OVERALL ADR-0068 STATUS: EXECUTED AND ACCEPTED.")
    out.append("  transition_from_previous remaining hits are doc/test-historical or")
    out.append("  location_changed W5 mirror (separate substrate keep, unrelated to rollback).")
    out.append("")
    forbidden_keys = (
        "forbidden_ai_stack_actor_situation",
        "forbidden_ai_stack_w5_actor_situation",
    )
    allowed_forbidden_reference_paths = {
        "docs/MVPs/w5_legacy_consumer_removal_inventory.md",
        "docs/MVPs/w5_actor_tracking_migration.md",
        "scripts/inventory_w5_legacy_consumers.py",
        "tests/test_inventory_w5_legacy_consumers.py",
    }
    forbidden = [
        f
        for f in report.findings
        if f.surface in forbidden_keys and f.path not in allowed_forbidden_reference_paths
    ]
    if forbidden:
        out.append("WARNING — forbidden package references detected:")
        for f in forbidden:
            out.append(f"  {f.path}:{f.line}: {f.text[:200]}")
    else:
        out.append("OK — no active forbidden package references detected.")
    out.append("")
    out.append("Phase 6B-9/6B-10/6B-11/6B-12 — ADR-0069 ACCEPTED (2026-05-29):")
    out.append("  viewer_room_id/current_room/current_room_id: deprecated public client aliases; kept for the client migration window.")
    out.append("  w5_player_view: public W5 player-shell authority; migrated in Phase 6B-1.")
    out.append("  world-engine/app/web/static/app.js currentRoom(): upgraded to W5-first.")
    out.append("  WS RuntimeSnapshot w5_player_view gap: CLOSED in Phase 6B-10.")
    out.append("  Production WS w5_player_view population: COMPLETE in Phase 6B-11.")
    out.append("  Deprecation metadata + one-time client fallback warnings: COMPLETE in Phase 6B-12.")
    out.append("  RuntimeSnapshot.viewer_room_id + .current_room: compat alias comments added; aliases not removed.")
    _6b9_keys = ("current_room", "current_room_id", "viewer_room_id", "w5_player_view")
    for key in _6b9_keys:
        count = sum(1 for f in report.findings if f.surface == key)
        label = PHASE_6B4_CLASSIFICATION.get(key, "—")
        out.append(f"  {key:48s} {count:3d}  {label[:70]}")
    out.append("")
    out.append("Phase 6B-13 — alias usage telemetry + client-readiness gate:")
    readiness = phase_6b13_readiness_report()
    for key in (
        "public_aliases_still_emitted",
        "w5_player_view_authority_present",
        "frontend_helpers_prefer_w5",
        "legacy_fallback_still_tested",
        "internal_alias_authority_consumers",
        "docs_describe_aliases_as_primary",
        "removal_ready",
        "reason",
    ):
        out.append(f"  {key}: {readiness[key]}")
    out.append("  removal gate: NON-FAILING — alias removal remains blocked pending client readiness evidence.")
    out.append("")
    out.append("Phase 6C-0 — narrator consequence / sensory location-framing inventory:")
    phase_6c0_rows = phase_6c0_location_framing_inventory()
    counts_by_classification: dict[str, int] = {}
    for row in phase_6c0_rows:
        classification = str(row.get("classification") or "unknown_needs_runtime_trace")
        counts_by_classification[classification] = counts_by_classification.get(classification, 0) + 1
    for classification, count in sorted(counts_by_classification.items()):
        out.append(f"  {classification:36s} {count:3d}")
    plan = phase_6c0_implementation_plan()
    out.append(f"  ADR: {plan['adr']}")
    out.append(
        "  runtime implementation in 6C-0: "
        f"{plan['runtime_implementation_in_phase_6c0']}"
    )
    out.append(f"  proposed helper module: {plan['proposed_helper_module']}")
    out.append("  migration gate: NON-FAILING — implementation deferred to a dedicated phase.")
    out.append("")
    out.append("Phase 6C-1 — W5 location-framing helper + additive integration:")
    phase_6c1 = phase_6c1_location_framing_report()
    for key in (
        "helper_module",
        "helper_schema_version",
        "typed_coercion_required",
        "raw_w5_history_emitted",
        "how_first_class",
        "inferred_why_soft_truth",
        "legacy_fallback_retained",
        "public_aliases_removed",
        "substrate_fields_removed",
        "default_graph_synthesizes_w5_location_framing",
    ):
        out.append(f"  {key}: {phase_6c1[key]}")
    out.append("  additive integration points:")
    for path in phase_6c1["additive_integration_points"]:
        out.append(f"    - {path}")
    out.append("  removal gate: NON-FAILING — no current_area/from_area/to_area removal in 6C-1.")
    out.append("")
    out.append("Phase 6C-2 — graph-owned W5 location-framing synthesis:")
    phase_6c2 = phase_6c2_location_framing_report()
    for key in (
        "graph_owned_synthesis",
        "synthesis_point",
        "synthesis_symbol",
        "state_field",
        "source",
        "typed_coercion_required",
        "raw_w5_history_emitted",
        "committed_events_mutated",
        "legacy_fallback_retained",
        "current_area_from_area_to_area_removed",
        "public_aliases_removed",
        "substrate_fields_removed",
        "default_authority_switch_complete",
    ):
        out.append(f"  {key}: {phase_6c2[key]}")
    out.append("  diagnostics: " + ", ".join(phase_6c2["diagnostics"]))
    out.append("  removal gate: NON-FAILING — parity proven for helper paths; authority switch deferred.")
    out.append("")
    out.append("Phase 6C-3 — W5-first location-framing authority switch:")
    phase_6c3 = phase_6c3_location_framing_authority_report()
    for key in (
        "w5_first_authority_switch",
        "authority_surface",
        "narrator_consequence_surface",
        "sensory_context_surface",
        "valid_w5_authority_condition",
        "legacy_fallback_retained",
        "current_area_from_area_to_area_removed",
        "public_aliases_removed",
        "substrate_fields_removed",
        "committed_events_mutated",
        "next_phase",
    ):
        out.append(f"  {key}: {phase_6c3[key]}")
    out.append("  diagnostics: " + ", ".join(phase_6c3["diagnostics"]))
    out.append("  removal gate: NON-FAILING — no legacy field removal in 6C-3.")
    out.append("")
    out.append("Phase 6C-4 — post-authority inventory and cleanup plan:")
    phase_6c4_plan = phase_6c4_cleanup_plan()
    phase_6c4_summary = phase_6c4_classification_summary()
    for classification, count in phase_6c4_summary.items():
        out.append(f"  {classification:36s} {count:3d}")
    for key in (
        "runtime_legacy_field_removal_in_phase_6c4",
        "next_phase",
    ):
        out.append(f"  {key}: {phase_6c4_plan[key]}")
    out.append(
        "  required evidence: "
        + "; ".join(phase_6c4_plan["required_evidence_before_removal_adr"])
    )
    out.append("  removal gate: NON-FAILING — inventory and cleanup planning only.")
    out.append("")
    out.append("This report is informational; the authoritative inventory and")
    out.append("classification live in docs/MVPs/w5_legacy_consumer_removal_inventory.md.")
    return "\n".join(out)


def _reconfigure_stdout_utf8() -> None:
    """Best-effort: force stdout to UTF-8 so non-ASCII findings can be printed
    on Windows consoles whose default code page is cp1252."""
    reconfigure = getattr(sys.stdout, "reconfigure", None)
    if callable(reconfigure):
        try:
            reconfigure(encoding="utf-8", errors="replace")
        except (OSError, ValueError):
            pass


def main(argv: list[str] | None = None) -> int:
    _reconfigure_stdout_utf8()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        default=str(Path(__file__).resolve().parents[1]),
        help="Repository root to scan (default: repository root inferred from this script).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit a JSON report instead of a human-readable summary.",
    )
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    report = scan(root)
    if args.json:
        payload = {
            "root": report.root,
            "files_scanned": report.files_scanned,
            "files_skipped": report.files_skipped,
            "files_with_findings": report.files_with_findings(),
            "total_findings": len(report.findings),
            "counts_by_surface": report.by_surface(),
            "phase_6b13_readiness": phase_6b13_readiness_report(),
            "phase_6c0_location_framing_inventory": phase_6c0_location_framing_inventory(),
            "phase_6c0_implementation_plan": phase_6c0_implementation_plan(),
            "phase_6c1_location_framing": phase_6c1_location_framing_report(),
            "phase_6c2_location_framing": phase_6c2_location_framing_report(),
            "phase_6c3_location_framing_authority": phase_6c3_location_framing_authority_report(),
            "phase_6c4_post_authority_inventory": phase_6c4_post_authority_inventory(),
            "phase_6c4_classification_summary": phase_6c4_classification_summary(),
            "phase_6c4_cleanup_plan": phase_6c4_cleanup_plan(),
            "findings": [f.to_dict() for f in report.findings],
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(_format_human(report))
    return 0


if __name__ == "__main__":
    sys.exit(main())
