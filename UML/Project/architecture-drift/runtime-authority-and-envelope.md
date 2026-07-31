# Better Tomorrow runtime authority and envelope drift edges

This projection is generated from the machine-readable drift-edge catalog. Edit the catalog, never this file.

[PlantUML source](runtime-authority-and-envelope.puml)

## Drift edges

| Edge | From | To | Effect | Claims | Carried fields | Source |
| --- | --- | --- | --- | --- | --- | --- |
| `runtime-compatibility-delegation` | `world-engine:runtime` | `world-engine:manager` | `compatibility_delegate` | `DRIFT-001`, `DRIFT-006` | `validated_command` | [`world-engine/world_engine/runtime/manager.py`](../../../world-engine/world_engine/runtime/manager.py) |
| `authored-module-to-compiler` | `content-authority:module` | `content-authority:compiler` | `content_projection` | `DRIFT-004` | `content_version`, `source_provenance` | [`backend/app/content/module_loader.py`](../../../backend/app/content/module_loader.py) |
| `compiler-to-module-validator` | `content-authority:compiler` | `content-authority:validator` | `content_projection` | `DRIFT-004` | `content_version`, `source_provenance` | [`backend/app/content/module_validator.py`](../../../backend/app/content/module_validator.py) |
| `validated-content-to-world-loader` | `content-authority:validator` | `content-authority:world_loader` | `content_projection` | `DRIFT-004` | `content_version`, `source_provenance` | [`world-engine/world_engine/content/backend_loader.py`](../../../world-engine/world_engine/content/backend_loader.py) |
| `world-content-to-ai-adapter` | `content-authority:world_loader` | `content-authority:ai_adapter` | `content_projection` | `DRIFT-004` | `content_version`, `source_provenance` | [`ai_stack/story_runtime/god_of_carnage/god_of_carnage_yaml_authority.py`](../../../ai_stack/story_runtime/god_of_carnage/god_of_carnage_yaml_authority.py) |
| `canonical-constraints-to-runtime` | `content-authority:canonical_path` | `world-engine:manager` | `read_only_constraint` | `DRIFT-005` | `canonical_constraints`, `content_version` | [`content/modules/god_of_carnage/canonical_path/_schema.yaml`](../../../content/modules/god_of_carnage/canonical_path/_schema.yaml) |
| `planner-to-runtime-proposal` | `ai-stack:director` | `ai-stack:proposal` | `proposal_flow` | `DRIFT-002`, `DRIFT-003` | `selected_scene_function`, `primary_responder_id`, `continuity_impacts`, `dramatic_effect_gate` | [`ai_stack/langgraph/langgraph_runtime_package_output_sections.py`](../../../ai_stack/langgraph/langgraph_runtime_package_output_sections.py) |
| `proposal-to-ai-validation` | `ai-stack:proposal` | `ai-stack:validator` | `proposal_flow` | `DRIFT-002`, `DRIFT-003` | `selected_scene_function`, `primary_responder_id`, `continuity_impacts`, `dramatic_effect_gate` | [`ai_stack/langgraph/runtime_executor/executor_validation_commit.py`](../../../ai_stack/langgraph/runtime_executor/executor_validation_commit.py) |
| `ai-validation-to-proposal-finalization` | `ai-stack:validator` | `ai-stack:proposal` | `proposal_finalize` | `DRIFT-002` | `selected_scene_function`, `primary_responder_id`, `continuity_impacts`, `dramatic_effect_gate` | [`ai_stack/langgraph/runtime_executor/executor_run_finish.py`](../../../ai_stack/langgraph/runtime_executor/executor_run_finish.py) |
| `runtime-proposal-to-world-bridge` | `ai-stack:proposal` | `world-engine:ai_bridge` | `proposal_flow` | `DRIFT-002`, `DRIFT-003` | `selected_scene_function`, `primary_responder_id`, `continuity_impacts`, `dramatic_effect_gate` | [`world-engine/world_engine/story_runtime/governed_runtime_adapters.py`](../../../world-engine/world_engine/story_runtime/governed_runtime_adapters.py) |
| `world-bridge-to-commit-validation` | `world-engine:ai_bridge` | `world-engine:validation` | `proposal_flow` | `DRIFT-002`, `DRIFT-003`, `DRIFT-005` | `selected_scene_function`, `primary_responder_id`, `continuity_impacts`, `dramatic_effect_gate` | [`world-engine/world_engine/story_runtime/narrative_commit_resolution.py`](../../../world-engine/world_engine/story_runtime/narrative_commit_resolution.py) |
| `world-validation-authoritative-write` | `world-engine:validation` | `world-engine:store` | `authoritative_write` | `DRIFT-001`, `DRIFT-002`, `DRIFT-003`, `DRIFT-005` | `selected_scene_function`, `primary_responder_id`, `continuity_impacts`, `dramatic_effect_gate`, `beat_progression`, `commit_contract_version` | [`world-engine/world_engine/story_runtime/story_session_store.py`](../../../world-engine/world_engine/story_runtime/story_session_store.py) |
| `committed-state-to-delivery` | `world-engine:store` | `world-engine:delivery` | `visible_projection` | `DRIFT-003`, `DRIFT-005`, `DRIFT-007` | `selected_scene_function`, `primary_responder_id`, `beat_progression`, `visible_blocks`, `speaker_identity` | [`world-engine/world_engine/story_runtime/manager/story_window_entry_parts.py`](../../../world-engine/world_engine/story_runtime/manager/story_window_entry_parts.py) |
| `delivery-to-frontend-stream` | `world-engine:delivery` | `frontend:stream` | `visible_projection` | `DRIFT-007` | `visible_blocks`, `speaker_identity` | [`world-engine/world_engine/api/story_ws.py`](../../../world-engine/world_engine/api/story_ws.py) |
| `frontend-stream-to-renderer` | `frontend:stream` | `frontend:renderer` | `visible_projection` | `DRIFT-007` | `visible_blocks`, `speaker_identity` | [`frontend/static/play_block_renderer.js`](../../../frontend/static/play_block_renderer.js) |
| `trace-backend-to-world` | `observability-traceability:backend` | `observability-traceability:world` | `evidence_flow` | `DRIFT-008` | `trace_id`, `session_id` | [`backend/app/api/v1/game/player_turn_trace_start.py`](../../../backend/app/api/v1/game/player_turn_trace_start.py) |
| `trace-world-to-ai` | `observability-traceability:world` | `observability-traceability:ai` | `evidence_flow` | `DRIFT-008` | `trace_id`, `session_id` | [`ai_stack/langfuse/langfuse_evidence.py`](../../../ai_stack/langfuse/langfuse_evidence.py) |
| `trace-ai-to-operator-projection` | `observability-traceability:ai` | `observability-traceability:projection` | `evidence_flow` | `DRIFT-008` | `trace_id`, `completeness`, `redaction_status` | [`world-engine/world_engine/web/static/ui_traces.js`](../../../world-engine/world_engine/web/static/ui_traces.js) |
| `integration-evidence-to-report` | `quality-gates:integration` | `quality-gates:report` | `evidence_flow` | `DRIFT-009` | `suite_id`, `execution_result`, `disposable_state_proof` | [`tests/architecture_assurance/test_disposable_akdb_integration.py`](../../../tests/architecture_assurance/test_disposable_akdb_integration.py) |
| `quality-report-to-ci` | `quality-gates:report` | `quality-gates:ci` | `evidence_flow` | `DRIFT-009` | `suite_id`, `execution_result`, `disposable_state_proof` | [`.github/workflows/architecture-assurance.yml`](../../../.github/workflows/architecture-assurance.yml) |
| `model-call-to-cost-ledger` | `story-runtime-core:adapters` | `ai-stack:ledger` | `evidence_flow` | `DRIFT-008` | `phase`, `attempt_index`, `input_tokens`, `output_tokens` | [`story_runtime_core/model_call_accounting.py`](../../../story_runtime_core/model_call_accounting.py) |
| `ledger-to-langfuse-observation` | `ai-stack:ledger` | `observability-traceability:ai` | `evidence_flow` | `DRIFT-008` | `phase`, `attempt_index`, `call_count` | [`story_runtime_core/model_call_accounting.py`](../../../story_runtime_core/model_call_accounting.py) |
| `runtime-manager-live-run-write` | `world-engine:runtime` | `world-engine:store` | `authoritative_write` | `DRIFT-001` | `runtime_profile_handoff` | [`world-engine/world_engine/runtime/manager.py`](../../../world-engine/world_engine/runtime/manager.py) |
| `manager-branching-tree-write` | `world-engine:manager` | `world-engine:store` | `authoritative_write` | `DRIFT-001` | `tree_id` | [`world-engine/world_engine/story_runtime/manager/session/manager_init_and_persistence.py`](../../../world-engine/world_engine/story_runtime/manager/session/manager_init_and_persistence.py) |
| `manager-branch-timeline-write` | `world-engine:manager` | `world-engine:store` | `authoritative_write` | `DRIFT-001` | `timeline_id` | [`world-engine/world_engine/story_runtime/manager/session/manager_init_and_persistence.py`](../../../world-engine/world_engine/story_runtime/manager/session/manager_init_and_persistence.py) |
| `manager-callback-web-write` | `world-engine:manager` | `world-engine:store` | `authoritative_write` | `DRIFT-001` | `callback_web_id` | [`world-engine/world_engine/story_runtime/manager/session/manager_init_and_persistence.py`](../../../world-engine/world_engine/story_runtime/manager/session/manager_init_and_persistence.py) |
| `manager-consequence-cascade-write` | `world-engine:manager` | `world-engine:store` | `authoritative_write` | `DRIFT-001` | `cascade_id` | [`world-engine/world_engine/story_runtime/manager/session/manager_init_and_persistence.py`](../../../world-engine/world_engine/story_runtime/manager/session/manager_init_and_persistence.py) |

