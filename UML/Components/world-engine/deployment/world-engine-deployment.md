# World Engine - Deployment

**Viewpoint:** `deployment`
**Concern:** Client boundary, authoritative service, AI collaborator and session persistence

[PlantUML source](world-engine-deployment.puml)

## Modeled elements

| Element | Responsibility | Contract | Source |
| --- | --- | --- | --- |
| Backend/Browser Clients | Call story endpoints and consume events | HTTP/WebSocket | [`world-engine/world_engine/api/http.py`](../../../../world-engine/world_engine/api/http.py) |
| World Engine Process | Host authoritative runtime | Python service | [`world-engine/Dockerfile`](../../../../world-engine/Dockerfile) |
| AI Runtime | Produce proposals | In-process/service adapter | [`ai_stack/langgraph/langgraph_runtime_executor.py`](../../../../ai_stack/langgraph/langgraph_runtime_executor.py) |
| Session Persistence | Persist committed state and evidence | Atomic revision storage | [`world-engine/world_engine/story_runtime/persist_outcome.py`](../../../../world-engine/world_engine/story_runtime/persist_outcome.py) |

## Modeled relationships

| From | To | Semantics | Contract | Source |
| --- | --- | --- | --- | --- |
| Backend/Browser Clients | World Engine Process | HTTP/WebSocket | ticketed story API | catalog contract |
| World Engine Process | AI Runtime | proposal call | bounded trace context | [`world-engine/world_engine/story_runtime/governed_runtime_adapters.py`](../../../../world-engine/world_engine/story_runtime/governed_runtime_adapters.py) |
| World Engine Process | Session Persistence | commit transaction | monotonic session revision | [`world-engine/world_engine/story_runtime/story_session_store.py`](../../../../world-engine/world_engine/story_runtime/story_session_store.py) |

Generated deterministically from Better Tomorrow's semantic model catalog; edit the catalog, not this projection.
