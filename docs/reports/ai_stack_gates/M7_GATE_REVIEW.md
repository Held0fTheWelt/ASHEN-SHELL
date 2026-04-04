# Milestone 7 Gate Review

Date: 2026-04-04  
Status: PASS  
Recommendation: Proceed

## Scope delivered

- Added canonical LangGraph architecture document:
  - `docs/architecture/langgraph_in_world_of_shadows.md`
- Added runtime LangGraph orchestration implementation:
  - `wos_ai_stack/langgraph_runtime.py`
- Integrated runtime manager with graph-owned execution:
  - `world-engine/app/story_runtime/manager.py`
- Added graph-focused automated tests:
  - `wos_ai_stack/tests/test_langgraph_runtime.py`
  - `world-engine/tests/test_story_runtime_rag_runtime.py` (fallback branch coverage)
  - `world-engine/tests/test_story_runtime_api.py` (graph diagnostics visibility)

## Prerequisite verification summary

- M6 retrieval foundation is present and passing:
  - `wos_ai_stack/tests/test_rag.py`
  - runtime retrieval integration tests in `world-engine/tests`

## Design decisions

- LangGraph now owns the runtime-supporting flow (interpret -> retrieval -> route -> invoke -> fallback -> package).
- A meaningful branch is operational: model failure transitions into fallback node.
- Graph state is explicit (`RuntimeTurnState`) and tracks node execution/outcome.
- World-Engine remains authority for final session mutation and committed event append.

## Migrations or compatibility shims

- `StoryRuntimeManager.execute_turn` switched from inline orchestration to graph invocation.
- Output shape is backward compatible for core fields and extends diagnostics via `graph`.

## Tests run

```bash
python -m pytest "wos_ai_stack/tests/test_rag.py" "wos_ai_stack/tests/test_langgraph_runtime.py" -q --tb=short
python -m pytest "world-engine/tests/test_story_runtime_api.py" "world-engine/tests/test_story_runtime_rag_runtime.py" -q --tb=short
```

Result: all commands passed.

## Acceptance criteria status

| Criterion | Status |
|---|---|
| Real runtime-supporting LangGraph flow exists | Pass |
| Graph materially owns control flow | Pass |
| Retry/fallback branch behavior is real | Pass |
| Graph state is inspectable | Pass |
| Diagnostics prove graph execution | Pass |
| Automated tests cover graph behavior | Pass |

## Required milestone-specific answers

### What exact path is now graph-owned?

- `interpret_input -> retrieve_context -> route_model -> invoke_model -> (fallback_model when needed) -> package_output`

### Which parts of authoritative runtime remain outside the graph and why?

- Session mutation and commit (`turn_counter`, `history`, `diagnostics`) remain in `StoryRuntimeManager` to preserve World-Engine runtime authority.

### What fallback or retry logic is now real?

- `invoke_model` failure or missing adapter triggers explicit `fallback_model` branch and uses `mock` adapter as controlled fallback.

### What later workflow graphs are seeded vs operational?

- Operational seed graphs exist for Writers-Room and improvement (`build_seed_writers_room_graph`, `build_seed_improvement_graph`), but full workflow logic remains for M9/M10.

### What graph/state design risks remain?

- Durable checkpoint persistence and replay tooling are not yet implemented.
- Multi-step retry budgets/backoff policies remain deferred.

## Known limitations

- Current fallback strategy is deterministic and simple; it does not yet include policy-weighted retries.

## Risks left open

- Future graph growth may require persistent checkpoint stores and richer error taxonomies.
