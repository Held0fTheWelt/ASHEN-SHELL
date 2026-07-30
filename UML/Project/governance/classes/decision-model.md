# Architecture Governance - Decision Model

**Viewpoint:** `class`
**Concern:** Proposals, accepted decisions and bounded exceptions

[PlantUML source](decision-model.puml)

## Modeled elements

| Element | Responsibility | Contract | Source |
| --- | --- | --- | --- |
| Decision Proposal | Frame problem, options and evidence | Owner and affected scopes | [`docs/architecture/project/DECISION_REGISTRY.md`](../../../../docs/architecture/project/DECISION_REGISTRY.md) |
| Accepted Decision | State selected option and consequences | Stable id and acceptance date | [`docs/architecture/project/ADR_ABSORPTION_MATRIX.md`](../../../../docs/architecture/project/ADR_ABSORPTION_MATRIX.md) |
| Governed Exception | Bound temporary deviation | Expiry, owner and compensating control | [`docs/architecture/project/governance/mechanism-catalog.md`](../../../../docs/architecture/project/governance/mechanism-catalog.md) |

## Modeled relationships

| From | To | Semantics | Contract | Source |
| --- | --- | --- | --- | --- |
| Decision Proposal | Accepted Decision | is accepted as | reviewed rationale | [`docs/architecture/project/DECISION_REGISTRY.md`](../../../../docs/architecture/project/DECISION_REGISTRY.md) |
| Accepted Decision | Governed Exception | may bound | temporary explicit deviation | [`docs/architecture/project/governance/mechanism-catalog.md`](../../../../docs/architecture/project/governance/mechanism-catalog.md) |

Generated deterministically from Better Tomorrow's semantic model catalog; edit the catalog, not this projection.
