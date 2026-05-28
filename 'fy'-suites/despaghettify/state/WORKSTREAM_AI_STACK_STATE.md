# Workstream: ai_stack

## Closed — DS-041 semantic/authority and DS-043 contract readiness split (session 20260528)

| DS-ID | Outcome | Primary files / symbols | Evidence |
|-------|---------|--------------------------|----------|
| DS-041 | Semantic move interpretation, readiness co-authority preview, validation authority bridge, and bounded dramatic context summary now delegate to named snapshot, status, classification, retrieval, and context helpers. | `interpret_goc_semantic_move`, `build_readiness_co_authority_preview`, `build_validation_authority_bridge`, `build_bounded_dramatic_context_summary` | Pre: `artifacts/workstreams/ai_stack/pre/session_20260528_DS-041-043_wave_plan.md`; post: `artifacts/workstreams/ai_stack/post/session_20260528_DS-041-043_comparison.md` |
| DS-043 | Off-stage memory write, stream readiness, voice consistency, environment-state mutation, and temporal-control realization now delegate to named guard, evidence, mutation, and result helpers. | `build_off_stage_hierarchical_memory_write`, `compute_stream_readiness`, `validate_voice_consistency`, `apply_action_to_environment_state`, `validate_temporal_control_realization` | Same AI-stack pre/post artefacts. |

**Gates (final):**

- DS-041 focused semantic/authority/LangGraph gate — 76 passed.
- DS-043 focused memory/readiness/voice/environment/temporal gate — 76 passed.
- `python -m py_compile` on all touched AI-stack files — passed.
- Final `check --with-metrics` — pass, report generated `2026-05-28T18:57:09Z`.

**Structural delta:** DS-041 through DS-044 target symbols are pruned from the current top-12 longest ranking. Current full scan: 11374 functions; L50 808; L100 90; D6 0; `M7_anteil` 3.6402.

## Closed — DS-037 policy/contracts, DS-039 narrator continuation, and DS-040 director/session/research split (session 20260528)

| DS-ID | Outcome | Primary files / symbols | Evidence |
|-------|---------|--------------------------|----------|
| DS-037 | Runtime governance, meta-awareness derivation, free-player-action resolution, and NPC-agency plan normalization now delegate to named section helpers. | `_runtime_governance_policy`, `derive_meta_narrative_awareness`, `build_free_player_action_resolution`, `normalize_npc_agency_plan` | Pre: `artifacts/workstreams/ai_stack/pre/session_20260528_DS-037-040_wave_plan.md`; post: `artifacts/workstreams/ai_stack/post/session_20260528_DS-037-040_comparison.md` |
| DS-039 | GoC scripted continuation block and payload construction now delegates NPC-speak, perception, director-plan, and result payload sections. | `build_goc_scripted_continuation` | Same AI-stack post comparison. |
| DS-040 | Director pulse, template/semantic follow-up composition, and bounded research expansion now delegate motivation/action, result, gate, and child-record helpers. | `evaluate_director_tick`, `_compose_template_render_follow_up`, `run_bounded_exploration_expand_loop` | Same AI-stack post comparison. |

**Gates (final):**

- DS-037 focused suite — 41 passed.
- DS-039 AI narrator suite — 28 passed.
- DS-040 Director/session/research suite — 207 passed.
- `python -m py_compile` on touched DS-037/039/040 AI-stack files — passed.
- Final `check --with-metrics` — pass, report generated `2026-05-28T18:18:39Z`.

**Structural delta:** DS-037 through DS-040 target symbols are pruned from the current top-12 longest ranking. Current full scan: 11299 functions; L50 809; L100 102; D6 0; `M7_anteil` 3.6891.

## Closed — DS-033 actor/ledger split and DS-036 policy/RAG residuals (session 20260528)

