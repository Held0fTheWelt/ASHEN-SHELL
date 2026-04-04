# MCP Capability Layer in World of Shadows

Status: Canonical Milestone 8 architecture and implementation baseline.

## Objective

Define MCP as a governed capability surface with explicit schemas, mode boundaries, audit semantics, and denial behavior.

## Capability categories

- Retrieval capabilities:
  - `wos.context_pack.build`
  - `wos.transcript.read`
- Action capabilities:
  - `wos.review_bundle.build`

Retrieval and action are separated by explicit `kind` metadata and mode gates.

## Actor and mode permissions

Allowed mode boundaries:

- `runtime`: retrieval-only capabilities needed for authoritative turn support.
- `writers_room`: retrieval + review bundle generation.
- `improvement`: retrieval + review bundle generation.
- `admin`: transcript and governance-facing access patterns.

Denied invocations emit typed `CapabilityAccessDeniedError` and are always audited.

## Capability definition contract

Each capability defines:

- capability name,
- input schema,
- result schema,
- allowed mode set,
- audit requirement flag,
- failure semantics.

This contract is implemented in `wos_ai_stack/capabilities.py`.

## Audit requirements

Every invocation writes an audit row with:

- timestamp,
- capability name,
- mode,
- actor,
- outcome (`allowed`, `denied`, `error`),
- trace id,
- error detail (if any).

Audit rows are surfaced in runtime graph diagnostics and governance endpoint responses.

## Runtime and workflow integration

`RuntimeTurnGraphExecutor` now uses `wos.context_pack.build` capability for context retrieval assembly in the authoritative support path.

This means at least one real production path uses guarded capability access instead of bypassing internal helper calls.

## Governance visibility

Backend exposes `GET /api/v1/sessions/<session_id>/capability-audit` for governance-side inspection of capability invocations recorded in world-engine diagnostics.

## MCP server alignment

`tools/mcp_server/tools_registry.py` now includes `wos.capabilities.catalog` to expose the guarded capability catalog through the MCP tool surface.

## Deferred beyond M8

- signed audit persistence beyond in-memory retention,
- richer policy engines (role-based actor claims and environment scopes),
- write/action capabilities for live mutation paths (still deferred by authority model).
