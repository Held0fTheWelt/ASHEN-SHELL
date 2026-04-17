# ADR-0018: Role-aware `AIDecisionLog` and `ParsedRoleAwareDecision`

Date: 2026-03-29

Status: Accepted

## Context

Workstream W2/W3 introduced role-structured decision artifacts (interpreter, director, responder) and a need to record role-aware decision diagnostics in a canonical, machine-readable form for auditing and debugging.

## Decision

- Extend the `AIDecisionLog` to include: `parsed_decision` (the canonical `ParsedAIDecision`), role fields (interpreter, director, responder summaries), and `parsed_output` as a serialisable representation of the canonical decision.
- Introduce `ParsedRoleAwareDecision` as a schema that normalizes role-aware fields into `parsed_decision` when present.
- Implement helper `construct_ai_decision_log()` to populate these fields deterministically from the parsing layer.

## Rationale

- Provides a single canonical decision representation for execution and audit.
- Enables diagnostic surfaces (debug panel, logs) to show structured role outputs rather than ad-hoc raw strings.
- Simplifies verification: parsed decision equality checks in tests and evidence pipelines.

## Consequences

- Logging schema changes; consumers must read `parsed_decision` from `AIDecisionLog` rather than inferring decisions from raw outputs.
- Tests and evidence builders should assert canonicalization invariants (parsed_decision identity).
- Backward compatibility: when role-aware fields are absent, systems fall back to legacy raw outputs.

## Migrated from

`docs/archive/superpowers-legacy-execution-2026/specs/2026-03-29-w2-4-4-role-diagnostics.md` and `docs/archive/superpowers-legacy-execution-2026/specs/2026-03-28-w2-4-3-role-parsing-integration.md`.

---

(Automated migration entry created 2026-04-17)
