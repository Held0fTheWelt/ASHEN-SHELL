# Architecture Assurance - Evidence Model

**Viewpoint:** `class`
**Concern:** Declarations, correspondence bindings and explainable findings

[PlantUML source](evidence-model.puml)

## Modeled elements

| Element | Responsibility | Contract | Source |
| --- | --- | --- | --- |
| Architecture Declarations | Capture decisions, qualities and constraints | Stable SAD identifiers | [`tools/architecture_assurance/sad_parser.py`](../../../../tools/architecture_assurance/sad_parser.py) |
| Correspondence Bindings | Relate declarations to implementation evidence | Existing paths and explicit kinds | [`tools/architecture_assurance/manifest_builder.py`](../../../../tools/architecture_assurance/manifest_builder.py) |
| Audit Findings | Explain drift with stable identifiers | severity, scope, evidence and remediation | [`tools/architecture_assurance/reporters.py`](../../../../tools/architecture_assurance/reporters.py) |

## Modeled relationships

| From | To | Semantics | Contract | Source |
| --- | --- | --- | --- | --- |
| Architecture Declarations | Correspondence Bindings | are grounded by | stable declaration ids | [`tools/architecture_assurance/manifest_builder.py`](../../../../tools/architecture_assurance/manifest_builder.py) |
| Correspondence Bindings | Audit Findings | produce gaps or proof | traceable evidence locations | [`tools/architecture_assurance/audit.py`](../../../../tools/architecture_assurance/audit.py) |

Generated deterministically from Better Tomorrow's semantic model catalog; edit the catalog, not this projection.
