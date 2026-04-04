# A2 Repair Gate Report — Authoritative Narrative Commit (World-Engine)

Date: 2026-04-04

Verification run: 2026-04-04 (repair block re-audit)

## 1. Scope completed

- Split **committed turn history** from **full diagnostic envelopes** inside `StoryRuntimeManager.execute_turn`.
- `session.history` now stores lean **committed records** (interpretation, progression verdict, post-turn session snapshot, turn outcome) without graph/retrieval payloads.
- `session.diagnostics` continues to store the **full turn envelope** returned from API responses (includes `graph`, `retrieval`, `model_route`) for orchestration and debugging.
- Exposed `last_committed_turn` on `GET /api/story/sessions/{id}/state` and `committed_history_tail` plus `diagnostics_kind` on diagnostics for clearer consumer semantics.
- Extended tests to prove diagnostics still carry graph data while committed tail records do not.

## 2. Files changed

- `world-engine/app/story_runtime/manager.py`
- `world-engine/tests/test_story_runtime_rag_runtime.py`
- `world-engine/tests/test_story_runtime_api.py`
- `docs/reports/ai_stack_gates/A2_REPAIR_GATE_REPORT.md`

## 3. What is truly committed runtime state

- Live fields on `StorySession`: `current_scene_id`, `turn_counter`, `updated_at`, `runtime_projection` (immutable projection for the session), `module_id`.
- Each `session.history` entry: `turn_number`, `raw_input`, `interpreted_input`, `progression_commit`, `turn_outcome` (`ok` | `degraded`), `committed_state_after` (scene + counter after the turn), `trace_id`.
- HTTP turn responses remain the **full envelope** (backward compatible for callers expecting `graph` on the turn object).

## 4. What remains diagnostic / orchestration only

- `session.diagnostics` entries: full `event` including `retrieval`, `model_route`, LangGraph `graph` diagnostics, capability audit, repro metadata.
- `diagnostics_kind` explains that the `diagnostics` array holds orchestration envelopes, not a substitute for `current_scene_id` / `history`.

## 5. Tests added/updated

- Updated `world-engine/tests/test_story_runtime_rag_runtime.py::test_story_runtime_builds_multi_turn_committed_progression` — asserts full graph in diagnostics, absence of `graph` in committed tail, committed scene in tail.
- Updated `world-engine/tests/test_story_runtime_api.py::test_story_session_lifecycle_and_nl_interpretation` — asserts `last_committed_turn` on state and no `graph` key there.
- Regression suite: all `test_story_runtime_rag_runtime.py`, `test_story_runtime_api.py`, `test_trace_middleware.py`.

## 6. Exact test commands run

```powershell
cd world-engine
python -m pytest tests/test_story_runtime_api.py tests/test_story_runtime_rag_runtime.py tests/test_trace_middleware.py -v --tb=short
```

```powershell
cd ..\backend
python -m pytest tests/test_session_routes.py -k "authoritative or diagnostics_prefers_world_engine or state_prefers_world_engine or execute_turn_proxies" -v --tb=short
python -m pytest tests/test_session_api_closure.py -k "post_execute_turn_proxies_to_world_engine" -v --tb=short
```

## 7. Verdict: Pass / Partial / Fail

**Pass**

## 8. Reason for verdict

- Legal turns still mutate `current_scene_id` only through `_commit_progression` with explicit allow/deny reasons.
- Multi-turn and illegal-transition tests still pass; diagnostics align with committed progression fields.
- Committed history is now **structurally distinct** from graph-heavy diagnostics, so consumers are not encouraged to treat diagnostics as the sole source of narrative truth.

## 9. Remaining risk

- Sparse `transition_hints` still block progression commits by design (`transition_hints_missing`).
- Scene proposal extraction remains conservative (explicit movement / scene tokens); richer NL-to-scene inference is future work.
