# D4: Director realization thin path

**Owner SAD:** [world-engine SAD](../../../../docs/architecture/components/world-engine/architecture.md#d4-director-realization-thin-path-resolver-director-narrator)
**Origin:** ADR-0062 (retired)
**Status:** Accepted

## Context

Default player movement must not require heavyweight graph detours.

## Decision

Resolver → Director → narrator realization is the default thin path for ordinary player turns.

## Evidence

| Kind | Link |
| --- | --- |
| Source | `ai_stack/story_runtime/director/` |
| Sequence | [primary turn sequence](../sequence/world-engine-primary-turn-sequence.md) |
