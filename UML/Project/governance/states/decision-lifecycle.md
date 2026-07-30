# Architecture Governance - Decision Lifecycle

**Viewpoint:** `state`
**Concern:** Draft, proposal, acceptance and supersession with preserved lineage

[PlantUML source](decision-lifecycle.puml)

## Modeled elements

| Element | Responsibility | Contract | Source |
| --- | --- | --- | --- |
| Draft | Collect problem and options | No authority yet | [`docs/architecture/project/DECISION_REGISTRY.md`](../../../../docs/architecture/project/DECISION_REGISTRY.md) |
| Proposed | Expose reviewable evidence | Owner and scope complete | [`docs/architecture/project/DECISION_REGISTRY.md`](../../../../docs/architecture/project/DECISION_REGISTRY.md) |
| Accepted | Govern implementation and models | Decision registry entry | [`docs/architecture/project/DECISION_REGISTRY.md`](../../../../docs/architecture/project/DECISION_REGISTRY.md) |
| Superseded | Retain lineage without current authority | Replacement decision linked | [`docs/adr/legacy/README.md`](../../../../docs/adr/legacy/README.md) |

## Modeled relationships

| From | To | Semantics | Contract | Source |
| --- | --- | --- | --- | --- |
| Initial | Draft | problem recorded | scope named | catalog contract |
| Draft | Proposed | options and evidence complete | review ready | catalog contract |
| Proposed | Accepted | approved | decision registry updated | [`docs/architecture/project/DECISION_REGISTRY.md`](../../../../docs/architecture/project/DECISION_REGISTRY.md) |
| Accepted | Superseded | replacement accepted | lineage preserved | [`docs/adr/legacy/README.md`](../../../../docs/adr/legacy/README.md) |

Generated deterministically from Better Tomorrow's semantic model catalog; edit the catalog, not this projection.
