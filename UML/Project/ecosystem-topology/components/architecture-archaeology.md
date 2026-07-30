# Better Tomorrow - Architecture Archaeology

**Viewpoint:** `component`
**Concern:** Current code, Git evolution and historical MVP corpus drive target selection

[PlantUML source](architecture-archaeology.puml)

## Modeled elements

| Element | Responsibility | Contract | Source |
| --- | --- | --- | --- |
| Current Code | Show executable present structures | HEAD plus source anchors | [`README.md`](../../../../README.md) |
| Git History | Show movement, replacement and hotspot chronology | Commit and rename evidence | [`.git`](../../../../.git) |
| Historical MVP Corpus | Preserve earlier goals, audits, snapshots and work orders | Non-authoritative read-only archaeology snapshot | [`docs/architecture/evidence/README.md`](../../../../docs/architecture/evidence/README.md) |
| Architecture Reconciliation | Classify claims and expose contradictions | confirmed, obsolete, conflicting or open | [`tools/architecture_assurance/model_catalog.json`](../../../../tools/architecture_assurance/model_catalog.json) |
| Target Architecture | State the best coherent solution selected from evidence | Accepted decisions and implementable deltas | [`docs/architecture/project/ecosystem-topology/architecture.md`](../../../../docs/architecture/project/ecosystem-topology/architecture.md) |

## Modeled relationships

| From | To | Semantics | Contract | Source |
| --- | --- | --- | --- | --- |
| Current Code | Architecture Reconciliation | supplies present structure | source anchors | catalog contract |
| Git History | Architecture Reconciliation | supplies evolution | commit/rename chronology | catalog contract |
| Historical MVP Corpus | Architecture Reconciliation | supplies historical claims | read-only dated provenance | catalog contract |
| Architecture Reconciliation | Target Architecture | justifies target options | accepted decision and delta | catalog contract |

Generated deterministically from Better Tomorrow's semantic model catalog; edit the catalog, not this projection.
