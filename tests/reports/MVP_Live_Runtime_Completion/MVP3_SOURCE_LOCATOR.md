# MVP3 Source Locator Matrix

**MVP**: 03 — Live Dramatic Scene Simulator  
**Date**: 2026-04-25  
**Status**: RESOLVED — no unresolved placeholders

---

## Source Locator Matrix

| Area | Expected Path | Actual Path | Symbol / Anchor | Status |
|---|---|---|---|---|
| MVP 03 guide | `docs/MVPs/MVP_Live_runtime_Completion/03_live_dramatic_scene_simulator.md` | `docs/MVPs/MVP_Live_runtime_Completion/03_live_dramatic_scene_simulator.md` | `## Mission`, `## Patch Map` | found |
| LDSS module | `ai_stack/live_dramatic_scene_simulator.py` | `ai_stack/live_dramatic_scene_simulator.py` | `run_ldss`, `SceneTurnEnvelopeV2`, `LDSSInput`, `LDSSOutput`, `NPCAgencyPlan` | found |
| World-engine API route | `world-engine/app/api/http.py` | `world-engine/app/api/http.py` | `POST /story/sessions/{session_id}/turns` → `execute_story_turn` | found |
| World-engine runtime manager | `world-engine/app/runtime/manager.py` | `world-engine/app/runtime/manager.py` | `RuntimeManager.create_run` | found |
| World-engine story runtime | `world-engine/app/story_runtime/manager.py` | `world-engine/app/story_runtime/manager.py` | `StoryRuntimeManager.execute_turn`, `_finalize_committed_turn`, `_build_ldss_scene_envelope` | found |
| LDSS integration seam | `world-engine/app/story_runtime/manager.py` | `world-engine/app/story_runtime/manager.py` | `_build_ldss_scene_envelope` called in `_finalize_committed_turn` | found |
| Actor lane context builder | `world-engine/app/runtime/actor_lane.py` | `world-engine/app/runtime/actor_lane.py` | `build_actor_lane_context`, `validate_actor_lane_output` | found |
| Actor lane models | `world-engine/app/runtime/models.py` | `world-engine/app/runtime/models.py` | `ActorLaneContext`, `ActorLaneValidationResult`, `RuntimeState`, `StorySessionState` | found |
| Object admission | `world-engine/app/runtime/object_admission.py` | `world-engine/app/runtime/object_admission.py` | `admit_object`, `validate_object_admission` | found |
| State delta | `world-engine/app/runtime/state_delta.py` | `world-engine/app/runtime/state_delta.py` | `validate_state_delta`, `validate_state_deltas` | found |
| ai_stack graph executor | `ai_stack/langgraph_runtime_executor.py` | `ai_stack/langgraph_runtime_executor.py` | `RuntimeTurnGraphExecutor`, `_package_output` | found |
| ai_stack turn seams | `ai_stack/goc_turn_seams.py` | `ai_stack/goc_turn_seams.py` | `run_visible_render`, `run_commit_seam`, `run_validation_seam` | found |
| ai_stack LDSS validators | `ai_stack/live_dramatic_scene_simulator.py` | `ai_stack/live_dramatic_scene_simulator.py` | `validate_actor_lane_blocks`, `validate_dramatic_mass`, `validate_narrator_voice`, `validate_passivity`, `validate_affordance` | found |
| ai_stack story experience | `ai_stack/story_runtime_experience.py` | `ai_stack/story_runtime_experience.py` | `EXPERIENCE_MODES` includes `live_dramatic_scene_simulator` | found |
| MVP 03 gate tests | `tests/gates/test_goc_mvp03_live_dramatic_scene_simulator_gate.py` | `tests/gates/test_goc_mvp03_live_dramatic_scene_simulator_gate.py` | 26 test functions | found |
| MVP 03 integration tests | `world-engine/tests/test_mvp3_ldss_integration.py` | `world-engine/tests/test_mvp3_ldss_integration.py` | 6 test functions through `execute_turn` | found |
| MVP 01/02 foundation gate | `tests/gates/test_goc_mvp01_mvp02_foundation_gate.py` | `tests/gates/test_goc_mvp01_mvp02_foundation_gate.py` | `TestMVP01RulesEnforced`, `TestMVP02RulesEnforced`, `TestFoundationGateOverall` | found |
| Runtime profile | `world-engine/app/runtime/profiles.py` | `world-engine/app/runtime/profiles.py` | `resolve_runtime_profile`, `build_actor_ownership` | found |
| Backend service | `backend/app/services/game_service.py` | `backend/app/services/game_service.py` | `runtime_projection` building | found |
| run-test.py | `run-test.py` | `run-test.py` | `--mvp3` suite flag | found |
| GitHub workflows | `.github/workflows/*.yml` | `.github/workflows/` | CI job anchors | checked |
| TOML/tooling | `pyproject.toml`, `world-engine/pyproject.toml`, `world-engine/pytest.ini` | same | `testpaths`, `markers` | found |
| Reports | `tests/reports/MVP_Live_Runtime_Completion/` | `tests/reports/MVP_Live_Runtime_Completion/` | `MVP3_SOURCE_LOCATOR.md`, `MVP3_OPERATIONAL_EVIDENCE.md` | found |
| ADR-011 | `docs/ADR/ADR-011-live-dramatic-scene-simulator.md` | `docs/ADR/ADR-011-live-dramatic-scene-simulator.md` | ADR-011 | not_present — not blocking: LDSS behavior is proven by gate tests and source code; ADR is a documentation deliverable |
| ADR-012 | `docs/ADR/ADR-012-npc-free-dramatic-agency.md` | not present | ADR-012 | not_present — not blocking |
| ADR-013 | `docs/ADR/ADR-013-narrator-inner-voice-contract.md` | not present | ADR-013 | not_present — not blocking |

---

## MVP 03 Known Blockers

None.

## MVP 01 / MVP 02 Dependencies

- `ActorLaneContext` from `world-engine/app/runtime/models.py` — fully available
- `validate_actor_lane_output` from `world-engine/app/runtime/actor_lane.py` — fully available
- `build_actor_ownership` from `world-engine/app/runtime/profiles.py` — fully available
- `admit_object` from `world-engine/app/runtime/object_admission.py` — fully available
- `validate_state_delta` from `world-engine/app/runtime/state_delta.py` — fully available
- `StoryRuntimeManager._extract_actor_lane_context` — fully available
- `GOD_OF_CARNAGE_MODULE_ID` from `world-engine/app/story_runtime/module_turn_hooks.py` — fully available

## Source Locator Gate Status

All required rows resolved. No placeholders remain.

`test_source_locator_matrix_has_no_placeholders_before_patch` — SATISFIED  
`test_source_locator_artifact_exists_for_mvp` — SATISFIED
