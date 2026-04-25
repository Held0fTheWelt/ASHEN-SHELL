# GOC MVP2 Source Locator — Phase 1 & Phase 2 Hardening

**MVP**: 02 — Runtime State, Actor Lanes, and Content Boundary
**Date**: 2026-04-25 (hardened)
**Status**: Complete — no unresolved anchors

---

## Core Source Anchors

| Area | Repository Path | Symbol / Anchor | Notes |
|---|---|---|---|
| ActorLaneContext type/model | `world-engine/app/runtime/models.py` | `ActorLaneContext` (Pydantic BaseModel) | Contract: `actor_lane_context.v1` |
| ActorLaneContext assembly function | `world-engine/app/runtime/actor_lane.py` | `build_actor_lane_context(actor_ownership, *, selected_player_role, runtime_profile_id, content_module_id)` | Consumes MVP1 `build_actor_ownership()` output |
| RuntimeState type/model | `world-engine/app/runtime/models.py` | `RuntimeState` (Pydantic BaseModel) | Contract: `runtime_state.v1` |
| StorySessionState type/model | `world-engine/app/runtime/models.py` | `StorySessionState` (Pydantic BaseModel) | Contract: `story_session_state.v1` |
| ActorLaneValidationResult type | `world-engine/app/runtime/models.py` | `ActorLaneValidationResult` (Pydantic BaseModel) | Contract: `actor_lane_validation_result.v1` |
| RuntimeState builder | `world-engine/app/runtime/actor_lane.py` | `build_runtime_state(actor_ownership, *, run_id, story_session_id, ...)` | Source provenance fields |
| StorySessionState builder | `world-engine/app/runtime/actor_lane.py` | `build_story_session_state(actor_ownership, *, run_id, story_session_id, ...)` | Persists role ownership |
| MVP1 handoff consumption point | `world-engine/app/runtime/profiles.py` | `build_actor_ownership(selected_player_role, profile)` → dict consumed by `build_actor_lane_context()` | Returns `human_actor_id`, `npc_actor_ids`, `actor_lanes`, `visitor_present`, `content_hash` |
| Runtime/session state source | `world-engine/app/runtime/profiles.py` | `resolve_runtime_profile("god_of_carnage_solo")` → `RuntimeProfile`; then `build_actor_ownership()` | Canonical actor IDs from `content/modules/god_of_carnage/characters.yaml` |
| AI/runtime candidate generation seam | `ai_stack/langgraph_runtime_executor.py` | `_run_validation()` closure inside `validate_seam` node (~line 2260) | Calls `run_validation_seam()` with `actor_lane_context` |
| Actor-lane validation function (world-engine) | `world-engine/app/runtime/actor_lane.py` | `validate_actor_lane_output(candidate, actor_lane_context, *, validation_location)` | Rejects AI output for human actor |
| Actor-lane validation function (ai_stack seam) | `ai_stack/goc_turn_seams.py` | `_check_human_actor_violations(structured, ai_forbidden, human_actor_id)` → called from `run_validation_seam()` | Runs before dramatic-effect gate |
| Actor-lane context in graph state | `ai_stack/langgraph_runtime_state.py` | `RuntimeTurnState.actor_lane_context: dict[str, Any]` | Optional field; populated by `RuntimeTurnGraphExecutor.run()` |
| Actor-lane context wiring in executor | `ai_stack/langgraph_runtime_executor.py` | `RuntimeTurnGraphExecutor.run(..., actor_lane_context=...)` | Passes context into `initial_state` |
| Actor-lane context extraction from session | `world-engine/app/story_runtime/manager.py` | `StoryRuntimeManager._extract_actor_lane_context(session)` | Returns None when runtime_projection lacks ownership |
| Responder validation function | `world-engine/app/runtime/actor_lane.py` | `validate_responder_plan(responder_plan, actor_lane_context)` | Rejects human actor as responder |
| run_validation_seam with enforcement | `ai_stack/goc_turn_seams.py` | `run_validation_seam(..., actor_lane_context=dict)` | Human-actor enforcement runs before dramatic-effect gate |
| Commit seam | `ai_stack/goc_turn_seams.py` | `run_commit_seam(module_id, validation_outcome, proposed_state_effects, ...)` | Blocked by rejected `validation_outcome.status` |
| Response packaging seam | `ai_stack/goc_turn_seams.py` | `run_visible_render(...)` | Emits `render_downgrade` when `actor_lane_validation.status == "rejected"` |

---

## Phase 1 Tests

