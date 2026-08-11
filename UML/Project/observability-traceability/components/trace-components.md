# Observability - Components

**Viewpoint:** `component`
**Concern:** Backend, world, AI, MCP and operator projection span ownership

[PlantUML source](trace-components.puml)

## Modeled elements

| Element | Responsibility | Contract | Source |
| --- | --- | --- | --- |
| Backend Trace Start | Create or propagate player request identity | Stable trace and request ids | [`backend/app/api/v1/game_routes_impl.py`](../../../../backend/app/api/v1/game_routes_impl.py) |
| World Runtime Trace | Record authoritative lifecycle spans | Session and revision correlation | [`world-engine/world_engine/observability/trace.py`](../../../../world-engine/world_engine/observability/trace.py) |
| AI Langfuse Evidence | Record retrieval, planning, generation and validation spans | Proposal trace under parent turn | [`ai_stack/langfuse/langfuse_evidence.py`](../../../../ai_stack/langfuse/langfuse_evidence.py) |
| MCP Trace Adapter | Record tool execution with redaction | No secret payloads | [`tools/mcp_server/langfuse_tracing.py`](../../../../tools/mcp_server/langfuse_tracing.py) |
| Operator Projection | Present cross-service trace tree and diagnostics | Read-only evidence view | [`world-engine/world_engine/web/static/ui_traces.js`](../../../../world-engine/world_engine/web/static/ui_traces.js) |

## Modeled relationships

| From | To | Semantics | Contract | Source |
| --- | --- | --- | --- | --- |
| Backend Trace Start | World Runtime Trace | propagates trace context | trace and request ids | [`backend/app/api/v1/game_routes_impl.py`](../../../../backend/app/api/v1/game_routes_impl.py) |
| World Runtime Trace | AI Langfuse Evidence | parents proposal trace | turn trace context | [`world-engine/world_engine/story_runtime/governed_runtime_adapters.py`](../../../../world-engine/world_engine/story_runtime/governed_runtime_adapters.py) |
| AI Langfuse Evidence | World Runtime Trace | returns evidence references | proposal span linkage | [`ai_stack/langfuse/langfuse_evidence.py`](../../../../ai_stack/langfuse/langfuse_evidence.py) |
| World Runtime Trace | Operator Projection | publishes lifecycle evidence | redacted trace DTO | [`world-engine/world_engine/web/static/ui_traces.js`](../../../../world-engine/world_engine/web/static/ui_traces.js) |
| MCP Trace Adapter | Operator Projection | adds tool evidence | redacted MCP span | [`tools/mcp_server/langfuse_tracing.py`](../../../../tools/mcp_server/langfuse_tracing.py) |

Generated deterministically from Better Tomorrow's semantic model catalog; edit the catalog, not this projection.
