# D6: W5 actor tracking

**Owner SAD:** [world-engine SAD](../../../../docs/architecture/components/world-engine/architecture.md#d6-w5-actor-tracking)
**Origin:** ADR-0063 (retired)
**Status:** Partially implemented

## Context

Narrator and director surfaces need actor topology projections for W5 location framing.

## Decision

Runtime aspect ledger exposes W5 actor tracking projections consumed by world-engine and ai-stack.

## Evidence

| Kind | Link |
| --- | --- |
| Gate | `tests/gates/test_adr_0039_pi_scope.py` |
| Mechanism | [WE-M11](../../../../docs/architecture/components/world-engine/mechanism-catalog.md) |
