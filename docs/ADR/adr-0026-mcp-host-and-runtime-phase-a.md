# ADR-0026: MCP Phase A — Host & Runtime defaults

Date: 2026-04-17

Status: Accepted

## Context

MCP (Model Context Protocol) usage during Phase A requires a safe, low-friction host and runtime contract for operator workflows and debugging.

## Decision

- Run the MCP server locally (stdio transport) for Phase A operator workflows.
- MCP tools communicate with the backend remotely over HTTPS.
- MCP in Phase A functions as an operator console (inspect/debug) and must not be used as an in-game mechanic.

## Rationale

- Minimizes risk and complexity for early operator tooling.
- Enables immediate value for debugging and QA without changing in-game loops.

## Consequences

- Operator tooling should be documented for local setup and required backend access.
- Future phases may evolve the host and runtime assumptions; changes require ADRs.

## Migrated from

`docs/mcp/01_M0_host_and_runtime.md` (Decision (Default for Phase A))

---

(Automated migration entry created 2026-04-17)
