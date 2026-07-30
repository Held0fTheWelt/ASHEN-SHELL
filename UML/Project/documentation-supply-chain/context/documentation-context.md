# Documentation Supply Chain - Context

**Viewpoint:** `context`
**Concern:** Human author and authoritative documentation corpus

[PlantUML source](documentation-context.puml)

## Modeled elements

| Element | Responsibility | Contract | Source |
| --- | --- | --- | --- |
| Document Author | Maintain architecture intent and operating knowledge | Role-correct Markdown source | [`docs/architecture/START-HERE.md`](../../../../docs/architecture/START-HERE.md) |
| Documentation Corpus | Expose current architecture, contracts and evidence | Navigable versioned Markdown | [`docs/architecture/README.md`](../../../../docs/architecture/README.md) |

## Modeled relationships

| From | To | Semantics | Contract | Source |
| --- | --- | --- | --- | --- |
| Document Author | Documentation Corpus | authors and reviews | versioned change | catalog contract |

Generated deterministically from Better Tomorrow's semantic model catalog; edit the catalog, not this projection.
