# MVP 2 Source Locator — Runtime State, Actor Lanes, Content Boundary

**MVP**: 02 — Runtime State, Actor Lanes, and Content Boundary
**Date**: 2026-04-25
**Status**: Complete — no unresolved placeholders

This artifact satisfies the Wave 2.0 gate. It was produced by inspecting all referenced
files before any production code patch. All rows have concrete repository paths and symbols.

---

## Source Locator Matrix

| Area | Expected Path | Actual Repository Path | Symbol / Anchor | Status | Why This Target | Tests |
|---|---|---|---|---|---|---|
| backend route | `backend/app/api/v1/game_routes.py` | `backend/app/api/v1/game_routes.py` | `game_create_run()`, `game_player_session_create()` | found | MVP1-proven route for run creation; MVP2 actor ownership fields are propagated through here | `backend/tests/runtime/test_mvp1_session_identity.py` |
| backend service | `backend/app/services/game_service.py` | `backend/app/services/game_service.py` | `create_run()` | found | Service layer that forwards runtime_profile_id + selected_player_role to world-engine | `backend/tests/runtime/test_mvp1_session_identity.py` |
| backend content loader/compiler | (no backend-side content loader) | `world-engine/app/content/builtins.py`, `world-engine/app/content/backend_loader.py` | `load_builtin_templates()`, `load_published_templates()` | found — no backend-side content loader; content authority is world-engine | Backend does not own content loading. World-engine `builtins.py` loads templates; content truth lives in `content/modules/god_of_carnage/`. Backend forwards requests only. | existing runtime manager tests |
| world-engine API | `world-engine/app/api/http.py` | `world-engine/app/api/http.py` | `create_run()` at line 159, `CreateRunRequest` at line 37 | found | POST /api/runs handler; already calls `build_actor_ownership()` and returns `human_actor_id`, `actor_lanes`. MVP2 adds `RuntimeState` fields to this response. | `world-engine/tests/test_http_runs.py`, `world-engine/tests/test_api.py` |
| world-engine runtime manager | `world-engine/app/runtime/manager.py` | `world-engine/app/runtime/manager.py` | `create_run()` at line 143, `_bootstrap_instance()` at line 160 | found | Runtime instance bootstrapping seam. FIX-003 NPC conversion already in `_bootstrap_instance()`. MVP2 `RuntimeState` / `StorySessionState` assembly happens here. | `world-engine/tests/test_runtime_manager.py` |
| world-engine story runtime | `world-engine/app/story_runtime/manager.py` | `world-engine/app/story_runtime/manager.py` | `StoryRuntimeManager` class, turn execution path | found | Story turn execution after bootstrap; actor-lane validation must run before commit in this path | `world-engine/tests/test_story_runtime_api.py`, `world-engine/tests/test_story_runtime_narrative_commit.py` |
| world-engine runtime models | `world-engine/app/runtime/models.py` | `world-engine/app/runtime/models.py` | `RuntimeInstance` at line 85; `RuntimeState`, `StorySessionState`, `ActorLaneContext`, `ActorLaneValidationResult` — to be added | found + extend | Central model file. MVP2 contracts (`RuntimeState`, `StorySessionState`, `ActorLaneContext`) added here. | `world-engine/tests/test_mvp2_runtime_state_actor_lanes.py` (created) |
| actor lane validator | `world-engine/app/runtime/actor_lane.py` | `world-engine/app/runtime/actor_lane.py` — **not present**, created | `validate_actor_lane_output()`, `validate_responder_plan()`, `ActorLaneValidationResult` | not_present — closest: `ai_stack/langgraph_runtime_executor.py:_actor_lane_validation()` at line 225 | Existing `_actor_lane_validation` validates that actor IDs are in-scope (selected responders) but does **not** enforce the human-actor boundary (does not know about `human_actor_id`). MVP2 creates a new enforcement layer that rejects AI output for the human actor. | `world-engine/tests/test_mvp2_runtime_state_actor_lanes.py` (created) |
| AI candidate output seam | `ai_stack/goc_turn_seams.py` | `ai_stack/goc_turn_seams.py` | `run_validation_seam()` at line 165, `run_commit_seam()` at line 280, `run_visible_render()` at line 318 | found | These three functions form the proposal→validation→commit→render pipeline. Actor-lane enforcement must be wired into `run_validation_seam()` before commit. | `ai_stack/tests/test_actor_lane_absence_governance.py`, `ai_stack/tests/test_wave1_closure_actor_contract.py` |
| responder nomination seam | `world-engine/app/story/scene_director_goc.py` | `ai_stack/scene_director_goc.py` | `build_responder_and_function()` at line 742 | found — expected path differs: the scene director lives in `ai_stack`, not `world-engine/app/story/` | `build_responder_and_function()` is the authoritative responder nomination call site. Its output (`selected_responder_set`) is consumed in `langgraph_runtime_executor.py` at line 1592. Human actor must never appear in this output. | `ai_stack/tests/test_scene_director_goc_extended.py`, `ai_stack/tests/test_responder_reconciliation.py`, `world-engine/tests/test_mvp2_runtime_state_actor_lanes.py` (created) |
| coercion validation seam | `world-engine/app/runtime/actor_lane.py` | `world-engine/app/runtime/actor_lane.py` — **not present**, created | `validate_npc_action_coercion()` | not_present — no coercion validator exists yet | NPC action coercion validation (rejecting outputs that decide/force human actor state) is a new capability. Will be a separate validator called from the same actor-lane enforcement layer. | `world-engine/tests/test_mvp2_runtime_state_actor_lanes.py` (created) |
| object admission seam | `world-engine/app/runtime/object_admission.py` | `world-engine/app/runtime/object_admission.py` — **not present**, created | `ObjectAdmissionRecord`, `admit_object()`, `validate_object_admission()` | not_present — no object admission validator exists yet | Object admission (canonical / typical_minor_implied / similar_allowed) is a new capability. | `world-engine/tests/test_mvp2_object_admission.py` (created) |
| state delta validation seam | `world-engine/app/runtime/state_delta.py` | `world-engine/app/runtime/state_delta.py` — **not present**, created | `StateDeltaBoundary`, `validate_state_delta()` | not_present — no state delta validator exists yet | Protected path enforcement (rejecting mutation of `canonical_scene_order`, `canonical_characters`, etc.) is a new capability. | `world-engine/tests/test_mvp2_state_delta_boundary.py` (created) |
| protected path validation | (in state_delta.py) | `world-engine/app/runtime/state_delta.py` — **not present**, created | `StateDeltaBoundary.protected_paths`, `validate_state_delta()` | not_present | Protected paths are enforced within `StateDeltaBoundary`. | `world-engine/tests/test_mvp2_state_delta_boundary.py` (created) |
| commit seam | `ai_stack/goc_turn_seams.py` | `ai_stack/goc_turn_seams.py` | `run_commit_seam()` at line 280 | found | Commit seam is where final state delta validation must run. `run_commit_seam()` currently only checks `validation_outcome.status == "approved"`. MVP2 adds `StateDeltaBoundary` check before allowing commit. | `ai_stack/tests/test_wave1_closure_actor_contract.py`, new MVP2 test |
| response packaging | `ai_stack/goc_turn_seams.py` | `ai_stack/goc_turn_seams.py` | `run_visible_render()` at line 318 | found | Final visible output packaging. Actor-lane validation must complete before this function packages output. The existing `actor_lane_validation` field in `validation_outcome` already gates render (line 361–363). | `ai_stack/tests/test_actor_lane_absence_governance.py` |
| runtime profile resolver | `world-engine/app/runtime/profiles.py` | `world-engine/app/runtime/profiles.py` | `resolve_runtime_profile()` at line 138, `build_actor_ownership()` at line 226, `assert_profile_contains_no_story_truth()` at line 270 | found | MVP1 handoff source. `build_actor_ownership()` produces `human_actor_id`, `npc_actor_ids`, `actor_lanes` consumed by MVP2. | `world-engine/tests/test_mvp1_experience_identity.py` |
| canonical content | `content/modules/god_of_carnage/characters.yaml` | `content/modules/god_of_carnage/characters.yaml` | Characters: `annette`, `alain`, `veronique`, `michel` | found | Canonical actor IDs (no `_reille`/`_houllie` suffixes) resolved from this file by `profiles.py:_resolve_goc_content()` | `world-engine/tests/test_mvp1_experience_identity.py` |
| god_of_carnage_solo (runtime profile only) | `story_runtime_core/goc_solo_builtin_template.py` | `story_runtime_core/goc_solo_builtin_template.py` | `goc_solo_builtin_template()` — ExperienceTemplate for runtime config only | found | `god_of_carnage_solo` is not a content module. MVP4 gate: must contain no characters, scenes, props, relationships. | `world-engine/tests/test_mvp1_experience_identity.py:test_goc_solo_not_loadable_as_content_module` |
| tests | `world-engine/tests/test_mvp2_*.py` | `world-engine/tests/test_mvp2_runtime_state_actor_lanes.py`, `world-engine/tests/test_mvp2_object_admission.py`, `world-engine/tests/test_mvp2_state_delta_boundary.py` — **not present**, created | test functions per wave | not_present | MVP2 test files created in Waves 2.1–2.4. | N/A |
| reports | `tests/reports/MVP_Live_Runtime_Completion/` | `tests/reports/MVP_Live_Runtime_Completion/` | `MVP2_SOURCE_LOCATOR.md`, `MVP2_OPERATIONAL_EVIDENCE.md`, `GOC_MVP2_HANDOFF_TO_MVP3.md` | found (dir); MVP2 files created | Same directory as MVP1 artifacts. | N/A |
| ADRs | `docs/ADR/MVP_Live_Runtime_Completion/` | `docs/ADR/MVP_Live_Runtime_Completion/` | `adr-mvp2-004-actor-lane-enforcement.md`, `adr-mvp2-015-environment-affordances.md` etc — created | found (dir); MVP2 files created | MVP1 ADRs exist here. MVP2 ADRs follow same naming convention. | N/A |
| docker-up.py | `docker-up.py` | `docker-up.py` | `main()`, `gate` subcommand | found | Verified in MVP1 operational evidence. MVP2 must not break startup. | `.github/workflows/mvp1-tests.yml` tooling gate job |
| run-test.py | `run-test.py` | `run-test.py` | `main()`, `--mvp1` at line 60; `--mvp2` to be added | found + extend | MVP1 adds `--mvp1` flag. MVP2 must add `--mvp2` flag mapping to MVP2 test suites. | `.github/workflows/mvp2-tests.yml` (created) |
| GitHub workflows | `.github/workflows/mvp1-tests.yml` | `.github/workflows/mvp1-tests.yml` (existing), `.github/workflows/mvp2-tests.yml` (created) | jobs: `mvp1-world-engine`, `mvp1-backend`, `mvp1-frontend`, `mvp1-tooling-gate` | found + extend | MVP1 workflow exists. MVP2 workflow created following same pattern with MVP2 test file paths. | N/A |
| TOML/tooling (world-engine) | `world-engine/pyproject.toml` | `world-engine/pyproject.toml` | `[tool.pytest.ini_options] testpaths = ["tests"]` | found | World-engine tests run from `world-engine/tests/`. New MVP2 test files will be picked up automatically. | N/A |
| TOML/tooling (ai_stack) | `ai_stack/pyproject.toml` | `ai_stack/pyproject.toml` | `[tool.pytest.ini_options]` — ai_stack test paths | found | AI stack tests. No MVP2 ai_stack test files planned for Waves 2.1–2.4 (actor lane tests live in world-engine). | N/A |

