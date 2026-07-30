# Documentation Supply Chain - Publication Flow

**Viewpoint:** `activity`
**Concern:** Deterministic authoring-to-publication validation

[PlantUML source](publication-flow.puml)

## Modeled elements

| Element | Responsibility | Contract | Source |
| --- | --- | --- | --- |
| Authoritative Sources | Hold SAD, decision, contract and runbook truth | Declared document role | [`docs/architecture/project/FRONTMATTER.md`](../../../../docs/architecture/project/FRONTMATTER.md) |
| Generated Model Companions | Project semantic catalog content for navigation | Regenerated, never hand-divergent | [`tools/architecture_assurance/view_builder.py`](../../../../tools/architecture_assurance/view_builder.py) |
| Link Audit | Detect missing and stale references | Repository-relative target resolution | [`scripts/architecture_link_audit.py`](../../../../scripts/architecture_link_audit.py) |
| Documentation Gate | Enforce required sections, roles and navigation | Blocking CI findings | [`tests/gates/test_architecture_documentation_gate.py`](../../../../tests/gates/test_architecture_documentation_gate.py) |
| MkDocs Projection | Publish navigable documentation | mkdocs.yml navigation | [`mkdocs.yml`](../../../../mkdocs.yml) |

## Modeled relationships

| From | To | Semantics | Contract | Source |
| --- | --- | --- | --- | --- |
| Authoritative Sources | Generated Model Companions | drives projections | semantic catalog and SAD intent | [`tools/architecture_assurance/view_builder.py`](../../../../tools/architecture_assurance/view_builder.py) |
| Generated Model Companions | Link Audit | is checked by | all generated links resolve | [`scripts/architecture_link_audit.py`](../../../../scripts/architecture_link_audit.py) |
| Link Audit | Documentation Gate | supplies findings | stable failing paths | [`tests/gates/test_architecture_documentation_gate.py`](../../../../tests/gates/test_architecture_documentation_gate.py) |
| Documentation Gate | MkDocs Projection | permits publication | all blocking gates pass | [`mkdocs.yml`](../../../../mkdocs.yml) |

Generated deterministically from Better Tomorrow's semantic model catalog; edit the catalog, not this projection.