| DS-ID | Outcome | Primary files / symbols | Evidence |
|-------|---------|--------------------------|----------|
| DS-033 | NPC initiative validation, runtime aspect-ledger score metadata, W5 actor validation, and W5 player-shell projection now delegate to named input, policy, failure-code, status, summary, and payload helpers. | `validate_npc_initiative_realization`, `aspect_score_metadata`, `validate_w5_actor_tracking`, `build_w5_projection_for_player_shell` | Pre: `artifacts/workstreams/ai_stack/pre/session_20260528_DS-033-036_wave_plan.*`; post: `artifacts/workstreams/ai_stack/post/session_20260528_DS-033-036_comparison.*` |
| DS-036 | Souffleuse projection, meta-awareness policy normalization, RAG retrieval orchestration, and module-runtime-policy assertions now use named context, normalization, result-building, authority, and assertion helpers. | `build_goc_opening_souffleuse_projection`, `normalize_meta_narrative_awareness_policy`, `retrieve`, `test_module_runtime_policy_loads_goc_without_runtime_hardcoding` | Same DS-033/036 pre/post artefacts. |

**Gates (final):**

- `python -m py_compile` on all touched DS-033/DS-036 AI-stack files — passed.
- `PYTHONPATH=/mnt/d/WorldOfShadows python -m pytest -q ai_stack/tests/test_actor_lane_hydration.py ai_stack/tests/test_w5_actor_tracking_validation.py ai_stack/tests/test_w5_actor_tracking_projection.py ai_stack/tests/test_runtime_aspect_ledger.py --tb=short` — 73 passed.
- `PYTHONPATH=/mnt/d/WorldOfShadows python -m pytest -q ai_stack/tests/test_god_of_carnage_souffleuse.py ai_stack/tests/test_meta_narrative_awareness_engine.py ai_stack/tests/test_retrieval_governance_wiring.py ai_stack/tests/test_module_runtime_policy.py --tb=short` — 42 passed.
- Final `check --with-metrics` — pass, report generated `2026-05-28T17:36:09Z`.

**Structural delta:** DS-033/DS-036 target symbols are pruned from the current top-12 longest ranking. Current full scan: 11230 functions; L50 808; L100 114; D6 0; `M7_anteil` 3.7336.

## Closed — DS-029 AI actor/NPC/narrative split and DS-032 policy-tail support (session 20260528)

| DS-ID | Outcome | Primary files / symbols | Evidence |
|-------|---------|--------------------------|----------|
| DS-029 | NPC agency closure, W5 extraction, voice semantic classification, narrative momentum, post-cut-in follow-up, claim-readiness, and actor-lane hydration now delegate to named semantic helpers. | `build_npc_agency_closure`, `extract_w5_snapshot_from_committed_event`, `classify_voice_semantic_lines`, `derive_narrative_momentum`, `build_post_cut_in_follow_up_event`, `assess_npc_agency_claim_readiness`, `hydrate_actor_lanes` | Pre: `artifacts/workstreams/ai_stack/pre/session_20260528_DS-029_*`; post: `artifacts/workstreams/ai_stack/post/session_20260528_DS-029_comparison.*` |
| DS-032 | Contract policy normalization, context synthesis prompt rendering, and pacing-rhythm derivation use named constants/shared normalization; duplicate local `_coerce_int` / `_string_list` contract helpers were removed. | `normalize_consequence_cascade_policy`, `normalize_callback_web_policy`, `context_synthesis_prompt_lines`, `derive_pacing_rhythm` | Post evidence is recorded under the primary backend workstream: `artifacts/workstreams/backend_runtime_services/post/session_20260528_DS-032_comparison.*` |

**Gates (final):**

- `PYTHONPATH=/mnt/d/WorldOfShadows python -m pytest -q ai_stack/tests/test_npc_agency_long_horizon_claim_readiness.py ai_stack/tests/test_npc_agency_planner.py ai_stack/tests/test_narrative_momentum_engine.py ai_stack/tests/test_pacing_rhythm_engine.py ai_stack/tests/test_phase2_ws_session_loop.py ai_stack/tests/test_runtime_authority_aspects.py --tb=short` — 156 passed.
- `PYTHONPATH=/mnt/d/WorldOfShadows python -m pytest -q ai_stack/tests/test_consequence_cascade_contracts.py ai_stack/tests/test_callback_web_contracts.py ai_stack/tests/test_context_synthesis_engine.py ai_stack/tests/test_context_synthesis_retry_loop.py ai_stack/tests/test_pacing_rhythm_engine.py story_runtime_core/tests/test_callback_web.py story_runtime_core/tests/test_consequence_cascade.py --tb=short` — 40 passed.
- `python -m py_compile` on all changed DS-029/DS-032 AI-stack and story-runtime-core files — passed.
- Final `check --with-metrics` — pass, report generated `2026-05-28T15:25:17Z`.

