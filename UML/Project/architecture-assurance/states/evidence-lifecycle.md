# Architecture Assurance - Evidence Lifecycle

**Viewpoint:** `state`
**Concern:** Intent, correlation, evaluation, export and later drift

[PlantUML source](evidence-lifecycle.puml)

## Modeled elements

| Element | Responsibility | Contract | Source |
| --- | --- | --- | --- |
| Authored Intent | Hold human-reviewed architecture intent | SAD and catalog valid | [`tools/architecture_assurance/model_catalog.json`](../../../../tools/architecture_assurance/model_catalog.json) |
| Correlated | Bind intent to code, Git and archaeology evidence | No unresolved source anchors | [`tools/architecture_assurance/manifest_builder.py`](../../../../tools/architecture_assurance/manifest_builder.py) |
| Evaluated | Classify correspondence and drift | Deterministic findings | [`tools/architecture_assurance/audit.py`](../../../../tools/architecture_assurance/audit.py) |
| Exported | Publish reports and AKDB canon | Idempotent artifacts | [`tools/architecture_assurance/canon.py`](../../../../tools/architecture_assurance/canon.py) |

## Modeled relationships

| From | To | Semantics | Contract | Source |
| --- | --- | --- | --- | --- |
| Initial | Authored Intent | intent accepted | catalog and SAD parse | catalog contract |
| Authored Intent | Correlated | sources and Git resolve | no fabricated anchor | [`tools/architecture_assurance/manifest_builder.py`](../../../../tools/architecture_assurance/manifest_builder.py) |
| Correlated | Evaluated | gates execute | complete audit result | [`tools/architecture_assurance/audit.py`](../../../../tools/architecture_assurance/audit.py) |
| Evaluated | Exported | formats and canon written | deterministic output | [`tools/architecture_assurance/reporters.py`](../../../../tools/architecture_assurance/reporters.py) |
| Exported | Evaluated | drift detected later | rerun from current source | catalog contract |

Generated deterministically from Better Tomorrow's semantic model catalog; edit the catalog, not this projection.
