# Observability - Turn Trace

**Viewpoint:** `sequence`
**Concern:** Trace identity and evidence cross the canonical turn boundaries

[PlantUML source](turn-trace.puml)

## Modeled elements

| Element | Responsibility | Contract | Source |
| --- | --- | --- | --- |
| Backend Trace Start | Create or propagate player request identity | Stable trace and request ids | [`backend/app/api/v1/game/player_turn_trace_start.py`](../../../../backend/app/api/v1/game/player_turn_trace_start.py) |
| World Runtime Trace | Record authoritative lifecycle spans | Session and revision correlation | [`world-engine/app/observability/trace.py`](../../../../world-engine/app/observability/trace.py) |
| AI Langfuse Evidence | Record retrieval, planning, generation and validation spans | Proposal trace under parent turn | [`ai_stack/langfuse/langfuse_evidence.py`](../../../../ai_stack/langfuse/langfuse_evidence.py) |
| Operator Projection | Present cross-service trace tree and diagnostics | Read-only evidence view | [`world-engine/app/web/static/ui_traces.js`](../../../../world-engine/app/web/static/ui_traces.js) |

## Modeled relationships

| From | To | Semantics | Contract | Source |
| --- | --- | --- | --- | --- |
| Backend Trace Start | World Runtime Trace | propagates trace context | trace and request ids | [`backend/app/api/v1/game/trace_identity_and_auth_helpers.py`](../../../../backend/app/api/v1/game/trace_identity_and_auth_helpers.py) |
| World Runtime Trace | AI Langfuse Evidence | parents proposal trace | turn trace context | [`world-engine/app/story_runtime/governed_runtime_adapters.py`](../../../../world-engine/app/story_runtime/governed_runtime_adapters.py) |
| AI Langfuse Evidence | World Runtime Trace | returns evidence references | proposal span linkage | [`ai_stack/langfuse/langfuse_evidence.py`](../../../../ai_stack/langfuse/langfuse_evidence.py) |
| World Runtime Trace | Operator Projection | publishes lifecycle evidence | redacted trace DTO | [`world-engine/app/web/static/ui_traces.js`](../../../../world-engine/app/web/static/ui_traces.js) |

Generated deterministically from Better Tomorrow's semantic model catalog; edit the catalog, not this projection.
