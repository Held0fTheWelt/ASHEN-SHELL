# Model Governance - Authority Context

**Viewpoint:** `context`
**Concern:** Routing package versus live world-engine authority

[PlantUML source](authority-context.puml)

## Modeled elements

| Element | Responsibility | Contract | Source |
| --- | --- | --- | --- |
| Operator / Platform | Configure and invoke model routing without owning live commits | Privileged or internal platform call | [`backend/app/model_governance/__init__.py`](../../../../backend/app/model_governance/__init__.py) |
| Model Governance | Route adapters and shape in-process governance sessions | Python package under backend/app/model_governance | [`backend/app/model_governance/__init__.py`](../../../../backend/app/model_governance/__init__.py) |
| World Engine | Own live story commits | Authoritative play service | [`world-engine/world_engine/main.py`](../../../../world-engine/world_engine/main.py) |

## Modeled relationships

| From | To | Semantics | Contract | Source |
| --- | --- | --- | --- | --- |
| Operator / Platform | Model Governance | configures routing | platform intent | [`backend/app/model_governance/__init__.py`](../../../../backend/app/model_governance/__init__.py) |
| Model Governance | World Engine | never commits live truth | authority boundary | [`tests/gates/test_runtime_sessions_table_absent.py`](../../../../tests/gates/test_runtime_sessions_table_absent.py) |

Generated deterministically from Better Tomorrow's semantic model catalog; edit the catalog, not this projection.
