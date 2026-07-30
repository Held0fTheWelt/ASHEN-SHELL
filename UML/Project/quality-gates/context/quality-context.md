# Quality Gates - Context

**Viewpoint:** `context`
**Concern:** Developer verification through one authoritative gate system

[PlantUML source](quality-context.puml)

## Modeled elements

| Element | Responsibility | Contract | Source |
| --- | --- | --- | --- |
| Developer | Run focused and complete verification | Central runner profile | [`tests/TESTING.md`](../../../../tests/TESTING.md) |
| Quality Gate System | Select, execute and report proportionate verification | Stable suite and exit semantics | [`tests/run_tests.py`](../../../../tests/run_tests.py) |

## Modeled relationships

| From | To | Semantics | Contract | Source |
| --- | --- | --- | --- | --- |
| Developer | Quality Gate System | requests verification | declared profile | catalog contract |

Generated deterministically from Better Tomorrow's semantic model catalog; edit the catalog, not this projection.
