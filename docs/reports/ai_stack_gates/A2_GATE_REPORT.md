# A2 Gate Report — World-Engine Authoritative Narrative Runtime Host

Date: 2026-04-04

## Scope completed

- Hardened backend-facing consumer endpoints to read authoritative story runtime data from world-engine when a world-engine story session is bound.
- Kept world-engine as the host that executes and commits narrative turns/progression.
- Preserved compatibility behavior when a world-engine story session has not been initialized yet.
- Added backend tests that prove consumer surfaces return authoritative state/diagnostics/snapshot payloads from world-engine bindings.

## Files changed

- `backend/app/api/v1/session_routes.py`
- `backend/tests/test_session_routes.py`
- `docs/reports/ai_stack_gates/A2_GATE_REPORT.md`
- `docs/reports/ai_stack_gates/A2_TO_E1_SEQUENTIAL_EXECUTION_PLAN.md`

## True runtime path now used

- Authoritative turn execution and progression commit remains in world-engine:
  - `world-engine /api/story/sessions/{id}/turns` -> `StoryRuntimeManager.execute_turn`.
- Backend session consumer surfaces now prefer world-engine truth when the bridge metadata contains `world_engine_story_session_id`:
  - `GET /api/v1/sessions/{id}`
  - `GET /api/v1/sessions/{id}/state`
  - `GET /api/v1/sessions/{id}/diagnostics`
- Backend still acts as policy/review/governance consumer and bridge, not as the authoritative story host.

## Remaining limitations

- Backend in-memory session structures are still retained for compatibility and pre-binding flows.
- If world-engine is unavailable, backend consumer endpoints return bridge error metadata and fallback warnings.
- This milestone does not remove legacy in-process runtime modules used outside the live story-turn bridge path; it enforces authority on the live story session consumer path.

## Tests added/updated

- Updated `backend/tests/test_session_routes.py`:
  - `test_get_session_prefers_world_engine_authoritative_snapshot_when_bound`
  - `test_get_state_prefers_world_engine_authoritative_state_when_bound`
  - `test_get_diagnostics_prefers_world_engine_authoritative_payload`
- Existing world-engine progression commit tests executed:
  - `world-engine/tests/test_story_runtime_rag_runtime.py` progression tests
- Existing backend bridge proxy test executed:
  - `backend/tests/test_session_api_closure.py::test_post_execute_turn_proxies_to_world_engine`

## Exact test commands run

```powershell
cd backend
python -m pytest tests/test_session_routes.py -k "authoritative or diagnostics_prefers_world_engine or state_prefers_world_engine or execute_turn_proxies_to_world_engine"
python -m pytest tests/test_session_api_closure.py -k "post_execute_turn_proxies_to_world_engine"
```

```powershell
cd world-engine
python -m pytest tests/test_story_runtime_rag_runtime.py -k "commits_legal_scene_progression or rejects_illegal_scene_progression or builds_multi_turn_committed_progression"
```

## Verdict

Pass

## Reason for verdict

- World-engine remains the authoritative host that executes and commits narrative turns.
- Backend-facing consumers now read authoritative story state/diagnostics from world-engine-bound sessions instead of only exposing local placeholders.
- Progression commit behavior is verified in world-engine tests, and backend bridge consumers are verified to read authoritative host data.
