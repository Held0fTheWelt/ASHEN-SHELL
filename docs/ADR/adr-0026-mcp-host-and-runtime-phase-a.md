# ADR-0026: MCP Phase A — Host & Runtime defaults

## Status
Proposed

## Date
2026-04-17

## Intellectual property rights
Repository authorship and licensing: see project LICENSE; contact maintainers for clarification.

## Privacy and confidentiality
This ADR contains no personal data. Implementers must follow the repository privacy and confidentiality policies, avoid committing secrets, and document any sensitive data handling in implementation steps.

## Context
MCP (Model Context Protocol) usage during Phase A requires a safe, low-friction host and runtime contract for operator workflows and debugging.

## Decision
- Run the MCP server locally (stdio transport) for Phase A operator workflows.
- MCP tools communicate with the backend remotely over HTTPS.
- MCP in Phase A functions as an operator console (inspect/debug) and must not be used as an in-game mechanic.

## Consequences
- Operator tooling should be documented for local setup and required backend access.
- Future phases may evolve the host and runtime assumptions; changes require ADRs.

## Testing


## References
(Automated migration entry created 2026-04-17)
