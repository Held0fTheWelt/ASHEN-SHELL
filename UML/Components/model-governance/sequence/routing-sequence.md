# Model Governance - Routing Sequence

**Viewpoint:** `sequence`
**Concern:** Adapter selection without live commit

[PlantUML source](routing-sequence.puml)

## Modeled elements

| Element | Responsibility | Contract | Source |
| --- | --- | --- | --- |
| Operator / Platform | Configure and invoke model routing without owning live commits | Privileged or internal platform call | [`backend/app/model_governance/__init__.py`](../../../../backend/app/model_governance/__init__.py) |
| Model Governance | Route adapters and shape in-process governance sessions | Python package under backend/app/model_governance | [`backend/app/model_governance/__init__.py`](../../../../backend/app/model_governance/__init__.py) |
| Model Routing | Choose adapters and record routing decisions | Routing policy without commit side effects | [`backend/app/model_governance/model_routing.py`](../../../../backend/app/model_governance/model_routing.py) |
| Adapter Registry | Register available AI adapters | Explicit registry bootstrap | [`backend/app/model_governance/adapter_registry.py`](../../../../backend/app/model_governance/adapter_registry.py) |
| Routing Contracts | Define routing decision vocabulary | Serializable contract types | [`backend/app/model_governance/model_routing_contracts.py`](../../../../backend/app/model_governance/model_routing_contracts.py) |
| Governance Session Persistence | Serialize in-process governance session shape | JSON-compatible snapshot; not live WE authority | [`backend/app/model_governance/session/session_persistence.py`](../../../../backend/app/model_governance/session/session_persistence.py) |

## Modeled relationships

| From | To | Semantics | Contract | Source |
| --- | --- | --- | --- | --- |
| Operator / Platform | Model Governance | configures routing | platform intent | [`backend/app/model_governance/__init__.py`](../../../../backend/app/model_governance/__init__.py) |
| Model Governance | Model Routing | selects adapter | routing-only side effect | [`backend/app/model_governance/model_routing.py`](../../../../backend/app/model_governance/model_routing.py) |
| Model Routing | Adapter Registry | resolves adapters | registered adapters only | [`backend/app/model_governance/adapter_registry.py`](../../../../backend/app/model_governance/adapter_registry.py) |
| Model Routing | Routing Contracts | emits decision vocabulary | stable contract types | [`backend/app/model_governance/model_routing_contracts.py`](../../../../backend/app/model_governance/model_routing_contracts.py) |
| Model Governance | Governance Session Persistence | persists governance snapshot | non-authoritative snapshot | [`backend/app/model_governance/session/session_persistence.py`](../../../../backend/app/model_governance/session/session_persistence.py) |

Generated deterministically from Better Tomorrow's semantic model catalog; edit the catalog, not this projection.