**Structural delta:** DS-029 leaders are pruned from the current top-12 longest ranking. `derive_pacing_rhythm` is 89 AST lines and has 0 counted magic integer literals; DS-032 contract/context targets have 0 counted magic integer literals in their target functions.

## Closed — DS-026 / DS-027 AI-stack authority and narrative split (session 20260523)

| DS-ID | Outcome | Primary files / symbols | Evidence |
|-------|---------|--------------------------|----------|
| DS-026 | Authority-preview, LangGraph package-output, validation-seam, and block-stream augmentation leaders now delegate to focused section builders. | `_build_adr0041_plan_enforced_runtime_projection_dispatch`, `package_runtime_graph_output`, `run_validation_seam`, `augment_envelope_with_block_stream` | Post: `artifacts/workstreams/ai_stack/post/session_20260523_DS-026-027_authority_narrative_comparison.*` |
| DS-027 | Narrative, telemetry, NPC motivation, pacing, expectation-variation, and contract depth tails now use named derivation helpers; depth-6 tail removed. | `validate_meta_narrative_awareness_realization`, `_build_vitality_telemetry_v1`, `build_pacing_and_silence`, `_candidate_rows`, `_extract_relationship_axis_pressure`, `_safe_dict` | Same post comparison as DS-026. |

**Gates (final):**

- Corrected DS-026 focused suite: `PYTHONPATH=/mnt/d/WorldOfShadows python -m pytest -q ai_stack/tests/test_adr0041_runtime_graph_sidecar.py ai_stack/tests/test_validation_authority_bridge.py ai_stack/tests/test_phase2_dual_mode.py ai_stack/tests/test_god_of_carnage_knowledge_runtime_gates.py ai_stack/tests/test_god_of_carnage_transcript_shell_validation.py ai_stack/tests/test_player_action_resolution.py --tb=short` — 157 passed.
- Explicit package-output diagnostic exposure: `PYTHONPATH=/mnt/d/WorldOfShadows python -m pytest -q ai_stack/tests/test_phase1_live_wiring.py::TestPhase1DiagnosticExposure::test_package_output_exposes_all_phase1_fields_when_present --tb=short` — 1 passed.
- DS-027 focused suite: `PYTHONPATH=/mnt/d/WorldOfShadows python -m pytest -q ai_stack/tests/test_meta_narrative_awareness_engine.py ai_stack/tests/test_expectation_variation_engine.py ai_stack/tests/test_vitality_telemetry_v1.py ai_stack/tests/test_phase2_director_pulse.py ai_stack/tests/test_hierarchical_memory_contracts.py ai_stack/tests/test_god_of_carnage_scene_director_extended.py -k 'pacing or silence or meta_narrative or expectation_variation or vitality or motivation or hierarchical' --tb=short` — 75 passed, 171 deselected.
- `python -m py_compile` on all changed DS-026/DS-027 Python files — passed.
- Final `check --with-metrics` — pass, report generated `2026-05-23T14:33:12Z`.

**Structural delta:** DS-026/DS-027 target symbols are no longer in the formal top-12 longest ranking, and the current full scan has `D6 = 0`. Current full scan: 11076 functions; L50 803; L100 139; D6 0; `M7_anteil` 3.8619.

## Closed — DS-021 / DS-023 / DS-024 AI-stack granularization (session 20260523)

| DS-ID | Outcome | Primary files / symbols | Evidence |
|-------|---------|--------------------------|----------|
| DS-021 | Director/Gathering and narrative derivation leaders now delegate to responder-selection, sensory-layer, relationship-state, and gathering-state helpers. | `build_responder_and_function`, `derive_sensory_context`, `derive_relationship_state`, `compute_gathering_state` | Pre: `artifacts/workstreams/ai_stack/pre/session_20260523_DS-021-023-024_wave_plan.*`; post: `artifacts/workstreams/ai_stack/post/session_20260523_DS-021-023-024_ai_stack_comparison.*` |
| DS-023 | Diagnostics, LDSS, capability, semantic-plan, and forecast builders split into named assembly phases without weakening MVP03/MVP04 semantics. | `build_diagnostics_envelope`, `run_ldss`, `derive_turn_situation_from_runtime_context`, `_director_capability_manager_plan`, `build_branching_forecast` | Same pre/post artefacts as DS-021; tests below. |
| DS-024 | Runtime readiness, temporal control, repro metadata, narrator consequence, authority drift, and adapter extraction depth tails flattened. | `resolve_runtime_readiness_with_adr0041`, `derive_temporal_control`, `build_repro_metadata_and_health`, `build_local_context_transition`, `classify_adr0041_validation_authority_drift`, `_extract_responses_text` | Same pre/post artefacts as DS-021; tests below. |

