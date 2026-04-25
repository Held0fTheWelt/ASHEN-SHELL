# MVP 2 Handoff to MVP 3

**From**: MVP 2 — Runtime State, Actor Lanes, and Content Boundary
**To**: MVP 3 — Live Dramatic Scene Simulator (LDSS)
**Date**: 2026-04-25

MVP 3 must not rediscover any decision made in MVP 2. This document is the authoritative
handoff surface.

---

## Runtime State Provenance

### RuntimeState contract

```json
{
  "contract": "runtime_state.v1",
  "state_version": "runtime_state.goc_solo.v1",
  "story_session_id": "<uuid>",
  "run_id": "<uuid>",
  "content_module_id": "god_of_carnage",
  "content_hash": "sha256:<16-char-hex>",
  "runtime_profile_id": "god_of_carnage_solo",
  "runtime_profile_hash": "sha256:not-computed",
  "runtime_module_id": "solo_story_runtime",
  "runtime_module_hash": "sha256:not-computed",
  "current_scene_id": "phase_1",
  "selected_player_role": "annette",
  "human_actor_id": "annette",
  "actor_lanes": {
    "annette": "human",
    "alain": "npc",
    "veronique": "npc",
    "michel": "npc"
  },
  "admitted_objects": []
}
```

**Source**: `world-engine/app/runtime/models.py:RuntimeState`
**Builder**: `world-engine/app/runtime/actor_lane.py:build_runtime_state()`

---

## Story Session State

### StorySessionState contract

```json
{
  "contract": "story_session_state.v1",
  "story_session_id": "<uuid>",
  "run_id": "<uuid>",
  "turn_number": 0,
  "content_module_id": "god_of_carnage",
  "runtime_profile_id": "god_of_carnage_solo",
  "runtime_module_id": "solo_story_runtime",
  "current_scene_id": "phase_1",
  "selected_player_role": "annette",
  "human_actor_id": "annette",
  "npc_actor_ids": ["alain", "veronique", "michel"],
  "visitor_present": false
}
```

**Source**: `world-engine/app/runtime/models.py:StorySessionState`
**Builder**: `world-engine/app/runtime/actor_lane.py:build_story_session_state()`

---

## ActorLaneContext

### ActorLaneContext contract

```json
{
  "contract": "actor_lane_context.v1",
  "content_module_id": "god_of_carnage",
  "runtime_profile_id": "god_of_carnage_solo",
  "selected_player_role": "annette",
  "human_actor_id": "annette",
  "actor_lanes": {
    "annette": "human",
    "alain": "npc",
    "veronique": "npc",
    "michel": "npc"
  },
  "ai_allowed_actor_ids": ["alain", "michel", "veronique"],
  "ai_forbidden_actor_ids": ["annette"]
}
```

**Source**: `world-engine/app/runtime/models.py:ActorLaneContext`
**Builder**: `world-engine/app/runtime/actor_lane.py:build_actor_lane_context()`
**Input**: MVP1 `build_actor_ownership()` output from `world-engine/app/runtime/profiles.py`

### For Alain start:

```json
{
  "human_actor_id": "alain",
  "ai_allowed_actor_ids": ["annette", "michel", "veronique"],
  "ai_forbidden_actor_ids": ["alain"]
}
```

---

## human_actor_id

- Type: `str`
- Value: canonical actor ID from `content/modules/god_of_carnage/characters.yaml`
- For annette start: `"annette"`
- For alain start: `"alain"`
- Never: `"visitor"` or any non-canonical ID
- Source: `profiles.py:build_actor_ownership()` → `actor_lane.py:build_actor_lane_context()`

---

## npc_actor_ids

- Type: `list[str]`
- For annette start: `["alain", "veronique", "michel"]`
- For alain start: `["annette", "veronique", "michel"]`
- All canonical GoC actors not selected by the player
- Canonical actor IDs: `annette`, `alain`, `veronique`, `michel` (no `_reille`/`_houllie` suffixes)

---

## actor_lanes

- Type: `dict[str, str]` mapping actor_id → `"human"` | `"npc"`
- Exactly one actor has lane `"human"` — the selected player
- All others have lane `"npc"`
- `"visitor"` never appears

---

## ai_allowed_actor_ids / ai_forbidden_actor_ids

- `ai_allowed_actor_ids`: sorted list of NPC actor IDs — AI may generate output for these
- `ai_forbidden_actor_ids`: list containing only `human_actor_id` — AI must not generate output for these
- These are always disjoint

---

## Content Projection Rules

