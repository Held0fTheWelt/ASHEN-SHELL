# 49 — Canonical Target Surfaces

This chapter maps MVP concerns to the real implementation owners.

## `backend/`
Use for API routes, auth/policy, content compiler integration, session/bootstrap orchestration, persistence, and operator-safe mirrors.

Primary zones:
- `backend/app/api/v1/`
- `backend/app/services/`
- `backend/app/runtime/`
- `backend/app/content/`
- `backend/tests/`

## `world-engine/`
Use for authoritative runtime execution, committed turn truth, session/run management, and live runtime diagnostics/play-service APIs.

Primary zones:
- `world-engine/app/api/`
- `world-engine/app/runtime/`
- `world-engine/tests/`

## `frontend/`
Use for ordinary player/public routes, launcher/bootstrap/ticket flow, and player shell integration.

## `administration-tool/`
Use for operator/admin surfaces, governance review, editorial management, and inspection UIs.

## `writers-room/`
Use for authoring-side UI, review-oriented flows, and backend writers-room integration.

## `ai_stack/`
Use for RAG, LangGraph orchestration, LangChain bridges, governed AI helpers, packaging, retrieval, and runtime steering support.

## `tools/mcp_server/`
Use for MCP registry behavior, safe handlers, operating-profile control, and backend parity.

## `tests/`
Use for cross-service smoke, e2e, and acceptance validation.

## Patching rule

Patch the component that owns the responsibility.

Examples:
- runtime truth defect → `world-engine/`
- backend session mirror or MCP-safe read surface → `backend/` and possibly `tools/mcp_server/`
- player route leakage → `frontend/` or backend redirect/config
- review/admin visibility gap → `administration-tool/` plus backend API if needed
- AI packaging/retrieval defect → `ai_stack/` or `story_runtime_core/`
