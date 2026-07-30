# Architecture Assurance - Audit Flow

**Viewpoint:** `activity`
**Concern:** From authored intent and source discovery to classified evidence

[PlantUML source](audit-flow.puml)

## Modeled elements

| Element | Responsibility | Contract | Source |
| --- | --- | --- | --- |
| Semantic Model Catalog | Define individualized elements, contracts, relations and viewpoints | Validated source-bound JSON | [`tools/architecture_assurance/model_catalog.json`](../../../../tools/architecture_assurance/model_catalog.json) |
| Repository Discovery | Enumerate implementation and document evidence | Ignored/local evidence excluded | [`tools/architecture_assurance/discovery.py`](../../../../tools/architecture_assurance/discovery.py) |
| Binding Manifest Builder | Bind SAD declarations to source, tests and views | One deterministic manifest per scope | [`tools/architecture_assurance/manifest_builder.py`](../../../../tools/architecture_assurance/manifest_builder.py) |
| Semantic View Builder | Project catalog models into PlantUML and companion documents | No generic inferred star graphs | [`tools/architecture_assurance/view_builder.py`](../../../../tools/architecture_assurance/view_builder.py) |
| Audit Engine | Evaluate correspondence and model semantics | Stable findings and exit policy | [`tools/architecture_assurance/audit.py`](../../../../tools/architecture_assurance/audit.py) |
| Report Exporters | Emit human, JSON, JUnit and SARIF evidence | Schema-stable deterministic serialization | [`tools/architecture_assurance/reporters.py`](../../../../tools/architecture_assurance/reporters.py) |

## Modeled relationships

| From | To | Semantics | Contract | Source |
| --- | --- | --- | --- | --- |
| Semantic Model Catalog | Repository Discovery | scopes evidence | history roots and source anchors | [`tools/architecture_assurance/model_catalog.json`](../../../../tools/architecture_assurance/model_catalog.json) |
| Repository Discovery | Binding Manifest Builder | supplies inventory | normalized repository paths | [`tools/architecture_assurance/discovery.py`](../../../../tools/architecture_assurance/discovery.py) |
| Semantic Model Catalog | Semantic View Builder | projects viewpoints | semantic elements and edge contracts | [`tools/architecture_assurance/semantic_models.py`](../../../../tools/architecture_assurance/semantic_models.py) |
| Binding Manifest Builder | Audit Engine | supplies declared correspondence | binding schema | [`tools/architecture_assurance/audit.py`](../../../../tools/architecture_assurance/audit.py) |
| Semantic View Builder | Audit Engine | supplies analyzable models | view requirements and source links | [`tools/architecture_assurance/semantic_models.py`](../../../../tools/architecture_assurance/semantic_models.py) |
| Audit Engine | Report Exporters | emits findings | normalized result model | [`tools/architecture_assurance/reporters.py`](../../../../tools/architecture_assurance/reporters.py) |

Generated deterministically from Better Tomorrow's semantic model catalog; edit the catalog, not this projection.
