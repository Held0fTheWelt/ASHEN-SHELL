# ADR-0002 — Versioned end-to-end turn envelope

**Decision status:** Accepted
**Implementation state:** Partial
**Owners:** World Engine, AI Stack, Frontend
**Date:** 2026-08-11
**Supersedes:** scattered planner, commit, beat and diagnostics correspondence decisions
**Violations:** `AR-V002`, `AR-V004`

## Context

The implementation computes more dramatic information than every downstream boundary currently
proves it preserves. Source presence at producer and consumer is useful but does not prove that the
same production turn carries the value. Silent field narrowing makes sophisticated upstream logic
invisible to commit or player experience.

## Decision drivers

- semantic fields need explicit end-to-end correspondence;
- schema evolution must reject unknown incompatible versions;
- intentional information loss must be reviewable;
- tests must distinguish production-path proof from helper presence.

## Considered options

1. **Independent dictionaries per stage.** Rejected because field loss and semantic renaming remain
   implicit.
2. **One unversioned mega-object.** Rejected because consumers cannot negotiate evolution and
   authority boundaries become blurred.
3. **Versioned envelope with stage-specific views and correspondence rules.** Accepted.

## Decision

A versioned turn envelope identifies the session, turn, base revision, content version and trace,
and defines stage-specific proposal, validation, commit and player-projection views. Each boundary
declares fields consumed, preserved, introduced and intentionally discarded. World Engine owns the
commit and player-projection views.

## Consequences

Existing dictionaries require adapters during migration. The envelope is not permission to expose
private planner or sensitive data to players. Contract tests and trace evidence become mandatory
for fields that affect authoritative or user-visible behavior.

## Implementation correspondence

The current machine-readable path is `tools/architecture_assurance/drift_edge_catalog.json`; the
human scenario is [SCN-TURN-001](../scenarios/canonical-turn.md). Closure requires a seeded-value
test through proposal, commit, persisted state and player delivery.

## Git and historical lineage

April audits recorded validation-to-commit asymmetry. July drift-edge work (`de2cff5b`) established
field-carrying edges. This ADR turns that repair evidence into a normative contract.
