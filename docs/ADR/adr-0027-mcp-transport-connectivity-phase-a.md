# ADR-0027: MCP Transport & Connectivity — Phase A defaults

Date: 2026-04-17

Status: Accepted

## Context

MCP transport and connectivity need stable defaults for Phase A operator/QA usage.

## Decision

- Use `stdio` as the MCP transport for Phase A (local runs).
- Use HTTPS for backend connectivity.
- Baseline timeouts and retries: backend HTTP timeout 5s, retry once on network errors.
- Include trace headers on MCP→backend calls: `X-WoS-Trace-Id`, `X-WoS-Client`, and optional `Authorization`.

## Rationale

- `stdio` keeps the local operator experience simple and robust.
- HTTPS maintains compatibility with remote backends like PythonAnywhere.

## Consequences

- Implementers should ensure tooling honours timeouts and header conventions.

## Migrated from

`docs/mcp/02_M0_transport_connectivity.md` (Decision (Phase A))

---

(Automated migration entry created 2026-04-17)
