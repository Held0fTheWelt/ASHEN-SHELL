# Milestone 8 Gate Review

Date: 2026-04-04  
Status: PASS  
Recommendation: Proceed

## Scope delivered

- Added canonical MCP architecture document:
  - `docs/architecture/mcp_in_world_of_shadows.md`
- Added guarded capability layer:
  - `wos_ai_stack/capabilities.py`
- Integrated capability invocation into runtime graph path:
  - `wos_ai_stack/langgraph_runtime.py`
  - `world-engine/app/story_runtime/manager.py`
- Added governance visibility endpoint:
  - `backend/app/api/v1/session_routes.py` (`GET /api/v1/sessions/<session_id>/capability-audit`)
- Aligned MCP server surface with capability catalog:
  - `tools/mcp_server/tools_registry.py` (`wos.capabilities.catalog`)
- Added capability and integration tests:
  - `wos_ai_stack/tests/test_capabilities.py`
  - `world-engine/tests/test_story_runtime_rag_runtime.py`
  - `backend/tests/test_session_routes.py`
  - `tools/mcp_server/tests/test_registry.py`
  - `tools/mcp_server/tests/test_tools_handlers.py`

## Prerequisite verification summary

- M7 runtime graph path and fallback branch are present and passing.
- M6 retrieval layer remains operational and is now consumed through guarded capability invocation.

## Design decisions

- Capabilities are declared with explicit name/schema/modes/audit/failure semantics.
- Runtime graph now calls `wos.context_pack.build` capability instead of direct retrieval helper invocation.
- Denied mode access raises typed `CapabilityAccessDeniedError` and always emits audit rows.
- Audit rows are surfaced both in runtime graph diagnostics and backend governance endpoint payloads.

## Migrations or compatibility shims

- Runtime retrieval remains functionally equivalent but now passes through guarded capability boundaries.
- Existing APIs remain compatible; capability audit is additive.

## Tests run

```bash
python -m pytest "wos_ai_stack/tests/test_rag.py" "wos_ai_stack/tests/test_langgraph_runtime.py" "wos_ai_stack/tests/test_capabilities.py" -q --tb=short
python -m pytest "world-engine/tests/test_story_runtime_api.py" "world-engine/tests/test_story_runtime_rag_runtime.py" -q --tb=short
python -m pytest "backend/tests/test_session_routes.py" -q --tb=short
python -m pytest "tools/mcp_server/tests/test_registry.py" "tools/mcp_server/tests/test_tools_handlers.py" -q --tb=short
```

Result: all commands passed.

## Acceptance criteria status

| Criterion | Status |
|---|---|
| Real guarded capability layer exists | Pass |
| Retrieval vs action separation is explicit | Pass |
| At least one real stack path uses capability layer | Pass |
| Audit and denial semantics are implemented | Pass |
| Automated tests prove behavior | Pass |

## Required milestone-specific answers

### What exact capabilities now exist?

- `wos.context_pack.build` (retrieval)
- `wos.transcript.read` (retrieval)
- `wos.review_bundle.build` (action)

### Which ones are runtime-facing, Writers-Room-facing, improvement-facing?

- Runtime-facing: `wos.context_pack.build`, `wos.transcript.read`
- Writers-Room-facing: `wos.context_pack.build`, `wos.review_bundle.build`
- Improvement-facing: `wos.context_pack.build`, `wos.transcript.read`, `wos.review_bundle.build`

### What still bypasses capability layer and why?

- Some legacy non-graph code paths and historical utilities still call underlying services directly; they are outside the newly graph-owned authoritative support flow and are slated for later unification.

### How is denied access represented and audited?

- Denied invocations raise `CapabilityAccessDeniedError`.
- Registry audit records outcome `denied`, including capability name, mode, actor, trace id, and error text.

### What remains deferred before MCP is broad rather than first-generation?

- Persistent signed audit storage.
- Rich role/claim-based policy beyond mode-level gating.
- Wider capability coverage for additional runtime/admin workflows.

## Known limitations

- Audit storage is in-memory within current process lifecycle.
- Capability schemas use lightweight required-field validation in this milestone.

## Risks left open

- Broader capability expansion requires stronger policy and persistence controls.