**Gates (final):**

- `python -m py_compile` on all changed DS-021/023/024 Python files — passed.
- `PYTHONPATH=/mnt/d/WorldOfShadows python -m pytest -q ai_stack/tests/test_god_of_carnage_scene_director_extended.py ai_stack/tests/test_sensory_context_engine.py ai_stack/tests/test_relationship_state_machine.py ai_stack/tests/test_pr_c_director_pause_mode.py --tb=short` — 201 passed.
- `PYTHONPATH=/mnt/d/WorldOfShadows python -m pytest -q tests/gates/test_goc_mvp04_observability_diagnostics_gate.py ai_stack/tests/test_ldss_canonical_step_integration.py ai_stack/tests/test_capability_selector.py tests/branching/test_branching_forecast.py ai_stack/tests/test_semantic_scene_planner.py --tb=short` — 78 passed.
- `PYTHONPATH=/mnt/d/WorldOfShadows python -m pytest -q ai_stack/tests/test_runtime_readiness_consumer.py ai_stack/tests/test_temporal_control_engine.py ai_stack/tests/test_narrator_consequence_contract.py story_runtime_core/tests/test_adapters.py --tb=short` — 64 passed.
- `PYTHONPATH=/mnt/d/WorldOfShadows python -m pytest -q ai_stack/tests/test_adr0041_runtime_graph_sidecar.py ai_stack/tests/test_validation_authority_bridge.py -k 'authority_preview or drift or plan_enforced' --tb=short` — 24 passed, 40 deselected.
- `PYTHONPATH=/mnt/d/WorldOfShadows python -m pytest -q ai_stack/tests/test_langgraph_runtime.py::test_runtime_turn_graph_propagates_trace_and_host_versions ai_stack/tests/test_langgraph_runtime.py::test_runtime_turn_graph_uses_thin_path_for_player_turn ai_stack/tests/test_langgraph_runtime.py::test_runtime_turn_graph_meta_input_uses_non_story_control_path --tb=short` — 3 passed.
- `PYTHONPATH=/mnt/d/WorldOfShadows python -m pytest -q ai_stack/tests/test_temporal_control_engine.py --tb=short` — 3 passed after the final `_select_temporal_operation` flattening.
- Final `check --with-metrics` — pass, report generated `2026-05-23T13:13:11Z`.

**Structural delta:** DS-021/023/024 target symbols are no longer in the formal top-12 longest ranking, and the depth-6 count fell from 9 to 3. Current full scan: 10996 functions; L50 804; L100 149; D6 3; `M7_anteil` 3.908.

## Closed — DS-017 / DS-019 / DS-020 AI-stack granularization (session 20260523)

| DS-ID | Outcome | Primary files / symbols | Evidence |
|-------|---------|--------------------------|----------|
| DS-017 | Telemetry/readout surfaces now delegate to focused helpers while public wrappers remain stable. | `_build_vitality_telemetry_v1`, `build_player_facing_narrative_cards`, `derive_meta_narrative_awareness`, `stream_narrator_blocks` | Pre: `artifacts/workstreams/ai_stack/pre/session_20260523_DS-017-019-020_wave_plan.*`; post: `artifacts/workstreams/ai_stack/post/session_20260523_DS-017-019-020_ai_stack_comparison.*` |
| DS-019 | Runtime policy, autonomous tick, playability rewrite, off-stage commit, and Scenario C registry builders are split into named phases. | `load_module_runtime_policy`, `evaluate_autonomous_tick`, `build_rewrite_instruction`, `commit_off_stage_update_candidates`, `build_scenario_c_registry` | Same pre/post artefacts as DS-017; tests below. |
| DS-020 | Branch timeline, visible narrative, synthetic action resolution, and quality-lab field extraction nesting tails are flattened. | `_snapshot_event_state`, `finalize_visible_scene_blocks`, `build_synthetic_generation_for_action_resolution`, `_field_values` | Same pre/post artefacts as DS-017; tests below. |

