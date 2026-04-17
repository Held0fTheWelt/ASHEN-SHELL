# M0 Transport & Connectivity · Decision

## Decision (Phase A)

- MCP transport: **stdio** (local).
- Backend connectivity: **HTTPS** calls to backend endpoints.

## Rationale

- stdio is minimally complex, robust, and ideal for local operator workflows.
- HTTPS enables use against PythonAnywhere without deploying additional service.

## Baseline Timeouts / Retries

- Backend HTTP timeout: **5s**
- Retry: **1** (network errors only), no retry on 4xx

**Migrated Decision:** See canonical ADR: [ADR-0027: MCP Transport & Connectivity — Phase A defaults](../ADR/adr-0027-mcp-transport-connectivity-phase-a.md)

## Trace/Headers

All MCP→backend calls carry:
- `X-WoS-Trace-Id` (UUID)
- `X-WoS-Client` (e.g., `mcp-operator`)
- optional `Authorization: Bearer <token>` (see Security)

