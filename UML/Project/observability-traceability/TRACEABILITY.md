# Observability and Traceability UML traceability

| View | Kind | Decisions | Source anchors |
| --- | --- | --- | --- |
| [Observability - Context](context/observability-context.md) | `context` | D1 | `administration-tool/templates/manage/diagnosis.html`, `docs/architecture/project/observability-traceability/architecture.md` |
| [Observability - Components](components/trace-components.md) | `component` | D1, D2 | `ai_stack/langfuse/langfuse_evidence.py`, `backend/app/api/v1/game/player_turn_trace_start.py`, `backend/app/api/v1/game/trace_identity_and_auth_helpers.py`, `tools/mcp_server/langfuse_tracing.py`, `world-engine/world_engine/observability/trace.py`, `world-engine/world_engine/story_runtime/governed_runtime_adapters.py`, `world-engine/world_engine/web/static/ui_traces.js` |
| [Observability - Turn Trace](sequence/turn-trace.md) | `sequence` | D1 | `ai_stack/langfuse/langfuse_evidence.py`, `backend/app/api/v1/game/player_turn_trace_start.py`, `backend/app/api/v1/game/trace_identity_and_auth_helpers.py`, `world-engine/world_engine/observability/trace.py`, `world-engine/world_engine/story_runtime/governed_runtime_adapters.py`, `world-engine/world_engine/web/static/ui_traces.js` |
| [Observability - Data Model](classes/trace-data-model.md) | `class` | D2 | `ai_stack/langfuse/langfuse_evidence.py`, `world-engine/world_engine/observability/audit_log.py`, `world-engine/world_engine/observability/trace.py` |
| [Observability - Trace Lifecycle](states/trace-lifecycle.md) | `state` | D3 | `backend/app/api/v1/game/player_turn_trace_start.py`, `world-engine/world_engine/middleware/trace_middleware.py`, `world-engine/world_engine/observability/langfuse_adapter.py`, `world-engine/world_engine/observability/trace.py`, `world-engine/world_engine/web/static/ui_traces.js` |

The table is a generated correspondence view. Source paths are validated before projection.
