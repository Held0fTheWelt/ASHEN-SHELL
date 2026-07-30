# World Engine - Runtime Containers

**Viewpoint:** `container`
**Concern:** API, canonical manager, compatibility runtime, persistence and observability

[PlantUML source](c4-container.puml)

## Modeled elements

| Element | Responsibility | Contract | Source |
| --- | --- | --- | --- |
| Story API | Expose health, package, session, turn and branching routes | Validated HTTP/WS envelopes | [`world-engine/app/api/http.py`](../../../../world-engine/app/api/http.py) |
| Story Runtime Manager | Coordinate canonical sessions and turns | Single live authority | [`world-engine/app/story_runtime/manager/runtime_manager.py`](../../../../world-engine/app/story_runtime/manager/runtime_manager.py) |
| Compatibility Runtime | Host legacy engine profiles and transitional behavior | Explicitly non-canonical where overlapped | [`world-engine/app/runtime/manager.py`](../../../../world-engine/app/runtime/manager.py) |
| Session Stores | Persist committed session, branches and callbacks | Commit-versioned state | [`world-engine/app/story_runtime/story_session_store.py`](../../../../world-engine/app/story_runtime/story_session_store.py) |
| Runtime Observability | Correlate turn lifecycle and failures | Redacted trace tree | [`world-engine/app/observability/trace.py`](../../../../world-engine/app/observability/trace.py) |

## Modeled relationships

| From | To | Semantics | Contract | Source |
| --- | --- | --- | --- | --- |
| Story API | Story Runtime Manager | delegates story operation | validated command | [`world-engine/app/api/http_routes/story_turn_routes.py`](../../../../world-engine/app/api/http_routes/story_turn_routes.py) |
| Compatibility Runtime | Story Runtime Manager | adapts supported legacy paths | explicit compatibility seam | [`world-engine/app/runtime/manager.py`](../../../../world-engine/app/runtime/manager.py) |
| Story Runtime Manager | Session Stores | loads and stores session | revision-safe transaction | [`world-engine/app/story_runtime/story_session_store.py`](../../../../world-engine/app/story_runtime/story_session_store.py) |
| Story Runtime Manager | Runtime Observability | emits lifecycle evidence | trace-correlated spans | [`world-engine/app/observability/trace.py`](../../../../world-engine/app/observability/trace.py) |

Generated deterministically from Better Tomorrow's semantic model catalog; edit the catalog, not this projection.
