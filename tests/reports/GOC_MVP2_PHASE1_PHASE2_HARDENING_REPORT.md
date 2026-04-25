# GOC MVP2 Phase 1 & Phase 2 Hardening Report

**Date**: 2026-04-25
**Status**: PASS

---

## Files Inspected

- `docs/MVPs/MVP_Live_runtime_Completion/02_runtime_state_actor_lanes_content_boundary.md`
- `tests/reports/MVP_Live_Runtime_Completion/MVP2_SOURCE_LOCATOR.md`
- `tests/reports/MVP_Live_Runtime_Completion/MVP1_HANDOFF_RUNTIME_PROFILE.md`
- `world-engine/app/runtime/actor_lane.py`
- `world-engine/app/runtime/models.py`
- `ai_stack/goc_turn_seams.py`
- `ai_stack/langgraph_runtime_executor.py`
- `ai_stack/langgraph_runtime_state.py`
- `world-engine/app/story_runtime/manager.py`
- `world-engine/app/api/http.py`
- `backend/app/api/v1/session_routes.py`
- `backend/app/content/compiler/compiler.py`
- `world-engine/tests/test_mvp2_runtime_state_actor_lanes.py`

---

## Files Changed

- `ai_stack/langgraph_runtime_state.py` — added `actor_lane_context: dict[str, Any]` to `RuntimeTurnState`
- `ai_stack/langgraph_runtime_executor.py` — added `actor_lane_context` to `run()` signature, `initial_state`, and `_run_validation()` → `run_validation_seam()` call
- `world-engine/app/story_runtime/manager.py` — added `_extract_actor_lane_context()` static method; wired into both `turn_graph.run()` calls (opening + player turn)
- `world-engine/tests/test_mvp2_runtime_state_actor_lanes.py` — added 11 new hardening tests (39 total)
- `tests/reports/GOC_MVP2_SOURCE_LOCATOR.md` — created
- `tests/reports/GOC_MVP2_PHASE1_PHASE2_HARDENING_REPORT.md` — this file

---

## Source Locator Updates

Created `tests/reports/GOC_MVP2_SOURCE_LOCATOR.md` with concrete anchors for:
- ActorLaneContext type and assembly function
- RuntimeTurnState.actor_lane_context field (new)
- RuntimeTurnGraphExecutor.run() actor_lane_context parameter (new)
- StoryRuntimeManager._extract_actor_lane_context() (new)
- All Phase 1 and Phase 2 test locations
- run-test.py, GitHub workflow, TOML entries

---

## Phase 1 Checks

| Check | Result | Notes |
|---|---|---|
| ActorLaneContext exists and is created from MVP1 handoff | PASS | `build_actor_lane_context()` consumes `build_actor_ownership()` output |
| Annette start: human_actor_id = canonical Annette ID | PASS | `test_actor_lane_context_created_for_annette_start` + `test_actor_lane_context_uses_mvp1_handoff` |
| Alain start: human_actor_id = canonical Alain ID | PASS | `test_actor_lane_context_created_for_alain_start` + `test_actor_lane_context_uses_mvp1_handoff_alain_start` (new) |
| Remaining canonical actors = NPC | PASS | `test_non_selected_canonical_actors_are_npcs` |
| ai_forbidden_actor_ids includes human_actor_id | PASS | `test_ai_forbidden_actor_ids_include_human_actor` (canonical name, new) |
| ai_allowed_actor_ids excludes human_actor_id | PASS | `test_ai_allowed_actor_ids_exclude_human_actor` (canonical name, new) |
| visitor absent from actor lanes | PASS | `test_actor_lane_context_excludes_visitor` |
| Actor IDs resolved from canonical content (MVP1 handoff) | PASS | `test_actor_lane_context_uses_mvp1_handoff` + `test_actor_lane_context_uses_mvp1_handoff_alain_start` |
| human_actor_id not nullable in live GoC solo session | PASS | `build_actor_lane_context()` raises if `human_actor_id` absent |

---

## Phase 2 Checks

| Check | Result | Notes |
|---|---|---|
| validate_actor_lane_output() exists | PASS | `world-engine/app/runtime/actor_lane.py:validate_actor_lane_output()` |
| AI cannot speak for human actor | PASS | `test_ai_cannot_speak_for_human_actor` |
| AI cannot act for human actor | PASS | `test_ai_cannot_act_for_human_actor` |
| AI cannot assign emotion to human actor | PASS | `test_ai_cannot_assign_human_actor_emotion` |
| AI cannot decide for human actor | PASS | `test_ai_cannot_decide_for_human_actor` |
| AI cannot move human actor | PASS | `test_ai_cannot_move_human_actor` (new) |
| Human actor cannot be primary responder | PASS | `test_human_actor_cannot_be_primary_responder` |
| Human actor cannot be secondary responder | PASS | `test_human_actor_cannot_be_secondary_responder` |
| Visitor cannot be responder | PASS | `test_visitor_cannot_be_responder` |
| Validation runs before response packaging | PASS | `test_actor_lane_validation_runs_before_response_packaging` |
| Validation runs before commit | PASS | `test_actor_lane_validation_runs_before_commit` (new) |
| actor_lane_context wired into graph execution | PASS | `test_actor_lane_enforcement_active_in_graph_execution` (new) |
| actor_lane_context in RuntimeTurnState | PASS | `test_runtime_turn_state_has_actor_lane_context_field` (new) |
| StoryRuntimeManager extracts context from session | PASS | `test_extract_actor_lane_context_returns_context_with_ownership` (new) |
| Safe degradation when no ownership in session | PASS | `test_extract_actor_lane_context_returns_none_without_ownership` (new) |

---

## False Greens Found and Fixed

