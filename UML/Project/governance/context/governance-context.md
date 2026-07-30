# Architecture Governance - Context

**Viewpoint:** `context`
**Concern:** Maintainer interaction with decision and runtime governance

[PlantUML source](governance-context.puml)

## Modeled elements

| Element | Responsibility | Contract | Source |
| --- | --- | --- | --- |
| Maintainer | Propose, review and accept architecture decisions | Evidence-backed review | [`docs/architecture/project/DECISION_REGISTRY.md`](../../../../docs/architecture/project/DECISION_REGISTRY.md) |
| Governance System | Control decision lifecycle and runtime policy changes | Recorded decision and audit evidence | [`docs/architecture/project/governance/architecture.md`](../../../../docs/architecture/project/governance/architecture.md) |

## Modeled relationships

| From | To | Semantics | Contract | Source |
| --- | --- | --- | --- | --- |
| Maintainer | Governance System | proposes and reviews | evidence-backed change | catalog contract |

Generated deterministically from Better Tomorrow's semantic model catalog; edit the catalog, not this projection.