**Gates (final):**

- `python -m py_compile` on all changed DS-017/019/020 Python files — passed.
- `pytest -q ai_stack/tests/test_vitality_telemetry_v1.py ai_stack/tests/test_player_narrative_cards.py ai_stack/tests/test_meta_narrative_awareness_engine.py ai_stack/tests/test_narrative_runtime_agent.py --tb=short` — 86 passed.
- `pytest -q ai_stack/tests/test_module_runtime_policy.py ai_stack/tests/test_phase2_autonomous_tick.py ai_stack/tests/test_phase2_stage_f_capability_feeding.py ai_stack/tests/test_phase2_stage_g_off_stage_commits.py ai_stack/tests/test_story_runtime_playability.py tests/branching/test_evaluation_cycle.py --tb=short` — 131 passed.
- `pytest -q tests/branching/test_branch_timeline.py ai_stack/tests/test_visible_narrative_contract.py ai_stack/tests/test_narrator_consequence_contract.py ai_stack/tests/test_return_movement_resolution.py ai_stack/tests/test_quality_lab_pattern_and_planning.py --tb=short` — 59 passed.
- `PYTHONPATH="'fy'-suites" python -m despaghettify.tools wave-plan-validate --file "'fy'-suites/despaghettify/state/artifacts/workstreams/ai_stack/pre/session_20260523_DS-017-019-020_wave_plan.json" --check-primary-paths --gate-prefix-allowlist python,pytest,PYTHONPATH` — pass.
- Final `check --with-metrics` — pass, report generated `2026-05-23T12:06:16Z`.

**Structural delta:** DS-017/019/020 target symbols no longer appear in the current top-12 longest or top-6 nesting rankings. Current full scan: 10840 functions; L50 803; L100 164; D6 9; `M7_anteil` 3.9968.

## Closed — DS-015 duplicate-name proxy triage (session 20260522)

| Sub-wave | Status | Outcome / next step | Evidence |
|----------|--------|---------------------|----------|
| w01 | completed | Added executable duplicate-name proxy classification so intentional public protocol names are not renamed blindly; helper candidates remain queued for centralization. | Pre: `artifacts/workstreams/ai_stack/pre/session_20260522_DS-015_w01_duplicate_proxy_classification_snapshot.*`; post: `artifacts/workstreams/ai_stack/post/session_20260522_DS-015_w01_duplicate_proxy_classification_comparison.*` |
| w02 | completed | Centralized equivalent AI-stack contract/narrative helper families (`_text`, `_clean_str_list`, `_bounded_int`, `_as_list`) without changing public contract methods. | Post: `artifacts/workstreams/ai_stack/post/session_20260522_DS-015_w02_helper_centralization_comparison.*` |
| w03 | completed | Replaced local operational-governance `_do` callback duplicates with route-specific action names while preserving `_handle` behavior. | Pre: `artifacts/workstreams/ai_stack/pre/session_20260522_DS-015_w03_operational_wrapper_snapshot.*`; post: `artifacts/workstreams/ai_stack/post/session_20260522_DS-015_w03_operational_wrapper_comparison.*` |

**w01 gates:**

- `PYTHONPATH="'fy'-suites" python -m despaghettify.tools wave-plan-validate --file "'fy'-suites/despaghettify/state/artifacts/workstreams/ai_stack/pre/session_20260522_DS-015_wave_plan.json" --check-primary-paths --gate-prefix-allowlist python,pytest,PYTHONPATH` — pass
- `python -m py_compile "'fy'-suites/despaghettify/tools/duplicate_name_proxy_classification.py" "'fy'-suites/despaghettify/tools/tests/test_duplicate_name_proxy_classification.py"` — pass
- `PYTHONPATH="'fy'-suites" pytest -q "'fy'-suites/despaghettify/tools/tests/test_duplicate_name_proxy_classification.py" --tb=short` — 3 passed

**w02 gates:**

