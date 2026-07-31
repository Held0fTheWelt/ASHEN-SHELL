# World Engine - Runtime Containers

**Viewpoint:** `container`
**Concern:** API, canonical manager, compatibility runtime, persistence and observability

[PlantUML source](c4-container.puml)

## Modeled elements

| Element | Responsibility | Contract | Source |
| --- | --- | --- | --- |
| Story API | Expose health, package, session, turn and branching routes | Validated HTTP/WS envelopes | [`world-engine/world_engine/api/http.py`](../../../../world-engine/world_engine/api/http.py) |
| Story Runtime Manager | Coordinate canonical sessions and turns | Single live authority | [`world-engine/world_engine/story_runtime/manager/runtime_manager.py`](../../../../world-engine/world_engine/story_runtime/manager/runtime_manager.py) |
| Compatibility Runtime | Host legacy engine profiles and transitional behavior | Explicitly non-canonical where overlapped | [`world-engine/world_engine/runtime/manager.py`](../../../../world-engine/world_engine/runtime/manager.py) |
| Session Stores | Persist committed session, branches and callbacks | Commit-versioned state | [`world-engine/world_engine/story_runtime/manager/session/manager_init_and_persistence.py`](../../../../world-engine/world_engine/story_runtime/manager/session/manager_init_and_persistence.py) |
| Runtime Observability | Correlate turn lifecycle and failures | Redacted trace tree | [`world-engine/world_engine/observability/trace.py`](../../../../world-engine/world_engine/observability/trace.py) |

## Modeled relationships

| From | To | Semantics | Contract | Source |
| --- | --- | --- | --- | --- |
| Story API | Story Runtime Manager | delegates story operation | validated command | [`world-engine/world_engine/api/http_routes/story_turn_routes.py`](../../../../world-engine/world_engine/api/http_routes/story_turn_routes.py) |
| Compatibility Runtime | Story Runtime Manager | adapts supported legacy paths | explicit compatibility seam | [`world-engine/world_engine/runtime/manager.py`](../../../../world-engine/world_engine/runtime/manager.py) |
| Story Runtime Manager | Session Stores | loads and stores session | revision-safe transaction | [`world-engine/world_engine/story_runtime/story_session_store.py`](../../../../world-engine/world_engine/story_runtime/story_session_store.py) |
| Story Runtime Manager | Runtime Observability | emits lifecycle evidence | trace-correlated spans | [`world-engine/world_engine/observability/trace.py`](../../../../world-engine/world_engine/observability/trace.py) |

Generated deterministically from Better Tomorrow's semantic model catalog; edit the catalog, not this projection.
