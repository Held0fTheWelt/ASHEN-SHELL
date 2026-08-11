# Architecture Assurance - Audit Flow

**Viewpoint:** `activity`
**Concern:** From authored intent and source discovery through drift invariants to classified evidence

[PlantUML source](audit-flow.puml)

## Modeled elements

| Element | Responsibility | Contract | Source |
| --- | --- | --- | --- |
| Semantic Model Catalog | Define individualized elements, contracts, relations and viewpoints | Validated source-bound JSON with no retired placeholder evidence | [`tools/architecture_assurance/model_catalog.json`](../../../../tools/architecture_assurance/model_catalog.json) |
| Repository Discovery | Enumerate implementation and document evidence | Ignored/local evidence excluded | [`tools/architecture_assurance/discovery.py`](../../../../tools/architecture_assurance/discovery.py) |
| Binding Manifest Builder | Bind SAD declarations to source, tests and views | One deterministic manifest per scope | [`tools/architecture_assurance/manifest_builder.py`](../../../../tools/architecture_assurance/manifest_builder.py) |
| Semantic View Builder | Project catalog models into PlantUML and companion documents | No generic inferred star graphs | [`tools/architecture_assurance/view_builder.py`](../../../../tools/architecture_assurance/view_builder.py) |
| Drift Edge Catalog | Describe authority, proposal, projection and evidence flows | Resolvable model nodes, claim ids, source anchors and carried fields | [`tools/architecture_assurance/drift_edge_catalog.json`](../../../../tools/architecture_assurance/drift_edge_catalog.json) |
| Authority and Envelope Gate | Resolve drift edges and reject competing writers or lost envelope fields | Source-bound topology with stable CI rule identifiers | [`tools/architecture_assurance/drift_edges.py`](../../../../tools/architecture_assurance/drift_edges.py) |
| Audit Engine | Evaluate correspondence and model semantics | Stable findings and exit policy | [`tools/architecture_assurance/audit.py`](../../../../tools/architecture_assurance/audit.py) |
| Report Exporters | Emit human, JSON, JUnit and SARIF evidence | Schema-stable deterministic serialization | [`tools/architecture_assurance/reporters.py`](../../../../tools/architecture_assurance/reporters.py) |

## Modeled relationships

| From | To | Semantics | Contract | Source |
| --- | --- | --- | --- | --- |
| Semantic Model Catalog | Repository Discovery | scopes evidence | history roots and source anchors | [`tools/architecture_assurance/model_catalog.json`](../../../../tools/architecture_assurance/model_catalog.json) |
| Repository Discovery | Binding Manifest Builder | supplies inventory | normalized repository paths | [`tools/architecture_assurance/discovery.py`](../../../../tools/architecture_assurance/discovery.py) |
| Semantic Model Catalog | Semantic View Builder | projects viewpoints | semantic elements and edge contracts | [`tools/architecture_assurance/semantic_models.py`](../../../../tools/architecture_assurance/semantic_models.py) |
| Semantic Model Catalog | Drift Edge Catalog | resolves drift topology | subsystem and element references | [`tools/architecture_assurance/drift_edges.py`](../../../../tools/architecture_assurance/drift_edges.py) |
| Drift Edge Catalog | Authority and Envelope Gate | supplies authority and field-flow contracts | versioned drift-edge schema | [`tools/architecture_assurance/drift_edge_catalog.json`](../../../../tools/architecture_assurance/drift_edge_catalog.json) |
| Binding Manifest Builder | Audit Engine | supplies declared correspondence | binding schema | [`tools/architecture_assurance/audit.py`](../../../../tools/architecture_assurance/audit.py) |
| Semantic View Builder | Audit Engine | supplies analyzable models | view requirements and source links | [`tools/architecture_assurance/semantic_models.py`](../../../../tools/architecture_assurance/semantic_models.py) |
| Authority and Envelope Gate | Audit Engine | emits hard invariant findings | write-conflict and field-loss rules | [`tools/architecture_assurance/drift_edges.py`](../../../../tools/architecture_assurance/drift_edges.py) |
| Audit Engine | Report Exporters | emits findings | normalized result model | [`tools/architecture_assurance/reporters.py`](../../../../tools/architecture_assurance/reporters.py) |

Generated deterministically from Better Tomorrow's semantic model catalog; edit the catalog, not this projection.
