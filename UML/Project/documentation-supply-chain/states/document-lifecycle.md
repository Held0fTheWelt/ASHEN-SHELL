# Documentation Supply Chain - Lifecycle

**Viewpoint:** `state`
**Concern:** Draft, validated, published and stale documentation

[PlantUML source](document-lifecycle.puml)

## Modeled elements

| Element | Responsibility | Contract | Source |
| --- | --- | --- | --- |
| Draft | Accept author changes | Not yet trusted | [`docs/architecture/project/FRONTMATTER.md`](../../../../docs/architecture/project/FRONTMATTER.md) |
| Validated | Pass structure, links and correspondence checks | No blocking finding | [`tests/gates/test_architecture_documentation_gate.py`](../../../../tests/gates/test_architecture_documentation_gate.py) |
| Published | Appear in navigation and canon | Role and owner visible | [`mkdocs.yml`](../../../../mkdocs.yml) |
| Stale | Record detected code or decision drift | Must be reconciled or archived | [`docs/architecture/DOC-HEALTH.md`](../../../../docs/architecture/DOC-HEALTH.md) |

## Modeled relationships

| From | To | Semantics | Contract | Source |
| --- | --- | --- | --- | --- |
| Initial | Draft | document created | declared role | catalog contract |
| Draft | Validated | checks pass | links and correspondence valid | [`tests/gates/test_architecture_documentation_gate.py`](../../../../tests/gates/test_architecture_documentation_gate.py) |
| Validated | Published | navigation includes source | discoverable canonical path | [`mkdocs.yml`](../../../../mkdocs.yml) |
| Published | Stale | code or decision drifts | drift finding linked | [`docs/architecture/DOC-HEALTH.md`](../../../../docs/architecture/DOC-HEALTH.md) |
| Stale | Draft | reconciliation starts | owner assigned | catalog contract |

Generated deterministically from Better Tomorrow's semantic model catalog; edit the catalog, not this projection.
