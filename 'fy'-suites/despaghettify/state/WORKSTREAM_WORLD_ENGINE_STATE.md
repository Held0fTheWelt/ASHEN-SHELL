# Workstream: world_engine

## Closed — DS-038 manager scene-block and diagnostic snapshot split (session 20260528)

| DS-ID | Outcome | Primary files / symbols | Evidence |
|-------|---------|--------------------------|----------|
| DS-038 | NPC scripted speech realization, player-input scene-block construction, and thin-path diagnostic snapshot aggregation now delegate to named helper phases without changing manager payloads. | `_realize_npc_speak_block`, `_player_input_scene_blocks_for_story_window`, `get_runtime_diagnostic_snapshot` | Pre: `artifacts/workstreams/world_engine/pre/session_20260528_DS-038_wave_plan.md`; post: `artifacts/workstreams/world_engine/post/session_20260528_DS-038_comparison.md` |

**Gates (final):**

- `python -m py_compile` on touched DS-038 world-engine files — passed.
- `INTERNAL_RUNTIME_CONFIG_TOKEN= PYTHONPATH=/mnt/d/WorldOfShadows/world-engine:/mnt/d/WorldOfShadows python -m pytest -q world-engine/tests/test_story_runtime_shell_readout.py world-engine/tests/test_story_runtime_shell_readout_structure.py world-engine/tests/test_story_runtime_manager_session_layout.py world-engine/tests/test_mvp1_experience_identity.py -k 'thin or diagnostic or player or scene or narrator or opening or session' --tb=short` — 24 passed, 62 deselected.
- Final `check --with-metrics` — pass, report generated `2026-05-28T18:18:39Z`.

**Structural delta:** DS-038 target symbols are pruned from the current top-12 longest ranking. Current full scan: 11299 functions; L50 809; L100 102; D6 0; `M7_anteil` 3.6891.

## Closed — DS-035 turn graph and branching executor split (session 20260528)

| DS-ID | Outcome | Primary files / symbols | Evidence |
|-------|---------|--------------------------|----------|
| DS-035 | Minimal turn graph execution now delegates prompt creation, primary/fallback route invocation, generation metadata, visible output, and diagnostics; branching turn execution now delegates path lookup, decision resolution, validation errors, decision recording, history updates, and path signatures. | `MinimalRuntimeTurnGraphExecutor.run`, `execute_turn` | Pre: `artifacts/workstreams/world_engine/pre/session_20260528_DS-035_wave_plan.*`; post: `artifacts/workstreams/world_engine/post/session_20260528_DS-035_comparison.*` |

**Gates (final):**

- `python -m py_compile world-engine/app/story_runtime/minimal_turn_graph.py world-engine/app/runtime/branching_turn_executor.py` — passed.
- `INTERNAL_RUNTIME_CONFIG_TOKEN= PYTHONPATH=/mnt/d/WorldOfShadows/world-engine:/mnt/d/WorldOfShadows python -m pytest -q tests/branching/test_branching_turn_executor.py tests/branching/test_evaluation_cycle.py --tb=short` — 29 passed.
- Final `check --with-metrics` — pass, report generated `2026-05-28T17:36:09Z`.

**Structural delta:** DS-035 target symbols are pruned from the current top-12 longest ranking. Current full scan: 11230 functions; L50 808; L100 114; D6 0; `M7_anteil` 3.7336.

**Caveat:** The broader `world-engine/tests/test_turn_execution.py` collection still fails on the existing import path `app.runtime.session_manager`; the focused DS-035 branching gate passes and the failure is outside these touched files.

## Closed — DS-031 manager split and DS-032 UI/prior-export support (session 20260528)

| DS-ID | Outcome | Primary files / symbols | Evidence |
|-------|---------|--------------------------|----------|
| DS-031 | Live scene envelope, narrator output realization, and opening prompt construction now delegate to named actor identity, speech/response, diagnostics, fallback, candidate-attempt, scene-context, and policy-context helpers. | `_build_live_scene_turn_envelope`, `_realize_narrator_path_output`, `_build_opening_prompt` | Pre: `artifacts/workstreams/world_engine/pre/session_20260528_DS-031_*`; post: `artifacts/workstreams/world_engine/post/session_20260528_DS-031_comparison.*` |
| DS-032 | World-engine UI route registration is split into entry/auth/proxy/page route registrars with named HTTP status constants; callback/cascade prior graph exports preserve continuity-edge signals for live graph calls. | `register_world_engine_ui_routes`, `_register_world_engine_auth_routes`, `_prior_callback_web_state_for_graph`, `_prior_consequence_cascade_state_for_graph` | Post evidence is recorded under the primary backend workstream: `artifacts/workstreams/backend_runtime_services/post/session_20260528_DS-032_comparison.*` |