- **Canonical content module**: `god_of_carnage` at `content/modules/god_of_carnage/`
- **Runtime profile**: `god_of_carnage_solo` — profile-only, no story truth
- **Runtime module**: `solo_story_runtime` — scaffolding only, `beats=[], props=[], actions=[]`
- MVP3 LDSS must read characters, scenes, escalation, relationships from `content/modules/god_of_carnage/`
- MVP3 must not invent canonical story truth at runtime

---

## Object Admission Rules

```json
{
  "canonical_content": {
    "commit_allowed": true,
    "temporary_scene_staging": false,
    "requires_similarity_reason": false
  },
  "typical_minor_implied": {
    "commit_allowed": false,
    "temporary_scene_staging": true,
    "requires_similarity_reason": false
  },
  "similar_allowed": {
    "commit_allowed": false,
    "temporary_scene_staging": false,
    "requires_similarity_reason": true
  }
}
```

**Source**: `world-engine/app/runtime/object_admission.py:admit_object()`
**Error codes**: `object_source_kind_required`, `environment_object_not_admitted`, `similar_allowed_requires_similarity_reason`

---

## StateDeltaBoundary

```json
{
  "contract": "state_delta_boundary.v1",
  "protected_paths": [
    "canonical_scene_order",
    "canonical_characters",
    "canonical_relationships",
    "canonical_content_truth",
    "canonical_props",
    "canonical_endings",
    "content_module_id",
    "selected_player_role",
    "human_actor_id",
    "actor_lanes"
  ],
  "allowed_runtime_paths": [
    "runtime_flags",
    "turn_memory",
    "scene_pressure",
    "admitted_objects",
    "relationship_runtime_pressure"
  ],
  "reject_unknown_paths": true
}
```

**Source**: `world-engine/app/runtime/models.py:StateDeltaBoundary`
**Validator**: `world-engine/app/runtime/state_delta.py:validate_state_delta()`
**Commit enforcement**: `ai_stack/goc_turn_seams.py:run_commit_seam()` with `candidate_deltas`

---

## Actor-Lane Validation Error Codes

| Error Code | Trigger | Enforced At |
|---|---|---|
| `ai_controlled_human_actor` | AI line/action/emotion/decision for human actor | `validate_actor_lane_output()`, `run_validation_seam()` |
| `human_actor_selected_as_responder` | Human actor as primary or secondary responder | `validate_responder_plan()`, `run_validation_seam()` |
| `invalid_visitor_runtime_reference` | Visitor appears in actor lanes or responder plan | `build_actor_lane_context()`, `validate_actor_lane_output()`, `validate_responder_plan()` |
| `actor_lane_validation_too_late` | Validation called after commit | `validate_actor_lane_output()` |
| `actor_lane_missing_human_actor` | No human actor in actor_lanes | (bootstrap validation — MVP3 adds live path) |

---

## Coercion Validation Error Codes

| Error Code | Trigger | Enforced At |
|---|---|---|
| `npc_action_controls_human_actor` | NPC forces/decides/assigns human outcome | `validate_npc_action_coercion()` |
| `protected_state_mutation_rejected` | Delta targets a protected path | `validate_state_delta()`, `run_commit_seam()` |
| `state_delta_boundary_violation` | Delta targets unknown non-allowed path | `validate_state_delta()` |

---

## Object Admission Error Codes

| Error Code | Trigger | Enforced At |
|---|---|---|
| `object_source_kind_required` | Missing or invalid source_kind | `admit_object()` |
| `environment_object_not_admitted` | Major/dangerous object without canonical backing | `admit_object()` |
| `similar_allowed_requires_similarity_reason` | similar_allowed without similarity_reason | `admit_object()` |
| `runtime_profile_contains_story_truth` | Profile dict contains story truth fields | `assert_profile_contains_no_story_truth()` |
| `runtime_module_contains_story_truth` | Template owns beats/props/actions | `assert_runtime_module_contains_no_story_truth()` |

---

## Tests Proving Enforcement

