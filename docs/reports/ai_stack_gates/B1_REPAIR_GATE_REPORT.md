# B1 Repair Gate Report — LangChain Integration Normalization

Date: 2026-04-04

Verification run: 2026-04-04 (repair block re-audit)

## 1. Scope completed

- Documented the **canonical LangChain integration surface** in `wos_ai_stack.langchain_integration` so call sites can route through one module instead of scattering LangChain imports.
- Re-verified runtime turn graph uses `invoke_runtime_adapter_with_langchain` (prompt + structured parse) and writers-room uses retriever + `StructuredTool` bridges.
- Confirmed integration tests cover parser, retriever bridge, tool bridge, and a combined run.

## 2. Files changed

- `wos_ai_stack/langchain_integration/__init__.py`
- `docs/reports/ai_stack_gates/B1_REPAIR_GATE_REPORT.md`

## 3. Where LangChain is truly used

- **Runtime turn graph** (`wos_ai_stack/langgraph_runtime.py` → `invoke_runtime_adapter_with_langchain`): model prompt rendering and optional Pydantic parse; metadata exposes `langchain_prompt_used` and parser errors.
- **Writers-room workflow** (`backend/app/services/writers_room_service.py`): LangChain retriever bridge for document preview and capability tool bridge for review bundle invocation.
- **World-Engine story runtime**: inherits the above via `RuntimeTurnGraphExecutor` inside `StoryRuntimeManager`.

## 4. Where LangChain is intentionally not used

- Legacy backend in-process runtime modules, forum/wiki paths, and non-AI routes.
- WebSocket live-run engine (command/say/emote path) does not use this stack.

## 5. Tests added/updated

- Existing suite unchanged; re-run confirms green:
  - `wos_ai_stack/tests/test_langchain_integration.py` (including combined bridge test)
  - `wos_ai_stack/tests/test_langgraph_runtime.py`
  - `backend/tests/test_writers_room_routes.py`
  - `world-engine/tests/test_story_runtime_api.py` and `test_story_runtime_rag_runtime.py`

## 6. Exact test commands run

```powershell
cd ..
$env:PYTHONPATH='.'
python -m pytest wos_ai_stack/tests/test_langchain_integration.py wos_ai_stack/tests/test_langgraph_runtime.py -v --tb=short
```

```powershell
cd backend
python -m pytest tests/test_writers_room_routes.py -v --tb=short
```

```powershell
cd ..\world-engine
python -m pytest tests/test_story_runtime_api.py tests/test_story_runtime_rag_runtime.py -q --tb=line
```

## 7. Pass / Partial / Fail

**Pass**

## 8. Reason for verdict

- LangChain remains a declared dependency in runtime requirement sets (unchanged this milestone).
- Multiple active paths (runtime graph + writers-room) exercise the normalized package.
- Tests verify real usage rather than optional stubs.

## 9. Dependency / environment blockers

- None observed on Python 3.13.12 during this verification run.