**Gates (final):**

- `INTERNAL_RUNTIME_CONFIG_TOKEN= PYTHONPATH=/mnt/d/WorldOfShadows/world-engine:/mnt/d/WorldOfShadows python -m pytest -q world-engine/tests/test_goc_narrator_path_opening.py world-engine/tests/test_mvp1_experience_identity.py -k 'opening or narrator_path' --tb=short` — 8 passed, 53 deselected.
- Initial broad DS-032 world-engine gate found two callback/cascade prior-export regressions after 35 passing tests; the corrected focused rerun `INTERNAL_RUNTIME_CONFIG_TOKEN= PYTHONPATH=/mnt/d/WorldOfShadows/world-engine:/mnt/d/WorldOfShadows python -m pytest -q world-engine/tests/test_story_runtime_callback_web.py world-engine/tests/test_story_runtime_consequence_cascade.py --tb=short` — 3 passed.
- `python -m py_compile` on all changed world-engine files — passed.
- Final `check --with-metrics` — pass, report generated `2026-05-28T15:25:17Z`.

**Structural delta:** DS-031 target leaders are pruned from the current top-12 longest ranking. `register_world_engine_ui_routes` is now a short registrar orchestrator with 0 counted magic integer literals.

## Closed — DS-025 world-engine manager/session split (session 20260523)

| Sub-wave | Outcome | Primary files / symbols | Evidence |
|----------|---------|--------------------------|----------|
| w01 | Souffleuse output realization now delegates source projection, fallback result, attempt execution, module-block realization, and module result assembly. | `souffleuse_output_realization.py`; `_realize_souffleuse_output` | Post: `artifacts/workstreams/world_engine/post/session_20260523_DS-025_world_engine_manager_session_comparison.*` |
| w02 | Opening execution now delegates graph run, state assembly, continuation, canonical-step advancement, and summary construction. | `opening_execution.py`; `_execute_opening_locked` | Same post comparison as w01. |
| w03 | Session manager initialization/persistence now delegates storage, authority state, runtime state, registry/adapters, retrieval, capability runtime, and persisted-session loading. | `session/manager_init_and_persistence.py`; `__init__` | Same post comparison as w01. |
| w04 | Shell social-pressure summary now delegates active-pressure label extraction and summary formatting. | `shell_readout/social_pressure_readout.py`; `_active_pressure_summary` | Same post comparison as w01. |

**Gates (final):**

- `INTERNAL_RUNTIME_CONFIG_TOKEN= PYTHONPATH=/mnt/d/WorldOfShadows/world-engine:/mnt/d/WorldOfShadows python -m pytest -q world-engine/tests/test_goc_narrator_path_opening.py world-engine/tests/test_story_runtime_manager_session_layout.py world-engine/tests/test_story_session_persistence.py --tb=short` — 16 passed, 1 warning.
- `INTERNAL_RUNTIME_CONFIG_TOKEN= PYTHONPATH=/mnt/d/WorldOfShadows/world-engine:/mnt/d/WorldOfShadows python -m pytest -q world-engine/tests/test_story_runtime_shell_readout.py world-engine/tests/test_story_runtime_shell_readout_structure.py world-engine/tests/test_story_runtime_environment_state.py --tb=short` — 22 passed.
- `python -m py_compile` on all changed DS-025 Python files — passed.
- Final `check --with-metrics` — pass, report generated `2026-05-23T14:33:12Z`.

**Structural delta:** DS-025 target symbols no longer appear in the formal top-12 longest ranking. Current full scan: 11076 functions; L50 803; L100 139; D6 0.

## Closed — DS-022 world-engine branch/session split (session 20260523)