- `python -m py_compile ai_stack/contracts/*.py ai_stack/story_runtime/narrative/*.py ai_stack/quality_lab/*.py ai_stack/story_runtime/god_of_carnage/god_of_carnage_knowledge_runtime_gates.py ai_stack/story_runtime/semantic_planner/semantic_scene_plan/utils.py story_runtime_core/*.py story_runtime_core/recovery/*.py` — pass
- `pytest -q ai_stack/tests/test_expectation_variation_engine.py ai_stack/tests/test_genre_awareness_engine.py ai_stack/tests/test_improvisational_coherence_engine.py ai_stack/tests/test_information_disclosure_contracts.py ai_stack/tests/test_meta_narrative_awareness_engine.py ai_stack/tests/test_narrative_momentum_engine.py ai_stack/tests/test_symbolic_object_resonance_engine.py ai_stack/tests/test_temporal_control_engine.py ai_stack/tests/test_tonal_consistency_engine.py --tb=short` — 32 passed
- `pytest -q ai_stack/tests/test_god_of_carnage_knowledge_runtime_gates.py ai_stack/tests/test_semantic_planner_contracts.py --tb=short` — 19 passed
- `pytest -q ai_stack/tests/test_active_listening_contracts.py ai_stack/tests/test_hierarchical_memory_contracts.py --tb=short` — 7 passed
- Scoped duplicate-helper grep for `_text`, `_clean_text`, `_clean_str_list`, `_bounded_int`, and `_as_list` — 0 matches

**w03 gates:**

- `python -m py_compile backend/app/api/v1/operational_governance/*.py` — pass
- `PYTHONPATH=backend pytest -q backend/tests/test_operational_governance_routes_structure.py backend/tests/test_operational_governance_mvp.py --tb=short` — 26 passed
- `PYTHONPATH="'fy'-suites" python "'fy'-suites/despaghettify/tools/ds005_runtime_import_check.py"` — exit 0, 12 imports
- `PYTHONPATH="'fy'-suites" python -m despaghettify.tools check --with-metrics --out "'fy'-suites/despaghettify/reports/latest_check_with_metrics.json"` — pass
- Operational-governance `_do` grep — 0 matches

**Final result:** DS-015 targeted package helper and local wrapper duplicate families are closed. Intentional public protocol names (`to_dict`, `to_runtime_dict`, `generate`) remain protected by the classification guard.

## Closed — DS-010 / DS-011 semantic boundary and helper triage (session 20260522)

| DS-ID | Outcome | Primary files / symbols | Evidence |
|-------|---------|--------------------------|----------|
| DS-010 | Runtime-executor semantic boundaries promoted into `semantic_boundaries.py`; `public.py` now consumes the registry instead of owning a loader-local group map. The compatibility facade remains stable. | `ai_stack/langgraph/runtime_executor/semantic_boundaries.py`, `public.py`, `README.md`, `test_runtime_executor_semantic_boundaries.py` | Pre snapshot: `artifacts/workstreams/ai_stack/pre/session_20260522_DS-010-011_semantic_boundaries_duplicate_helpers_snapshot.*`; post comparison/check: `artifacts/workstreams/ai_stack/post/session_20260522_DS-010-011_semantic_boundaries_duplicate_helpers_comparison.*`, `artifacts/workstreams/ai_stack/post/session_20260522_DS-010-011_check_with_metrics.json` |
| DS-011 | Scoped duplicate serialization helper families centralized. `ai_stack/contracts` and `story_runtime_core` no longer redeclare local `_json_safe` / `_as_list`; protocol names `to_dict`, `to_runtime_dict`, and adapter `generate` remain intentional. | `ai_stack/contracts/serialization.py`, `story_runtime_core/serialization.py`, contract modules, story-runtime-core branching/callback/consequence modules, `test_contract_serialization_helpers.py` | Same pre/post artefacts as DS-010; tests below. |

**Gates (final):**

