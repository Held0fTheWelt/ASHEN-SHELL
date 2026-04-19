# 51 — Audit Translation Rules

Use this chapter whenever an audit identifies a real gap.

## Translation rule

Translate every serious finding into:
- an owning component,
- exact file targets,
- the test targets,
- the validation commands,
- and the adjacent seams that should be checked for the same class of drift.

## Example

### Finding
Runtime-safe MCP session surfaces are claimed but repository behavior is incomplete or misaligned.

### Translation
- Owner: `backend/` plus `tools/mcp_server/`
- File targets:
  - `backend/app/api/v1/session_routes.py`
  - `backend/app/services/session_service.py`
  - `tools/mcp_server/backend_session_mcp_handler_factories.py`
  - `tools/mcp_server/tools_registry_handlers_backend_session.py`
- Tests:
  - `backend/tests/runtime/test_mcp_enrichment.py`
  - `tools/mcp_server/tests/test_mcp_runtime_safe_session_surface.py`
- Validation:
  - targeted pytest commands,
  - then smoke/e2e when player flow or routing is affected.

## Adjacent-hardening rule

When fixing a gap, inspect neighboring seams that would fail on the same audit axis.
Do not stop at the first green assertion if descriptors, routes, docs, or ownership boundaries still disagree.