| Sub-wave | Outcome | Primary files / symbols | Evidence |
|----------|---------|--------------------------|----------|
| w01 | Branch tree node selection now delegates freshness/context lookup, start/replay/final timeline events, payload assembly, and commit-record persistence. | `branch_selection.py`; `select_branching_tree_node` | Pre: `artifacts/workstreams/world_engine/pre/session_20260523_DS-022_wave_plan.*`; post: `artifacts/workstreams/world_engine/post/session_20260523_DS-022_world_engine_branch_session_comparison.*` |
| w02 | Story session creation route now delegates Langfuse adapter setup, environment/span setup, session scope, runtime creation, response assembly, and finalization. | `story_session_lifecycle_routes.py`; `create_story_session` | Same post comparison as w01. |
| w03 | Opening fallback observability now delegates primary-attempt metadata, fallback generation, validation, committed result, ledger, and degradation assembly. | `opening_fallback_observability.py`; `_ldss_opening_fallback_state` | Same post comparison as w01. |

**Gates (final):**

- `python -m py_compile` on changed DS-022 Python files — passed.
- `INTERNAL_RUNTIME_CONFIG_TOKEN= PYTHONPATH=/mnt/d/WorldOfShadows/world-engine:/mnt/d/WorldOfShadows python -m pytest -q world-engine/tests/test_story_runtime_branching_simulation_tree.py world-engine/tests/test_story_runtime_branching_tree_api.py --tb=short` — 7 passed.
- `INTERNAL_RUNTIME_CONFIG_TOKEN= PYTHONPATH=/mnt/d/WorldOfShadows/world-engine:/mnt/d/WorldOfShadows python -m pytest -q world-engine/tests/test_ldss_opening_fallback_actor_lane.py --tb=short` — 3 passed.
- `INTERNAL_RUNTIME_CONFIG_TOKEN= PYTHONPATH=/mnt/d/WorldOfShadows/world-engine:/mnt/d/WorldOfShadows python -m pytest -q world-engine/tests/test_mvp1_experience_identity.py -k 'create_story_session' --tb=short` — 3 passed, 53 deselected.
- Final `check --with-metrics` — pass, report generated `2026-05-23T13:13:11Z`.

**Structural delta:** `select_branching_tree_node` 198 → 93 AST lines; `create_story_session` 185 → 80; `_ldss_opening_fallback_state` 180 → 27. Current full scan: 10996 functions; L50 804; L100 149; D6 3.

## Closed — DS-018 world-engine turn API / WebSocket split (session 20260523)

| Sub-wave | Outcome | Primary files / symbols | Evidence |
|----------|---------|--------------------------|----------|
| w01 | HTTP story-turn execution now delegates trace/span setup, trace updates, turn execution, and span close to named helpers. | `story_turn_routes.py`; `execute_story_turn` | Pre: `artifacts/workstreams/world_engine/pre/session_20260523_DS-018_wave_plan.*`; post: `artifacts/workstreams/world_engine/post/session_20260523_DS-018_world_engine_turn_api_comparison.*` |
| w02 | Locked manager turn execution delegates graph run and recoverable graph-exception persistence. | `turn_execution.py`; `_execute_turn_locked` | Same post comparison as w01. |
| w03 | WebSocket session streaming and autonomous follow-up phases are explicit; MVP3 streaming fixture now uses canonical `npc_initiatives`. | `story_ws.py`; `story_session_stream`, `_run_autonomous_followup_after_turn`; `test_mvp3_narrative_streaming_endpoint.py` | Same post comparison as w01. |

**Gates (final):**

- `python -m py_compile` on all changed DS-018 Python files — passed.
- `INTERNAL_RUNTIME_CONFIG_TOKEN= PYTHONPATH=/mnt/d/WorldOfShadows/world-engine:/mnt/d/WorldOfShadows python -m pytest -q world-engine/tests/test_phase2_ws_session_loop_endpoint.py world-engine/tests/test_mvp3_narrative_streaming_endpoint.py world-engine/tests/test_story_runtime_narrative_commit.py --tb=short` — 79 passed.
- `pytest -q tests/gates/test_goc_mvp03_live_dramatic_scene_simulator_gate.py tests/gates/test_goc_mvp04_observability_diagnostics_gate.py --tb=short` — 75 passed.
- `PYTHONPATH="'fy'-suites" python -m despaghettify.tools wave-plan-validate --file "'fy'-suites/despaghettify/state/artifacts/workstreams/world_engine/pre/session_20260523_DS-018_wave_plan.json" --check-primary-paths --gate-prefix-allowlist python,pytest,INTERNAL_RUNTIME_CONFIG_TOKEN,PYTHONPATH` — pass.
- Final `check --with-metrics` — pass, report generated `2026-05-23T12:06:16Z`.

