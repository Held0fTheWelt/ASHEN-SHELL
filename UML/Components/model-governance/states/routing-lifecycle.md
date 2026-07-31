# Model Governance - Routing Lifecycle

**Viewpoint:** `state`
**Concern:** Configure, route and persist governance snapshots only

[PlantUML source](routing-lifecycle.puml)

## Modeled elements

| Element | Responsibility | Contract | Source |
| --- | --- | --- | --- |
| Configured | Hold registry and policy | Ready for routing | [`backend/app/model_governance/routing_registry_bootstrap.py`](../../../../backend/app/model_governance/routing_registry_bootstrap.py) |
| Routed | Adapter selected for a call | No narrative commit | [`backend/app/model_governance/model_routing.py`](../../../../backend/app/model_governance/model_routing.py) |
| Governance Snapshot Persisted | Store governance session snapshot | Non-authoritative relative to world-engine | [`backend/app/model_governance/session/session_persistence.py`](../../../../backend/app/model_governance/session/session_persistence.py) |

## Modeled relationships

| From | To | Semantics | Contract | Source |
| --- | --- | --- | --- | --- |
| Initial | Configured | registry bootstrapped | adapters available | [`backend/app/model_governance/routing_registry_bootstrap.py`](../../../../backend/app/model_governance/routing_registry_bootstrap.py) |
| Configured | Routed | adapter chosen | policy applied | [`backend/app/model_governance/model_routing.py`](../../../../backend/app/model_governance/model_routing.py) |
| Routed | Governance Snapshot Persisted | snapshot written | governance-only persistence | [`backend/app/model_governance/session/session_persistence.py`](../../../../backend/app/model_governance/session/session_persistence.py) |
| Governance Snapshot Persisted | Final | pipeline complete | no live commit | catalog contract |

Generated deterministically from Better Tomorrow's semantic model catalog; edit the catalog, not this projection.