## Authority invariants

- `single-live-story-session-writer`: `world-engine:validation` is the only writer of `live_story_session` and writes through `world-engine:store`.
- `single-live-run-instance-writer`: `world-engine:runtime` is the only writer of `live_run_instance` and writes through `world-engine:store`.
- `single-branching-tree-writer`: `world-engine:manager` is the only writer of `branching_tree` and writes through `world-engine:store`.
- `single-branch-timeline-writer`: `world-engine:manager` is the only writer of `branch_timeline` and writes through `world-engine:store`.
- `single-callback-web-writer`: `world-engine:manager` is the only writer of `callback_web` and writes through `world-engine:store`.
- `single-consequence-cascade-writer`: `world-engine:manager` is the only writer of `consequence_cascade` and writes through `world-engine:store`.

## Source write-surface guards

| Guard | Resource | Sink call | Allowed callsites |
| --- | --- | --- | --- |
| `live-story-session-json-save-callsite` | `live_story_session` | `self._session_store.save` | `world-engine/world_engine/story_runtime/manager/session/manager_init_and_persistence.py::_persist_session` |
| `live-run-instance-store-save-callsite` | `live_run_instance` | `self.store.save` | `world-engine/world_engine/runtime/manager.py::attach_runtime_profile_handoff`<br>`world-engine/world_engine/runtime/manager.py::bind_story_session`<br>`world-engine/world_engine/runtime/manager.py::_bootstrap_instance`<br>`world-engine/world_engine/runtime/manager.py::find_or_join_run`<br>`world-engine/world_engine/runtime/manager.py::connect`<br>`world-engine/world_engine/runtime/manager.py::disconnect`<br>`world-engine/world_engine/runtime/manager.py::process_command` |
| `branching-tree-store-save-callsite` | `branching_tree` | `self._branching_tree_store.save` | `world-engine/world_engine/story_runtime/manager/session/manager_init_and_persistence.py::_persist_branching_tree_record` |
| `branch-timeline-store-save-callsite` | `branch_timeline` | `self._branch_timeline_store.save` | `world-engine/world_engine/story_runtime/manager/session/manager_init_and_persistence.py::_persist_branch_timeline_record` |
| `callback-web-store-save-callsite` | `callback_web` | `self._callback_web_store.save` | `world-engine/world_engine/story_runtime/manager/session/manager_init_and_persistence.py::_persist_callback_web_record` |
| `consequence-cascade-store-save-callsite` | `consequence_cascade` | `self._consequence_cascade_store.save` | `world-engine/world_engine/story_runtime/manager/session/manager_init_and_persistence.py::_persist_consequence_cascade_record` |