### FG-001: ActorLaneContext not consumed by graph execution (CRITICAL)
**Pattern**: `ActorLaneContext exists but is not consumed by AI/runtime seams`
**Finding**: `run_validation_seam()` was called in `langgraph_runtime_executor.py` at line 2293 without `actor_lane_context`. The enforcement was standalone functions that were never reached during graph execution.
**Fix**: 
1. Added `actor_lane_context: dict[str, Any]` to `RuntimeTurnState`
2. Added `actor_lane_context` parameter to `RuntimeTurnGraphExecutor.run()`
3. Wired `state.get("actor_lane_context")` into `run_validation_seam()` call in `_run_validation()`
**Test**: `test_actor_lane_enforcement_active_in_graph_execution`, `test_runtime_turn_state_has_actor_lane_context_field`

### FG-002: StoryRuntimeManager never passes actor_lane_context to graph
**Pattern**: `ActorLaneContext exists but is not consumed by AI/runtime seams`
**Finding**: Both `execute_opening()` and `execute_turn()` in `story_runtime/manager.py` called `turn_graph.run()` without `actor_lane_context`.
**Fix**: Added `_extract_actor_lane_context(session)` static method that reads from `session.runtime_projection`. Both turn execution paths now pass the extracted context.
**Test**: `test_story_runtime_manager_has_extract_actor_lane_context`, `test_extract_actor_lane_context_returns_context_with_ownership`

### FG-003: Missing Alain MVP1 handoff test
**Pattern**: `tests only use static fixtures and never exercise runtime start path` (for Alain)
**Finding**: `test_actor_lane_context_uses_mvp1_handoff` only tested Annette. Alain start via real `build_actor_ownership()` was untested.
**Fix**: Added `test_actor_lane_context_uses_mvp1_handoff_alain_start`

### FG-004: Missing `test_ai_cannot_move_human_actor`
**Pattern**: Required test was absent
**Fix**: Added test with `block_type="movement"` and `block_type="physical_state"`

### FG-005: Missing `test_actor_lane_validation_runs_before_commit`
**Pattern**: Required test was absent (different concern from the packaging test)
**Fix**: Added test proving `commit_applied=False` when validation rejects

### FG-006: Canonical test names missing
**Pattern**: `test_ai_allowed_actor_ids_exclude_human_actor` and `test_ai_forbidden_actor_ids_include_human_actor` existed under slightly different names
**Fix**: Added canonical-named tests

---

## Remaining Blocker

### BLOCKER-001: Backend must pass actor ownership in runtime_projection (integration gap)
**Severity**: Does not block Phase 1/2 hardening; blocks live end-to-end enforcement
**Description**: The backend's `create_story_session()` call does not currently include `human_actor_id`, `npc_actor_ids`, `actor_lanes`, or `selected_player_role` in the `runtime_projection` dict. The `_extract_actor_lane_context()` helper returns `None` for existing sessions, causing enforcement to be safely skipped.
**Required fix**: Backend must extend `runtime_projection` to include actor ownership fields from the `create_run` response when `runtime_profile_id=god_of_carnage_solo` is used.
**This is an MVP3 integration point.** Phase 1/2 hardening proves the enforcement machinery is correct and wired. The backend plumbing is out of scope for MVP2.

---

## Tests Added/Updated

| Test | Type | Phase |
|---|---|---|
| `test_ai_allowed_actor_ids_exclude_human_actor` | new (canonical name) | Phase 1 |
| `test_ai_forbidden_actor_ids_include_human_actor` | new (canonical name) | Phase 1 |
| `test_actor_lane_context_uses_mvp1_handoff_alain_start` | new | Phase 1 |
| `test_ai_cannot_move_human_actor` | new | Phase 2 |
| `test_ai_cannot_move_human_actor_physical_state` | new | Phase 2 |
| `test_actor_lane_validation_runs_before_commit` | new | Phase 2 |
| `test_actor_lane_enforcement_active_in_graph_execution` | new | Phase 2 |
| `test_runtime_turn_state_has_actor_lane_context_field` | new | Phase 2 |
| `test_story_runtime_manager_has_extract_actor_lane_context` | new | Phase 2 |
| `test_extract_actor_lane_context_returns_none_without_ownership` | new | Phase 2 |
| `test_extract_actor_lane_context_returns_context_with_ownership` | new | Phase 2 |

---

## Tests Executed

```
world-engine/tests/test_mvp2_runtime_state_actor_lanes.py   39 passed
world-engine/tests/test_mvp2_npc_coercion_state_delta.py    32 passed
world-engine/tests/test_mvp2_object_admission.py            22 passed
world-engine/tests/test_mvp2_operational_gate.py            17 passed
world-engine/tests/test_mvp1_experience_identity.py         53 passed
TOTAL: 163 passed, 0 failed
```

---

## run-test.py Coverage

`python run-test.py --mvp2` → `python tests/run_tests.py --suite engine`
Includes: `test_mvp2_runtime_state_actor_lanes.py` (39 tests) ✓

---

## GitHub Workflow Coverage

`.github/workflows/mvp2-tests.yml` → `mvp2-world-engine` job runs all 4 MVP2 test files ✓

---

## TOML/Tooling Coverage

`world-engine/pyproject.toml` → `testpaths = ["tests"]` picks up all MVP2 test files ✓

---

## Final PASS/FAIL Verdict

**Phase 1 status: PASS**
- ActorLaneContext created from real MVP1 handoff (Annette + Alain)
- All canonical Phase 1 tests pass
- No false-green patterns remain in Phase 1

**Phase 2 status: PASS**
- All enforcement validators proven to reject AI output for human actor
- Enforcement wired into graph execution path (FG-001 and FG-002 fixed)
- Validation proven to run before commit and before packaging
- One known integration dependency documented (BLOCKER-001 — backend runtime_projection gap, MVP3 integration point)
