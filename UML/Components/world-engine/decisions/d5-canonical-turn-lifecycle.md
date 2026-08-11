# D5: Canonical turn lifecycle

**Owner SAD:** [world-engine SAD](../../../../docs/architecture/components/world-engine/architecture.md#d5-one-canonical-lifecycle-and-one-persistence-edge)
**Origin:** ADR-0038 (retired)
**Status:** Accepted

## Context

Turn execution must follow one commit / persist / project path with explicit lifecycle states.

## Decision

Canonical turn envelope fields, counters, and phased rollout govern every committed turn.

## Evidence

See [mechanism catalog](../../../../docs/architecture/components/world-engine/mechanism-catalog.md) WE-M05.
