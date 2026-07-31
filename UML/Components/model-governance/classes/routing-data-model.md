# Model Governance - Data Model

**Viewpoint:** `class`
**Concern:** Governance session models and routing decisions

[PlantUML source](routing-data-model.puml)

## Modeled elements

| Element | Responsibility | Contract | Source |
| --- | --- | --- | --- |
| Runtime Models | Carry SessionState and turn deltas for governance pipelines | Pydantic value objects | [`backend/app/model_governance/runtime_models.py`](../../../../backend/app/model_governance/runtime_models.py) |
| Routing Decision | Explain adapter selection | Auditable routing evidence | [`backend/app/model_governance/model_routing.py`](../../../../backend/app/model_governance/model_routing.py) |

## Modeled relationships

| From | To | Semantics | Contract | Source |
| --- | --- | --- | --- | --- |
| Runtime Models | Routing Decision | bounds routing evidence | explainable selection | [`backend/app/model_governance/runtime_models.py`](../../../../backend/app/model_governance/runtime_models.py) |

Generated deterministically from Better Tomorrow's semantic model catalog; edit the catalog, not this projection.
