# B2 Repair Gate Report — LangGraph Dependency and Runtime Hardening

Date: 2026-04-04

## 1. Scope completed

- Declared LangGraph as an explicit dependency in backend and world-engine requirement sets.
- Hardened LangGraph import/runtime behavior in `wos_ai_stack/langgraph_runtime.py`.
- Added explicit dependency guard (`ensure_langgraph_available`) for graph constructors.
- Added test coverage for missing-dependency failure mode and healthy graph execution paths.

## 2. Files changed

- `wos_ai_stack/langgraph_runtime.py`
- `wos_ai_stack/tests/test_langgraph_runtime.py`
- `wos_ai_stack/__init__.py`
- `backend/requirements.txt`
- `world-engine/requirements.txt`
- `docs/architecture/langgraph_runtime_install_and_failure_modes.md`
- `docs/reports/ai_stack_gates/B2_REPAIR_GATE_REPORT.md`

## 3. What is truly wired

- Runtime turn graph and seed graph builders now verify LangGraph availability before graph construction.
- Missing/misconfigured LangGraph now fails with explicit, readable runtime error text.
- Healthy runtime path remains executable and test-covered for:
  - runtime turn graph
  - writers-room seed graph
  - improvement seed graph

## 4. What remains incomplete

- This milestone hardens dependency/runtime reliability; it does not redesign orchestration semantics.
- Environment provisioning still requires operators to install dependencies from requirements files before runtime startup.

## 5. Tests added/updated

- Updated: `wos_ai_stack/tests/test_langgraph_runtime.py`
  - added `test_langgraph_missing_dependency_raises_honest_runtime_error`
  - retained graph execution tests for healthy mode
- Existing integration suites re-run:
  - world-engine runtime API and manager tests
  - backend writers-room route tests

## 6. Exact test commands run

```powershell
cd ..
$env:PYTHONPATH='.'
python -m pytest wos_ai_stack/tests/test_langgraph_runtime.py wos_ai_stack/tests/test_langchain_integration.py
```

```powershell
cd world-engine
python -m pytest tests/test_story_runtime_api.py tests/test_story_runtime_rag_runtime.py tests/test_trace_middleware.py
```

```powershell
cd ..\backend
python -m pytest tests/test_writers_room_routes.py
```

## 7. Pass / Partial / Fail

Pass

## 8. Reason for the verdict

- LangGraph dependency is now explicitly declared for intended runtime environments.
- LangGraph modules import and execute successfully in real test runs.
- Missing dependency path now fails honestly with explicit runtime guidance.
- Runtime outputs remain coherent with existing story runtime expectations in world-engine tests.

## 9. Risks introduced or remaining

- Strict dependency guard means environments with stale installs fail early (intended), requiring disciplined dependency management.
- Dependency ranges can still drift over time; regular lock/compatibility review remains necessary.