## Envelope invariants

### `dramatic-turn-envelope-v1`

Path: `planner-to-runtime-proposal` → `runtime-proposal-to-world-bridge` → `world-bridge-to-commit-validation` → `world-validation-authoritative-write` → `committed-state-to-delivery`

| Field | Introduced | Required through |
| --- | --- | --- |
| `selected_scene_function` | `planner-to-runtime-proposal` | `committed-state-to-delivery` |
| `primary_responder_id` | `planner-to-runtime-proposal` | `committed-state-to-delivery` |
| `continuity_impacts` | `planner-to-runtime-proposal` | `world-validation-authoritative-write` |
| `dramatic_effect_gate` | `planner-to-runtime-proposal` | `world-validation-authoritative-write` |
| `beat_progression` | `world-validation-authoritative-write` | `committed-state-to-delivery` |
| `commit_contract_version` | `world-validation-authoritative-write` | `world-validation-authoritative-write` |

### `player-visible-block-envelope-v1`

Path: `committed-state-to-delivery` → `delivery-to-frontend-stream` → `frontend-stream-to-renderer`

| Field | Introduced | Required through |
| --- | --- | --- |
| `visible_blocks` | `committed-state-to-delivery` | `frontend-stream-to-renderer` |
| `speaker_identity` | `committed-state-to-delivery` | `frontend-stream-to-renderer` |