**Structural delta:** `story_session_stream` 229 → 93 AST lines, `_run_autonomous_followup_after_turn` 181 → 128, `execute_story_turn` 225 → 66, `_execute_turn_locked` 214 → 81. DS-018 target symbols no longer appear in the current top-12 longest or top-6 nesting rankings.

## Closed — DS-014 world-engine runtime/readout split (session 20260522)

| Sub-wave | Outcome | Primary files / symbols | Evidence |
|----------|---------|--------------------------|----------|
| w01 | Player-visible persistence now delegates event defaults, runtime-surface copy, and canonical record assembly to focused helpers. | `player_visible_persistence.py`, `player_visible_event_defaults.py`, `player_visible_runtime_surfaces.py`, `player_visible_canonical_record.py`; `_persist_player_visible_turn_event` | Post comparison: `artifacts/workstreams/world_engine/post/session_20260522_DS-014_world_engine_runtime_readout_comparison.*` |
| w02 | Session-state readout now delegates last-turn extraction, canonical counts, snapshots, loop readout, committed-state readout, and final response assembly. | `session/session_state_api.py`, `session_state_readout_parts.py`, `session_state_response_parts.py`; `get_state` | Post comparison: `artifacts/workstreams/world_engine/post/session_20260522_DS-014_world_engine_runtime_readout_comparison.*` |
| w03 | Story-window entry construction and committed dramatic-context sections are split into named helpers while preserving projection fields. | `story_window_entries.py`, `story_window_entry_parts.py`, `committed_dramatic_context.py`, `committed_dramatic_context_parts.py` | Post comparison: `artifacts/workstreams/world_engine/post/session_20260522_DS-014_world_engine_runtime_readout_comparison.*` |
| w04 | Governed provider adapter construction and route/model selection helpers are outside the policy class body. | `governed_runtime.py`, `governed_runtime_adapters.py`; `GovernedStoryRoutingPolicy`, `build_governed_model_adapters` | Post comparison: `artifacts/workstreams/world_engine/post/session_20260522_DS-014_world_engine_runtime_readout_comparison.*` |

**Plan mirror:** `artifacts/workstreams/world_engine/pre/session_20260522_DS-014_wave_plan.json`

**Current metrics report:** `../reports/latest_check_with_metrics.json` generated `2026-05-22T19:50:52Z`.

## Gates

- `python -m py_compile` on all changed DS-014 Python files — passed.
- `INTERNAL_RUNTIME_CONFIG_TOKEN= PYTHONPATH=world-engine:. pytest -q world-engine/tests/test_story_window_projection.py world-engine/tests/test_story_runtime_w5_player_view.py --tb=short` — 15 passed.
- `INTERNAL_RUNTIME_CONFIG_TOKEN= PYTHONPATH=world-engine:. pytest -q world-engine/tests/test_authority_version_and_route_family_truth.py::test_narrative_task_reports_route_family_truth world-engine/tests/test_authority_version_and_route_family_truth.py::test_build_governed_components_uses_new_policy world-engine/tests/test_authority_version_and_route_family_truth.py::test_governed_routing_prefers_rich_model_for_high_complexity_turns world-engine/tests/test_live_story_runtime_governance.py::test_governed_config_enables_live_path --tb=short` — 4 passed.
- `INTERNAL_RUNTIME_CONFIG_TOKEN= PYTHONPATH=world-engine:. pytest -q world-engine/tests/test_story_runtime_narrative_commit.py::test_recoverable_validation_rejection_returns_structured_turn world-engine/tests/test_story_runtime_narrative_commit.py::test_execute_turn_propagates_vitality_telemetry_to_event_and_governance world-engine/tests/test_story_runtime_narrative_commit.py::test_human_input_attribution_uses_player_input_kind_surface --tb=short` — 3 passed.
- `INTERNAL_RUNTIME_CONFIG_TOKEN= PYTHONPATH=world-engine:. pytest -q world-engine/tests/test_story_runtime_narrative_threads.py::test_committed_dramatic_context_reaches_history_story_window_and_shell --tb=short` — 1 passed.
- `PYTHONPATH="'fy'-suites" python -m despaghettify.tools check --with-metrics --out "'fy'-suites/despaghettify/reports/latest_check_with_metrics.json"` — passed.
- `git diff --check` for touched DS-014 files — passed with CRLF normalization warnings only.

## Structural delta