- `python -m py_compile ai_stack/langgraph/runtime_executor/public.py ai_stack/langgraph/runtime_executor/semantic_boundaries.py ai_stack/contracts/serialization.py story_runtime_core/serialization.py ai_stack/contracts/*.py story_runtime_core/branching/*.py story_runtime_core/callbacks/callback_web.py story_runtime_core/consequences/consequence_cascade.py ai_stack/tests/test_runtime_executor_semantic_boundaries.py ai_stack/tests/test_contract_serialization_helpers.py` — pass
- `pytest -q ai_stack/tests/test_runtime_executor_semantic_boundaries.py ai_stack/tests/test_contract_serialization_helpers.py` — 5 passed
- `pytest -q ai_stack/tests/test_responder_reconciliation.py ai_stack/tests/test_runtime_authority_aspects.py ai_stack/tests/test_phase1_live_wiring.py ai_stack/tests/test_phase_c_reaction_order_governance.py ai_stack/tests/test_wave3_multi_actor_vitality.py --tb=short` — 158 passed
- `pytest -q --import-mode=importlib ai_stack/tests/test_temporal_control_engine.py ai_stack/tests/test_tonal_consistency_engine.py ai_stack/tests/test_runtime_aspect_ledger.py story_runtime_core/tests/test_callback_web.py story_runtime_core/tests/test_consequence_cascade.py tests/branching/test_branch_timeline.py tests/branching/test_branching_forecast.py tests/callbacks/test_callback_web.py tests/consequences/test_consequence_cascade.py --tb=short` — 65 passed
- `python tests/run_tests.py --suite ai_stack_langgraph ai_stack_contracts story_runtime_core --quick --continue-on-failure` — pass (58 + 160 + 162 tests)
- `PYTHONPATH="'fy'-suites" python "'fy'-suites/despaghettify/tools/spaghetti_ast_scan.py"` — pass
- `PYTHONPATH="'fy'-suites" python -m despaghettify.tools check --with-metrics --out "'fy'-suites/despaghettify/state/artifacts/workstreams/ai_stack/post/session_20260522_DS-010-011_check_with_metrics.json"` — writes report, exits 1 on known unrelated DS-005 `ModuleNotFoundError: app.runtime.turn_executor`

## Closed — DS-010 runtime executor split (session 20260521)

| Sub-wave | Outcome | Primary files / symbols | Evidence |
|----------|---------|--------------------------|----------|
| w01 | Physical runtime-executor split under 200 lines per file, with clear responsibility names and code-adjacent documentation. This is a transitional loader split; semantic promotion into ordinary modules remains open. | `ai_stack/langgraph/langgraph_runtime_executor.py`, `ai_stack/langgraph/runtime_executor/`; `_build_dramatic_generation_packet`, `_assemble_model_context`, `_director_select_dramatic_parameters`, `_interpret_input`, `_resolve_player_action` | Pre snapshot: `artifacts/workstreams/ai_stack/pre/session_20260521_DS-010_runtime_executor_split_snapshot.*`; post comparison: `artifacts/workstreams/ai_stack/post/session_20260521_DS-010_w01_runtime_executor_split_comparison.*` |

**Current structure:** `ai_stack/langgraph/langgraph_runtime_executor.py` is a compatibility facade. `ai_stack/langgraph/runtime_executor/public.py` assembles named source groups from `ai_stack/langgraph/runtime_executor/*.py`. Every segment file now has a responsibility-specific module docstring, and `ai_stack/langgraph/runtime_executor/README.md` explains the loader, responsibility groups, segment docstrings, and next extraction pass.

**Gates so far:**

- `python -m compileall -q ai_stack/langgraph/langgraph_runtime_executor.py ai_stack/langgraph/runtime_executor` — pass
- File-line check for facade + staging package — pass; max 186 lines, 0 files over 200, 0 numbered suffix names
- `pytest ai_stack/tests/test_responder_reconciliation.py ai_stack/tests/test_runtime_authority_aspects.py ai_stack/tests/test_phase1_live_wiring.py -q --tb=short` — 93 passed
- `pytest ai_stack/tests/test_phase_c_reaction_order_governance.py -q --tb=short` — 27 passed
- `pytest ai_stack/tests/test_wave3_multi_actor_vitality.py -q --tb=short` — 38 passed
- `PYTHONPATH="'fy'-suites" python "'fy'-suites/despaghettify/tools/spaghetti_ast_scan.py"` — pass; executor leaders no longer appear in top longest/nesting rankings
- `PYTHONPATH="'fy'-suites" python -m docify.tools audit --root ai_stack/langgraph/runtime_executor --json --out "'fy'-suites/docify/reports/ds010_runtime_executor_doc_audit.json" --exit-zero` — pass; 0 findings, 0 parse errors after responsibility-specific module docstrings
- `PYTHONPATH="'fy'-suites" python -m docify.tools drift --paths-file /tmp/ds010_docify_paths.txt --json --out "'fy'-suites/docify/reports/ds010_runtime_executor_doc_drift.json"` — pass; report written
- `git diff --check` for touched executor/despaghettify report files — pass

