# ADR-0005 — Cross-service turn trace contract

**Decision status:** Accepted
**Implementation state:** Partial
**Owners:** Backend, World Engine, AI Stack, Operations
**Date:** 2026-08-11
**Supersedes:** retired Langfuse and trace-correlation decisions
**Violations:** `AR-V006`

## Context

Backend, World Engine, AI and MCP contain legitimate local telemetry adapters. Without a common
trace identity, ownership tree, redaction rule and gap state, a rich operator screen can still hide
a missing production-path span.

## Decision

Every player turn carries one trace identity. Each service owns named spans and propagates the
identity across boundaries. The trace records commit/persist outcome and player-projection version,
represents unavailable telemetry as an explicit partial gap, and never changes domain behavior.

## Considered options

- Provider-specific trace structures as the contract were rejected due to lock-in.
- Best-effort IDs without parentage were rejected because they cannot prove continuity.
- Domain failure on telemetry loss was rejected because observability is not story authority.

## Consequences

Local adapters remain, but must satisfy the shared contract. Redaction tests apply at every exporter.
Integration evidence must traverse backend, World Engine and AI with a disposable provider or a
contract-faithful local substitute.

## Implementation correspondence

Current anchors include `player_turn_trace_start.py`, `world_engine/observability/trace.py`,
`ai_stack/langfuse/langfuse_evidence.py` and `tools/mcp_server/langfuse_tracing.py`.

## Git and historical lineage

MVP4 observability work established the operator need; subsequent runtime work exposed incomplete
cross-service continuity. Git evidence remains linked through `DRIFT-008`.