- `_persist_player_visible_turn_event`: 120 AST lines → 91.
- `get_state`: 153 AST lines → 94.
- `_story_window_entries_for_session`: 123 AST lines → 91.
- `_build_committed_dramatic_context_summary`: 235 AST lines → 93.
- `GovernedStoryRoutingPolicy`: 168 AST lines → 83.
- Current full scan: 10638 functions; L50 794; L100 187; D6 16.
- DS-014 world-engine targets no longer appear in the formal top-12 longest ranking.

## Closed — DS-009 world-engine runtime split (session 20260520)

| Sub-wave | Outcome | Primary files / symbols | Evidence |
|----------|---------|--------------------------|----------|
| w01 | Planner-truth projection moved behind a focused story-runtime projection module. `_planner_truth_from_graph_state(...)` remains as the stable `PlannerTruth` wrapper. | `world-engine/app/story_runtime/commit_models.py`, `world-engine/app/story_runtime/planner_truth_projection.py`; `_planner_truth_from_graph_state`, `build_planner_truth_payload` | Post comparison: `artifacts/workstreams/world_engine/post/session_20260520_DS-009_w01_planner_truth_comparison.*` |
| w02 | WebSocket autonomous follow-up wait/cut-in loop extracted from `story_session_stream(...)` into `_run_autonomous_followup_after_turn(...)`. | `world-engine/app/api/story_ws.py`; `story_session_stream`, `_run_autonomous_followup_after_turn` | Post comparison: `artifacts/workstreams/world_engine/post/session_20260520_DS-009_w02_ws_stream_loop_comparison.*` |

**Plan mirror:** `artifacts/workstreams/world_engine/pre/session_20260520_DS-009_wave_plan.json`

**Current metrics report:** `../reports/latest_check_with_metrics.json` generated `2026-05-20T22:02:19Z`.

## Gates

- `python -m compileall -q world-engine/app/story_runtime world-engine/app/api` — passed.
- `INTERNAL_RUNTIME_CONFIG_TOKEN= pytest world-engine/tests/test_planner_truth_and_runtime_surfaces.py::test_planner_truth_populated_from_graph_state world-engine/tests/test_planner_truth_and_runtime_surfaces.py::test_planner_truth_persists_current_npc_agency_closure world-engine/tests/test_validator_lane_truth.py::test_planner_truth_validator_layers_from_live_seam -q --tb=short` — 3 passed.
- Earlier full focused planner/lane/commit gate in this wave: `pytest world-engine/tests/test_planner_truth_and_runtime_surfaces.py world-engine/tests/test_validator_lane_truth.py world-engine/tests/test_story_runtime_narrative_commit.py -q --tb=short` — 33 passed before the final helper compaction.
- `INTERNAL_RUNTIME_CONFIG_TOKEN= pytest world-engine/tests/test_phase2_ws_session_loop_endpoint.py world-engine/tests/test_mvp3_narrative_streaming_endpoint.py -q --tb=short` — 60 passed.
- `PYTHONPATH="'fy'-suites" DESPAG_SKIP_ARCHIVE_SYNC=1 python -m despaghettify.tools.hub_cli wave-plan-validate --file "'fy'-suites/despaghettify/state/artifacts/workstreams/world_engine/pre/session_20260520_DS-009_wave_plan.json" --check-primary-paths` — passed.
- `PYTHONPATH="'fy'-suites" DESPAG_SKIP_ARCHIVE_SYNC=1 python -m despaghettify.tools.hub_cli check --with-metrics --out "'fy'-suites/despaghettify/reports/latest_check_with_metrics.json"` — passed.
- `git diff --check` for touched world-engine/state files — passed.

## Caveats

- `python tests/run_tests.py --suite engine_runtime --quick` currently stops on unrelated NLU contract drift in `world-engine/tests/test_story_runtime_api.py::test_story_session_lifecycle_and_nl_interpretation` (`interpreted_input.kind`: expected `mixed`, got `speech`).
- `python tests/run_tests.py --suite engine_http_ws --quick` was stopped as over-broad for DS-009 after a long generic HTTP run; no DS-009 failure had surfaced at the stop point.

## Structural delta

- `_planner_truth_from_graph_state`: 540 AST lines / depth 6 → 9 lines / depth 0 wrapper.
- `build_planner_truth_payload`: 133 lines / depth 1 in the extracted projection module.
- `story_session_stream`: 391 AST lines / depth 8 → 229 lines / depth 5.
- Current full scan: 10747 functions; L50 858; L100 235; D6 24.
- DS-009 symbols no longer appear in the formal top longest/nesting rankings.