**Caveat:** `check --with-metrics` writes `../reports/latest_check_with_metrics.json` but exits 1 because the existing DS-005 runtime import check cannot import `app.runtime.turn_executor` in the current tree. That is outside this executor split.

**Next DS-010 pass:** promote `SOURCE_LINES` chunks into ordinary Python modules by responsibility group, starting with semantic input, actor lanes, retrieval, dramatic packet, and director context. Keep the compatibility facade until direct imports move to stable module names.

## Closed — DS-008 (session 20260520)

| Sub-wave | Goal | Primary files / symbols | Gate |
|----------|------|--------------------------|------|
| 1 | Extract the LangGraph runtime aspect validation orchestration into a focused module while preserving the existing executor export and validation contract. | `ai_stack/langgraph/langgraph_runtime_executor.py`, `ai_stack/langgraph/langgraph_runtime_validation.py`; `_build_runtime_aspect_validation` | `python -m compileall -q ai_stack/langgraph`; `pytest ai_stack/tests/test_character_voice_runtime_enforcement.py ai_stack/tests/test_runtime_authority_aspects.py -q --tb=short`; `python tests/run_tests.py --suite ai_stack_narrative ai_stack_quality --quick` |
| 2 | Thin the validation seam retry/context surface around the extracted validation module without changing graph node behavior. | `ai_stack/langgraph/langgraph_runtime_executor.py`; `_validate_seam` | `python -m compileall -q ai_stack/langgraph`; `pytest ai_stack/tests/test_langgraph_runtime.py ai_stack/tests/test_character_voice_runtime_enforcement.py ai_stack/tests/test_runtime_authority_aspects.py -q --tb=short`; `python tests/run_tests.py --suite ai_stack_graph ai_stack_narrative ai_stack_quality --quick`; `PYTHONPATH="'fy'-suites" DESPAG_SKIP_ARCHIVE_SYNC=1 python -m despaghettify.tools.hub_cli check --with-metrics --out "'fy'-suites/despaghettify/reports/latest_check_with_metrics.json"` |

**Plan mirror:** `artifacts/workstreams/ai_stack/pre/session_20260520_DS-008_wave_plan.json`

**Outcome:** `_build_runtime_aspect_validation` moved behind a stable executor wrapper into `ai_stack/langgraph/langgraph_runtime_validation.py`; `_validate_seam` now delegates validation seam execution, retry feedback assembly, retry attempt record assembly, and validation update copying. Formal scan no longer lists either DS-008 primary symbol in top longest/nesting rankings.

**Gates (final):**

- `python -m compileall -q ai_stack/langgraph` — pass
- `pytest ai_stack/tests/test_langgraph_runtime.py ai_stack/tests/test_character_voice_runtime_enforcement.py ai_stack/tests/test_runtime_authority_aspects.py -q --tb=short` — 51 passed
- `python tests/run_tests.py --suite ai_stack_graph ai_stack_narrative ai_stack_quality --quick` — pass
- `check --with-metrics` — pass, report `2026-05-20T19:32:19Z`

**Post artefacts:** `artifacts/workstreams/ai_stack/post/session_20260520_DS-008_w01_runtime_validation_comparison.*`, `artifacts/workstreams/ai_stack/post/session_20260520_DS-008_w02_validation_seam_comparison.*`

## Closed — DS-003, DS-005 (session 20260520)

RAG module split + shared GoC YAML cache fixture (C6). Validation seam extracted to `goc_turn_seams_validation.py` (C7).

**Gates (final):**

- `python tests/run_tests.py --suite ai_stack_goc ai_stack_retrieval_research --quick` — pass
- `pytest ai_stack/tests/test_w5_actor_situation_validation.py ai_stack/tests/test_goc_transcript_shell_validation.py ai_stack/tests/test_goc_runtime_graph_seams_and_diagnostics.py` — 27 passed

**Post artefacts:** `artifacts/workstreams/ai_stack/post/session_20260520_DS-003-005_*.json`