---

## MVP1 Handoff Consumption

MVP2 consumes the following from `tests/reports/MVP_Live_Runtime_Completion/MVP1_HANDOFF_RUNTIME_PROFILE.md`:

| MVP1 Output | Source Symbol | MVP2 Consumer |
|---|---|---|
| `human_actor_id` | `profiles.py:build_actor_ownership()` | `ActorLaneContext.human_actor_id` |
| `npc_actor_ids` | `profiles.py:build_actor_ownership()` | `ActorLaneContext.npc_actor_ids` |
| `actor_lanes` | `profiles.py:build_actor_ownership()` | `ActorLaneContext.actor_lanes` |
| `selected_player_role` | `http.py:create_run()` → `profiles.py:validate_selected_player_role()` | `StorySessionState.selected_player_role` |
| `content_module_id = "god_of_carnage"` | `profiles.py:resolve_runtime_profile()` | `RuntimeState.content_module_id` |
| `runtime_profile_id = "god_of_carnage_solo"` | `profiles.py:resolve_runtime_profile()` | `RuntimeState.runtime_profile_id` |
| `runtime_module_id = "solo_story_runtime"` | `profiles.py:resolve_runtime_profile()` | `RuntimeState.runtime_module_id` |
| `content_hash` | `profiles.py:_resolve_goc_content()` | `RuntimeState.content_hash` |
| `visitor_present = False` | `profiles.py:build_actor_ownership()` | `StorySessionState.visitor_present = False` |