| Test | File | Classification | Covers |
|---|---|---|---|
| `test_actor_lane_context_created_for_annette_start` | `test_mvp2_runtime_state_actor_lanes.py` | behavior_proving | ActorLaneContext for Annette |
| `test_actor_lane_context_created_for_alain_start` | `test_mvp2_runtime_state_actor_lanes.py` | behavior_proving | ActorLaneContext for Alain |
| `test_selected_actor_is_human` | `test_mvp2_runtime_state_actor_lanes.py` | behavior_proving | selected actor has lane "human" |
| `test_non_selected_canonical_actors_are_npcs` | `test_mvp2_runtime_state_actor_lanes.py` | behavior_proving | remaining actors have lane "npc" |
| `test_actor_lane_context_uses_mvp1_handoff` | `test_mvp2_runtime_state_actor_lanes.py` | behavior_proving | real resolver, Annette start |
| `test_actor_lane_context_uses_mvp1_handoff_alain_start` | `test_mvp2_runtime_state_actor_lanes.py` | behavior_proving | real resolver, Alain start |
| `test_actor_lane_context_excludes_visitor` | `test_mvp2_runtime_state_actor_lanes.py` | behavior_proving | visitor rejected from lanes |
| `test_ai_allowed_actor_ids_exclude_human_actor` | `test_mvp2_runtime_state_actor_lanes.py` | behavior_proving | canonical Phase 1 required name |
| `test_ai_forbidden_actor_ids_include_human_actor` | `test_mvp2_runtime_state_actor_lanes.py` | behavior_proving | canonical Phase 1 required name |

---

## Phase 2 Tests

| Test | File | Classification | Covers |
|---|---|---|---|
| `test_ai_cannot_speak_for_human_actor` | `test_mvp2_runtime_state_actor_lanes.py` | behavior_proving | AI line rejected |
| `test_ai_cannot_act_for_human_actor` | `test_mvp2_runtime_state_actor_lanes.py` | behavior_proving | AI action rejected |
| `test_ai_cannot_assign_human_actor_emotion` | `test_mvp2_runtime_state_actor_lanes.py` | behavior_proving | AI emotion rejected |
| `test_ai_cannot_decide_for_human_actor` | `test_mvp2_runtime_state_actor_lanes.py` | behavior_proving | AI decision rejected |
| `test_ai_cannot_move_human_actor` | `test_mvp2_runtime_state_actor_lanes.py` | behavior_proving | AI movement rejected |
| `test_human_actor_cannot_be_primary_responder` | `test_mvp2_runtime_state_actor_lanes.py` | behavior_proving | responder rejection |
| `test_human_actor_cannot_be_secondary_responder` | `test_mvp2_runtime_state_actor_lanes.py` | behavior_proving | secondary responder rejection |
| `test_visitor_cannot_be_responder` | `test_mvp2_runtime_state_actor_lanes.py` | behavior_proving | visitor responder rejected |
| `test_actor_lane_validation_runs_before_response_packaging` | `test_mvp2_runtime_state_actor_lanes.py` | behavior_proving | enforcement before packaging |
| `test_actor_lane_validation_runs_before_commit` | `test_mvp2_runtime_state_actor_lanes.py` | behavior_proving | enforcement before commit |
| `test_actor_lane_enforcement_active_in_graph_execution` | `test_mvp2_runtime_state_actor_lanes.py` | behavior_proving | graph wiring confirmed |
| `test_runtime_turn_state_has_actor_lane_context_field` | `test_mvp2_runtime_state_actor_lanes.py` | behavior_proving | state carries context |
| `test_story_runtime_manager_has_extract_actor_lane_context` | `test_mvp2_runtime_state_actor_lanes.py` | behavior_proving | manager wired |
| `test_extract_actor_lane_context_returns_none_without_ownership` | `test_mvp2_runtime_state_actor_lanes.py` | behavior_proving | safe when no ownership |
| `test_extract_actor_lane_context_returns_context_with_ownership` | `test_mvp2_runtime_state_actor_lanes.py` | behavior_proving | extracts correctly |

---

## Operational Infrastructure

| Area | Path | Symbol |
|---|---|---|
| run-test.py suite entry | `run-test.py` | `--mvp2` → `--suite engine` |
| GitHub workflow job | `.github/workflows/mvp2-tests.yml` | `mvp2-world-engine` job |
| TOML testpaths | `world-engine/pyproject.toml` | `testpaths = ["tests"]` |
| docker-up.py | `docker-up.py` | `gate` subcommand |

---

## Known Integration Dependency (not a blocker for Phase 1/2 hardening)

The backend must include `human_actor_id`, `npc_actor_ids`, `actor_lanes`, and `selected_player_role`
in the `runtime_projection` dict when calling `POST /api/story/sessions` for a God of Carnage solo session.
Without these fields, `_extract_actor_lane_context()` returns `None` and enforcement is skipped (safe degradation).
The wiring from world-engine's `create_run` response to the story session `runtime_projection` is an MVP3
integration point. Phase 1/2 hardening proves the enforcement machinery and wiring are correct.
