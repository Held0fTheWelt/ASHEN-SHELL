# MVP Completion - Experience Context

**Viewpoint:** `context`
**Concern:** Player-visible experience as the completion boundary

[PlantUML source](experience-context.puml)

## Modeled elements

| Element | Responsibility | Contract | Source |
| --- | --- | --- | --- |
| Player | Launch and play the God of Carnage experience | Real browser/runtime path | [`tests/e2e/test_final_goc_annette_alain_e2e.py`](../../../../tests/e2e/test_final_goc_annette_alain_e2e.py) |
| Live Dramatic Experience | Deliver a responsive, stateful, role-sensitive scene | End-to-end acceptance contract | [`docs/architecture/project/mvp-live-runtime-completion/architecture.md`](../../../../docs/architecture/project/mvp-live-runtime-completion/architecture.md) |

## Modeled relationships

| From | To | Semantics | Contract | Source |
| --- | --- | --- | --- | --- |
| Player | Live Dramatic Experience | plays and evaluates | real runtime path | catalog contract |

Generated deterministically from Better Tomorrow's semantic model catalog; edit the catalog, not this projection.