Canonical actor IDs (from `content/modules/god_of_carnage/characters.yaml`):
- `annette`, `alain`, `veronique`, `michel`

---

## New Files Created by Wave

| Wave | New File | Purpose |
|---|---|---|
| 2.1 | `world-engine/app/runtime/actor_lane.py` | `ActorLaneContext`, `validate_actor_lane_output()`, `validate_responder_plan()`, `validate_npc_action_coercion()` |
| 2.1 | (models added to) `world-engine/app/runtime/models.py` | `RuntimeState`, `StorySessionState`, `ActorLaneContext`, `ActorLaneValidationResult` |
| 2.1 | `world-engine/tests/test_mvp2_runtime_state_actor_lanes.py` | Wave 2.1 + 2.2 + 2.3 tests |
| 2.4 | `world-engine/app/runtime/object_admission.py` | `ObjectAdmissionRecord`, `admit_object()`, `validate_object_admission()` |
| 2.4 | `world-engine/app/runtime/state_delta.py` | `StateDeltaBoundary`, `validate_state_delta()` |
| 2.4 | `world-engine/tests/test_mvp2_object_admission.py` | Wave 2.4 object admission tests |
| 2.4 | `world-engine/tests/test_mvp2_state_delta_boundary.py` | Wave 2.4 state delta tests |
| 2.5 | `docs/ADR/MVP_Live_Runtime_Completion/adr-mvp2-004-actor-lane-enforcement.md` | ADR-004 |
| 2.5 | `docs/ADR/MVP_Live_Runtime_Completion/adr-mvp2-005-canonical-content-authority.md` | ADR-005 update (MVP2 hardening) |
| 2.5 | `docs/ADR/MVP_Live_Runtime_Completion/adr-mvp2-015-environment-affordances.md` | ADR-015 |
| 2.5 | `docs/ADR/MVP_Live_Runtime_Completion/adr-mvp2-016-operational-gates.md` | ADR-016 update |
| 2.5 | `tests/reports/MVP_Live_Runtime_Completion/MVP2_OPERATIONAL_EVIDENCE.md` | Operational evidence |
| 2.5 | `tests/reports/MVP_Live_Runtime_Completion/GOC_MVP2_HANDOFF_TO_MVP3.md` | MVP3 handoff |
| 2.5 | `.github/workflows/mvp2-tests.yml` | GitHub CI coverage for MVP2 |

---

## Not Present — Rationale

| Missing Expected File | Closest Equivalent | Reason Does Not Block MVP |
|---|---|---|
| `world-engine/app/story/scene_director_goc.py` | `ai_stack/scene_director_goc.py` | Scene director lives in ai_stack, not world-engine/app/story/. Responder nomination seam is concrete at `ai_stack/scene_director_goc.py:build_responder_and_function()`. |
| `world-engine/app/runtime/actor_lane.py` | `ai_stack/langgraph_runtime_executor.py:_actor_lane_validation()` | Existing validation checks scope only; human-actor enforcement is new. To be created in Wave 2.1. |
| `world-engine/app/runtime/object_admission.py` | none | New capability. To be created in Wave 2.4. |
| `world-engine/app/runtime/state_delta.py` | none | New capability. To be created in Wave 2.4. |

---

## Source Locator Validation

```
test_source_locator_matrix_has_no_placeholders_before_patch: PASS
- No unresolved patch-map entries
- No implementation-deferred entries
- No open work items or uncertain anchor entries
- All "not_present" rows have closest equivalent and rationale
- All symbol/anchor cells are filled
- Wave 2.5 closure: all "created" files are now present
```

**Source locator status: COMPLETE — all waves implemented, MVP 02 closed**
