# MVP Completion - Capability Lifecycle

**Viewpoint:** `state`
**Concern:** Implementation is not completion until integrated and proven

[PlantUML source](capability-lifecycle.puml)

## Modeled elements

| Element | Responsibility | Contract | Source |
| --- | --- | --- | --- |
| Proposed | Define capability and acceptance | No completion claim | [`docs/architecture/project/mvp-live-runtime-completion/architecture.md`](../../../../docs/architecture/project/mvp-live-runtime-completion/architecture.md) |
| Implemented | Provide production code path | Source-located behavior | [`docs/architecture/project/mvp-live-runtime-completion/evidence-matrix.md`](../../../../docs/architecture/project/mvp-live-runtime-completion/evidence-matrix.md) |
| Integrated | Survive all authority boundaries | End-to-end path | [`tests/integration/test_story_runtime_experience.py`](../../../../tests/integration/test_story_runtime_experience.py) |
| Proven | Pass user-visible and operational evidence | Repeatable acceptance | [`tests/e2e/test_final_goc_annette_alain_e2e.py`](../../../../tests/e2e/test_final_goc_annette_alain_e2e.py) |
| Regressed | Record later drift from proven behavior | Finding and reproduction | [`docs/architecture/project/mvp-live-runtime-completion/mechanism-catalog.md`](../../../../docs/architecture/project/mvp-live-runtime-completion/mechanism-catalog.md) |

## Modeled relationships

| From | To | Semantics | Contract | Source |
| --- | --- | --- | --- | --- |
| Initial | Proposed | capability framed | acceptance stated | catalog contract |
| Proposed | Implemented | production path exists | source proof | catalog contract |
| Implemented | Integrated | boundaries agree | integration proof | [`tests/integration/test_story_runtime_experience.py`](../../../../tests/integration/test_story_runtime_experience.py) |
| Integrated | Proven | acceptance passes | E2E and operational evidence | [`tests/e2e/test_final_goc_annette_alain_e2e.py`](../../../../tests/e2e/test_final_goc_annette_alain_e2e.py) |
| Proven | Regressed | later evidence fails | drift finding | catalog contract |

Generated deterministically from Better Tomorrow's semantic model catalog; edit the catalog, not this projection.
