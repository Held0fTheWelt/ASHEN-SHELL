# D14: Semantic player input translation ingress

**Owner SAD:** [world-engine SAD](../../../../docs/architecture/components/world-engine/architecture.md#d14-semantic-player-input-enters-once)
**Origin:** ADR-0055 (retired)
**Status:** Accepted

## Context

Raw player text must become bounded semantic evidence before structural guards run.

## Decision

Translation ingress produces semantic payloads; structural guards remain non-semantic.

## Evidence

| Kind | Link |
| --- | --- |
| Mechanism | [WE-M10](../../../../docs/architecture/components/world-engine/mechanism-catalog.md) |
