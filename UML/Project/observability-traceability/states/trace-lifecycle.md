# Observability - Trace Lifecycle

**Viewpoint:** `state`
**Concern:** Complete and partial telemetry both disclose their evidence quality

[PlantUML source](trace-lifecycle.puml)

## Modeled elements

| Element | Responsibility | Contract | Source |
| --- | --- | --- | --- |
| Started | Establish trace identity | Trace id present | [`backend/app/api/v1/game/player_turn_trace_start.py`](../../../../backend/app/api/v1/game/player_turn_trace_start.py) |
| Propagating | Carry identity across service boundaries | Parent context retained | [`world-engine/app/middleware/trace_middleware.py`](../../../../world-engine/app/middleware/trace_middleware.py) |
| Complete | Close all required spans | Terminal outcome recorded | [`world-engine/app/observability/trace.py`](../../../../world-engine/app/observability/trace.py) |
| Partial | Retain useful evidence after telemetry failure | Domain flow not failed solely by telemetry | [`world-engine/app/observability/langfuse_adapter.py`](../../../../world-engine/app/observability/langfuse_adapter.py) |
| Redacted | Publish safe operator evidence | Secrets and sensitive text removed | [`world-engine/app/web/static/ui_traces.js`](../../../../world-engine/app/web/static/ui_traces.js) |

## Modeled relationships

| From | To | Semantics | Contract | Source |
| --- | --- | --- | --- | --- |
| Initial | Started | request accepted | trace id | catalog contract |
| Started | Propagating | boundary crossed | parent context | [`world-engine/app/middleware/trace_middleware.py`](../../../../world-engine/app/middleware/trace_middleware.py) |
| Propagating | Complete | all terminal spans close | turn outcome | catalog contract |
| Propagating | Partial | telemetry degrades | domain flow preserved | [`world-engine/app/observability/langfuse_adapter.py`](../../../../world-engine/app/observability/langfuse_adapter.py) |
| Complete | Redacted | operator view generated | safe evidence projection | catalog contract |
| Partial | Redacted | partial view generated | missing spans disclosed | catalog contract |

Generated deterministically from Better Tomorrow's semantic model catalog; edit the catalog, not this projection.
