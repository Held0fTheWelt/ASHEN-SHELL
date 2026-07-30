# MVP Completion - Evidence Model

**Viewpoint:** `class`
**Concern:** Claims require multidimensional proof and explicit residual gaps

[PlantUML source](capability-evidence-model.puml)

## Modeled elements

| Element | Responsibility | Contract | Source |
| --- | --- | --- | --- |
| Capability Claim | State user-observable outcome | Stable capability id | [`docs/architecture/project/mvp-live-runtime-completion/evidence-matrix.md`](../../../../docs/architecture/project/mvp-live-runtime-completion/evidence-matrix.md) |
| Capability Proof | Bind code, test, trace and demonstration | Production-path evidence | [`tests/reports/MVP_Live_Runtime_Completion/MVP5_OPERATIONAL_EVIDENCE.md`](../../../../tests/reports/MVP_Live_Runtime_Completion/MVP5_OPERATIONAL_EVIDENCE.md) |
| Residual Gap | Explain incomplete cross-link or degraded behavior | Owner and closure criterion | [`docs/architecture/project/mvp-live-runtime-completion/mechanism-catalog.md`](../../../../docs/architecture/project/mvp-live-runtime-completion/mechanism-catalog.md) |

## Modeled relationships

| From | To | Semantics | Contract | Source |
| --- | --- | --- | --- | --- |
| Capability Claim | Capability Proof | requires | all evidence dimensions | [`docs/architecture/project/mvp-live-runtime-completion/evidence-matrix.md`](../../../../docs/architecture/project/mvp-live-runtime-completion/evidence-matrix.md) |
| Capability Proof | Residual Gap | exposes missing evidence as | no false completion | [`docs/architecture/project/mvp-live-runtime-completion/mechanism-catalog.md`](../../../../docs/architecture/project/mvp-live-runtime-completion/mechanism-catalog.md) |

Generated deterministically from Better Tomorrow's semantic model catalog; edit the catalog, not this projection.
