# B2-next Gate Report — Deepen LangGraph orchestration layer

Date: 2026-04-04

## 1. Scope completed

- Added **`wos_ai_stack/runtime_turn_contracts.py`** with stable `ExecutionHealth` / `AdapterInvocationMode` literals, shared string constants, and the documented **raw-fallback bypass note** (mock output is not JSON).
- **`invoke_model`:** generation metadata always includes **`adapter_invocation_mode: langchain_structured_primary`** when an adapter runs through LangChain; missing adapter sets **`degraded_no_fallback_adapter`** with an explicit note (no hidden skip).
- **`fallback_model`:** successful mock fallback sets **`adapter_invocation_mode: raw_adapter_graph_managed_fallback`**, `langchain_prompt_used: false`, and **`bypass_note`**; missing mock keeps **`degraded_no_fallback_adapter`** on metadata and records `fallback_adapter_missing:mock` in graph errors.
- **`package_output`:** `repro_metadata` now includes **`adapter_invocation_mode`** and **`graph_path_summary`** so audits can see primary vs fallback-node completion without inferring only from `execution_health`.
- **`execution_health`** assignments now use the shared constants (string values unchanged for consumers).

## 2. Files changed

- `wos_ai_stack/runtime_turn_contracts.py` (new)
- `wos_ai_stack/langgraph_runtime.py`
- `wos_ai_stack/tests/test_langgraph_runtime.py`
- `world-engine/tests/test_story_runtime_rag_runtime.py`
- `docs/architecture/langgraph_in_world_of_shadows.md`
- `docs/reports/ai_stack_gates/B2_NEXT_GATE_REPORT.md`

## 3. What was deepened versus what already existed

- **Already existed:** LangGraph node chain, conditional fallback edge, `execution_health`, `ensure_langgraph_available`, World-Engine `StoryRuntimeManager` as host.
- **Deepened:** Explicit **invocation-mode** and **graph-path** semantics on diagnostics; **contract constants** for health and adapter modes; **tests** for healthy primary, graph-managed raw fallback, and missing-mock degraded path; World-Engine tests now assert repro metadata on both healthy and fallback turns.

## 4. Where LangGraph truly drives execution

- **Runtime turn graph** still owns the full node sequence through `package_output`; World-Engine only commits session/diagnostic records from the graph result.
- **Primary model path** remains LangChain-structured inside `invoke_model` (B1 layer); B2-next does **not** claim the fallback path is LangChain-structured — it is labeled **raw graph-managed fallback**.

## 5. Where fallback or degraded behavior still remains

- **`fallback_model`** uses **raw** `adapter.generate` on the mock adapter (by design).
- **Seed graphs** (`build_seed_writers_room_graph`, `build_seed_improvement_graph`) remain **single-node stubs** — not product workflow orchestration.

## 6. Why those paths still exist

- Default **mock** adapters return **non-JSON** text; running `PydanticOutputParser` on fallback would produce systematic parser failures and fake “structured” outcomes.
- Seed graphs are intentionally minimal to avoid parallel full-workflow engines before later milestones.

## 7. Tests added/updated

- `wos_ai_stack/tests/test_langgraph_runtime.py`: primary-path `adapter_invocation_mode` / `graph_path_summary`; fallback-path raw mode + `bypass_note`; missing-mock degraded mode + `graph_error`; constant-set guard.
- `world-engine/tests/test_story_runtime_rag_runtime.py`: healthy turn repro metadata; fallback turn repro metadata.

## 8. Exact test commands run

```powershell
cd C:\Users\YvesT\PycharmProjects\WorldOfShadows
$env:PYTHONPATH="."
python -m pytest wos_ai_stack/tests/test_langgraph_runtime.py wos_ai_stack/tests/test_langchain_integration.py -v --tb=short
```

```powershell
cd C:\Users\YvesT\PycharmProjects\WorldOfShadows\world-engine
$env:PYTHONPATH=".."
python -m pytest tests/test_story_runtime_rag_runtime.py::test_story_runtime_retrieval_context_influences_authoritative_turn tests/test_story_runtime_rag_runtime.py::test_story_runtime_graph_uses_fallback_branch_on_model_failure -v --tb=short
```

## 9. Verdict

**Pass**

## 10. Reason for verdict

- LangGraph execution is **more truthful**: diagnostics distinguish LangChain-primary from **raw graph-managed fallback** and **degraded missing-fallback** cases.
- Tests prove **real graph behavior** (not import-only), including World-Engine integration.
- **No claim** of full structured orchestration on fallback; **bypass_note** and invocation modes make that explicit.
- Report does not overstate graph authority over session commit or non-graph legacy areas.

## 11. Remaining risk

- Consumers that only read legacy fields might ignore `adapter_invocation_mode` / `graph_path_summary` until dashboards are updated.
- If a future mock emitted JSON, teams might consider optional structured fallback — out of scope here.

## 12. Dependency / environment notes

- Unchanged: `langgraph` required for `RuntimeTurnGraphExecutor`; same `PYTHONPATH` conventions as other stack tests.
