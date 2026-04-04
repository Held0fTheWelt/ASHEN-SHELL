# LangGraph in World of Shadows

Status: Canonical Milestone 7 architecture and implementation baseline.

## Scope and ownership

LangGraph now materially owns the authoritative runtime-supporting turn orchestration path in World-Engine, while World-Engine remains the authority that commits session history and diagnostics.

Graph-owned path:

1. interpret player input,
2. retrieve and assemble context pack,
3. route model/provider,
4. invoke model,
5. branch to fallback when invocation fails,
6. package graph-level diagnostics and outcomes.

World-Engine authority boundary:

- Graph output is proposal/diagnostic data.
- Session mutation/commit (`turn_counter`, history append, diagnostics append) is still performed by `StoryRuntimeManager`.

## Runtime turn graph

Implemented in `wos_ai_stack/langgraph_runtime.py` via `RuntimeTurnGraphExecutor`.

Nodes:

- `interpret_input`
- `retrieve_context`
- `route_model`
- `invoke_model`
- `fallback_model` (conditional)
- `package_output`

## Retry, fallback, checkpoint philosophy

- M7 introduces explicit branch ownership: `invoke_model -> fallback_model` on error.
- Fallback uses `mock` adapter when available to keep runtime-supporting flow operational.
- If fallback adapter is missing, graph emits explicit error markers in diagnostics.
- Checkpoint persistence is deferred; M7 uses graph state traceability and deterministic fallback semantics first.

## Graph state discipline

The runtime graph uses explicit typed state (`RuntimeTurnState`) including:

- input/session identifiers,
- interpreted input object,
- retrieval pack metadata,
- routing decision details,
- generation outcome data,
- graph trace metadata (`nodes_executed`, `node_outcomes`, `errors`).

This keeps node boundaries explicit and debuggable.

## Diagnostics and traceability

Each graph run emits:

- `graph_name`
- `graph_version`
- `nodes_executed`
- `node_outcomes`
- `fallback_path_taken`
- graph errors (if any)

These diagnostics are attached to the authoritative runtime turn event.

## Workflow graph seeds (for later milestones)

M7 ships operational seed graphs in the same stack:

- `build_seed_writers_room_graph()` for Writers-Room workflow seed.
- `build_seed_improvement_graph()` for improvement workflow seed.

These are intentionally minimal but executable and test-covered, enabling M9/M10 expansion without introducing a parallel orchestration stack.

## Deferred beyond M7

- durable checkpoint stores,
- advanced retry policies with backoff and budgets,
- cross-run graph replay tooling.
