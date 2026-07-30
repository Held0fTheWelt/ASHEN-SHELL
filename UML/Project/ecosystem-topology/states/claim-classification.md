# Better Tomorrow - Historical Claim Classification

**Viewpoint:** `state`
**Concern:** Historical claims become confirmed, obsolete, conflicting or open target options

[PlantUML source](claim-classification.puml)

## Modeled elements

| Element | Responsibility | Contract | Source |
| --- | --- | --- | --- |
| Unclassified Claim | Hold an archaeological assertion before verification | Source and date recorded | [`docs/architecture/project/ecosystem-topology/evidence-matrix.md`](../../../../docs/architecture/project/ecosystem-topology/evidence-matrix.md) |
| Confirmed Current | Match current code and accepted decision | Live source anchors | [`docs/architecture/project/ecosystem-topology/evidence-matrix.md`](../../../../docs/architecture/project/ecosystem-topology/evidence-matrix.md) |
| Obsolete | Explain superseded historical material | Replacement evidence | [`docs/architecture/project/ecosystem-topology/evidence-matrix.md`](../../../../docs/architecture/project/ecosystem-topology/evidence-matrix.md) |
| Conflicting | Expose concurrent incompatible truths | Decision required | [`docs/architecture/project/ecosystem-topology/architecture.md`](../../../../docs/architecture/project/ecosystem-topology/architecture.md) |
| Open Target Question | Preserve valuable intent not yet implemented | Explicit option and acceptance evidence | [`docs/architecture/project/ecosystem-topology/mechanism-catalog.md`](../../../../docs/architecture/project/ecosystem-topology/mechanism-catalog.md) |

## Modeled relationships

| From | To | Semantics | Contract | Source |
| --- | --- | --- | --- | --- |
| Initial | Unclassified Claim | claim harvested | provenance recorded | catalog contract |
| Unclassified Claim | Confirmed Current | matches current code | source and test proof | catalog contract |
| Unclassified Claim | Obsolete | superseded | replacement commit or decision | catalog contract |
| Unclassified Claim | Conflicting | multiple truths remain | conflict evidence | catalog contract |
| Unclassified Claim | Open Target Question | valuable intent unimplemented | target option retained | catalog contract |
| Conflicting | Open Target Question | decision framed | trade-offs and acceptance criteria | catalog contract |

Generated deterministically from Better Tomorrow's semantic model catalog; edit the catalog, not this projection.
