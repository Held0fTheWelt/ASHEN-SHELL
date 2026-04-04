# A1 Repair Gate Report — Free Natural Input Primary Runtime Path

Date: 2026-04-04

## 1. Scope completed

- Replaced frontend queue-only play execute behavior with real runtime turn dispatch.
- Wired frontend play shell to create and cache backend runtime session bindings per run.
- Preserved explicit command handling while keeping free natural input as the default UX path.
- Added execution-focused tests for frontend route wiring and World-Engine input behavior (speech/action/mixed/command/ambiguous).
- Updated input interpretation contract and added an A1 runtime path architecture note.

## 2. Files changed

- `frontend/app/routes.py`
- `frontend/templates/session_shell.html`
- `frontend/tests/test_routes_extended.py`
- `world-engine/tests/test_story_runtime_api.py`
- `backend/tests/test_session_api_closure.py`
- `backend/tests/test_session_routes.py`
- `docs/architecture/player_input_interpretation_contract.md`
- `docs/architecture/a1_free_input_primary_runtime_path.md`
- `docs/reports/ai_stack_gates/A1_REPAIR_GATE_REPORT.md`

## 3. What is truly wired

- Frontend `/play/<run_id>/execute` now calls backend `POST /api/v1/sessions/<backend_session_id>/turns` with `player_input`.
- Backend turn route executes shared interpreter preview and proxies to World-Engine authoritative story runtime.
- World-Engine turn execution classifies and executes natural and command input through runtime graph execution.
- Frontend shell copy now reflects true runtime behavior instead of queue-only semantics.

## 4. What remains incomplete

- Run metadata normalization between play-service run identity and backend module identity is still indirect; frontend currently binds backend session creation using selected template id.
- No additional websocket turn-submit path was introduced in this milestone; HTTP runtime turn path is the canonical executable path.

## 5. Tests added/updated

- Updated: `frontend/tests/test_routes_extended.py`
  - `test_play_create_success` (stores run-to-module mapping)
  - `test_play_shell_ticket_ok_and_error` (creates backend session binding)
  - `test_play_execute_empty_and_runtime_dispatch` (verifies real turn dispatch)
  - `test_play_execute_rejects_missing_backend_session_binding`
- Added: `world-engine/tests/test_story_runtime_api.py::test_story_turns_cover_primary_free_input_paths`
- Updated legacy contract test: `backend/tests/test_session_api_closure.py::test_post_execute_turn_proxies_to_world_engine`
- Updated monkeypatch signatures for trace-aware bridge calls:
  - `backend/tests/test_session_routes.py`
  - `backend/tests/test_session_api_closure.py`

## 6. Exact test commands run

```powershell
cd frontend
python -m pytest tests/test_routes_extended.py -k "play_shell_ticket_ok_and_error or play_execute_empty_and_runtime_dispatch or play_execute_rejects_missing_backend_session_binding"
python -m pytest tests/test_routes_extended.py
```

```powershell
cd world-engine
python -m pytest tests/test_story_runtime_api.py -k "lifecycle or primary_free_input_paths"
```

```powershell
cd backend
python -m pytest tests/test_session_routes.py tests/test_session_api_closure.py -k "execute_turn or turns"
```

```powershell
cd ..
$env:PYTHONPATH='.'
python -m pytest story_runtime_core/tests/test_input_interpreter.py
```

## 7. Pass / Partial / Fail

Pass

## 8. Reason for the verdict

- The intended playable frontend path now executes free natural input as a real runtime turn (no queue-only fallback in the repaired path).
- Interpreter outputs are used in executed turn payloads and runtime diagnostics.
- Tests cover execution behavior across natural speech, natural action, mixed input, explicit command input, ambiguous input continuation, and UI-facing route dispatch into runtime execution.

## 9. Risks introduced or remaining

- If template ids diverge from backend module ids in future content pipelines, frontend run-to-backend binding may fail to create backend runtime sessions for some runs.
- Session bindings are currently stored in frontend session state; loss of browser session requires re-establishing bindings by re-entering play flow.
