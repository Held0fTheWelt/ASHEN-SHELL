# Model Governance UML traceability

| View | Kind | Decisions | Source anchors |
| --- | --- | --- | --- |
| [Model Governance - Authority Context](context/authority-context.md) | `context` | D1 | `backend/app/model_governance/__init__.py`, `tests/gates/test_runtime_sessions_table_absent.py`, `world-engine/world_engine/main.py` |
| [Model Governance - Components](components/routing-components.md) | `component` | D1 | `backend/app/model_governance/__init__.py`, `backend/app/model_governance/adapter_registry.py`, `backend/app/model_governance/model_routing.py`, `backend/app/model_governance/model_routing_contracts.py`, `backend/app/model_governance/session/session_persistence.py` |
| [Model Governance - Routing Sequence](sequence/routing-sequence.md) | `sequence` | D1 | `backend/app/model_governance/__init__.py`, `backend/app/model_governance/adapter_registry.py`, `backend/app/model_governance/model_routing.py`, `backend/app/model_governance/model_routing_contracts.py`, `backend/app/model_governance/session/session_persistence.py` |
| [Model Governance - Data Model](classes/routing-data-model.md) | `class` | D1 | `backend/app/model_governance/model_routing.py`, `backend/app/model_governance/runtime_models.py` |
| [Model Governance - Routing Lifecycle](states/routing-lifecycle.md) | `state` | D1 | `backend/app/model_governance/model_routing.py`, `backend/app/model_governance/routing_registry_bootstrap.py`, `backend/app/model_governance/session/session_persistence.py` |

The table is a generated correspondence view. Source paths are validated before projection.