| Test | Wave | File | Status |
|---|---|---|---|
| `test_actor_lane_context_created_for_annette_start` | 2.1 | test_mvp2_runtime_state_actor_lanes.py | PASS |
| `test_actor_lane_context_created_for_alain_start` | 2.1 | test_mvp2_runtime_state_actor_lanes.py | PASS |
| `test_selected_actor_is_human` | 2.1 | test_mvp2_runtime_state_actor_lanes.py | PASS |
| `test_non_selected_canonical_actors_are_npcs` | 2.1 | test_mvp2_runtime_state_actor_lanes.py | PASS |
| `test_runtime_state_contains_source_provenance` | 2.1 | test_mvp2_runtime_state_actor_lanes.py | PASS |
| `test_actor_lane_context_uses_mvp1_handoff` | 2.1 | test_mvp2_runtime_state_actor_lanes.py | PASS |
| `test_actor_lane_context_excludes_visitor` | 2.1 | test_mvp2_runtime_state_actor_lanes.py | PASS |
| `test_ai_cannot_speak_for_human_actor` | 2.2 | test_mvp2_runtime_state_actor_lanes.py | PASS |
| `test_ai_cannot_act_for_human_actor` | 2.2 | test_mvp2_runtime_state_actor_lanes.py | PASS |
| `test_ai_cannot_assign_human_actor_emotion` | 2.2 | test_mvp2_runtime_state_actor_lanes.py | PASS |
| `test_ai_cannot_decide_for_human_actor` | 2.2 | test_mvp2_runtime_state_actor_lanes.py | PASS |
| `test_human_actor_cannot_be_primary_responder` | 2.2 | test_mvp2_runtime_state_actor_lanes.py | PASS |
| `test_human_actor_cannot_be_secondary_responder` | 2.2 | test_mvp2_runtime_state_actor_lanes.py | PASS |
| `test_visitor_cannot_be_responder` | 2.2 | test_mvp2_runtime_state_actor_lanes.py | PASS |
| `test_actor_lane_validation_runs_before_response_packaging` | 2.2 | test_mvp2_runtime_state_actor_lanes.py | PASS |
| `test_npc_action_cannot_force_human_response` | 2.3 | test_mvp2_npc_coercion_state_delta.py | PASS |
| `test_npc_action_can_pressure_human_without_control` | 2.3 | test_mvp2_npc_coercion_state_delta.py | PASS |
| `test_ai_delta_cannot_change_selected_player_role` | 2.3 | test_mvp2_npc_coercion_state_delta.py | PASS |
| `test_ai_delta_cannot_change_human_actor_id` | 2.3 | test_mvp2_npc_coercion_state_delta.py | PASS |
| `test_ai_delta_cannot_mutate_actor_lanes` | 2.3 | test_mvp2_npc_coercion_state_delta.py | PASS |
| `test_commit_seam_rejects_protected_state_mutation` | 2.3 | test_mvp2_npc_coercion_state_delta.py | PASS |
| `test_canonical_object_admitted` | 2.4 | test_mvp2_object_admission.py | PASS |
| `test_typical_minor_object_admitted_as_temporary` | 2.4 | test_mvp2_object_admission.py | PASS |
| `test_similar_allowed_requires_similarity_reason` | 2.4 | test_mvp2_object_admission.py | PASS |
| `test_unadmitted_plausible_object_rejected` | 2.4 | test_mvp2_object_admission.py | PASS |
| `test_major_plot_changing_object_rejected` | 2.4 | test_mvp2_object_admission.py | PASS |
| `test_runtime_profile_contains_no_story_truth` | 2.4 | test_mvp2_object_admission.py | PASS |
| `test_runtime_module_contains_no_goc_story_truth` | 2.4 | test_mvp2_object_admission.py | PASS |
| `test_god_of_carnage_solo_does_not_define_characters_scenes_props_or_plot_truth` | 2.4 | test_mvp2_object_admission.py | PASS |

---

## Source Locator Evidence

`tests/reports/MVP_Live_Runtime_Completion/MVP2_SOURCE_LOCATOR.md`

## Operational Evidence Path

`tests/reports/MVP_Live_Runtime_Completion/MVP2_OPERATIONAL_EVIDENCE.md`

---

## What MVP 3 Can Assume

1. `ActorLaneContext` is always built from `build_actor_ownership()` — canonical actor IDs only
2. `human_actor_id` is always `"annette"` or `"alain"` — never visitor, never invented
3. `ai_forbidden_actor_ids` always contains exactly the human actor and nothing else
4. `run_validation_seam()` rejects AI output for the human actor when `actor_lane_context` is passed
5. `run_commit_seam()` rejects protected path mutations when `candidate_deltas` is passed
6. `god_of_carnage_solo` template is runtime configuration only — no story truth
7. All canonical story truth lives in `content/modules/god_of_carnage/`
8. Object admission requires explicit `source_kind` — no unadmitted objects enter the runtime
9. `visitor_present` is always `False` — visitor is fully removed from all seams
10. NPC coercion of the human actor is rejected at `validate_npc_action_coercion()` — not a pure string match
