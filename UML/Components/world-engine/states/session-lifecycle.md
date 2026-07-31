# World Engine - Session Lifecycle

**Viewpoint:** `state`
**Concern:** Session creation, serialized turns, degradation, recovery and closure

[PlantUML source](session-lifecycle.puml)

## Modeled elements

| Element | Responsibility | Contract | Source |
| --- | --- | --- | --- |
| New | Await initial content/session binding | No player turn | [`world-engine/world_engine/api/http_routes/story_session_lifecycle_routes.py`](../../../../world-engine/world_engine/api/http_routes/story_session_lifecycle_routes.py) |
| Active | Accept canonical turns | Bound content and actor | [`world-engine/world_engine/story_runtime/manager/runtime_manager.py`](../../../../world-engine/world_engine/story_runtime/manager/runtime_manager.py) |
| Executing Turn | Hold one in-flight command | Serialized session mutation | [`world-engine/world_engine/story_runtime/manager/turn_execution.py`](../../../../world-engine/world_engine/story_runtime/manager/turn_execution.py) |
| Degraded | Preserve session during provider or validation failure | No fabricated commit | [`world-engine/world_engine/narrative/fallback_generator.py`](../../../../world-engine/world_engine/narrative/fallback_generator.py) |
| Closed | Reject further turns and retain evidence | Final persisted revision | [`world-engine/world_engine/api/http_routes/story_session_lifecycle_routes.py`](../../../../world-engine/world_engine/api/http_routes/story_session_lifecycle_routes.py) |

## Modeled relationships

| From | To | Semantics | Contract | Source |
| --- | --- | --- | --- | --- |
| Initial | New | session created | unique id | catalog contract |
| New | Active | content and actor bound | valid launch | [`world-engine/world_engine/api/http_routes/story_session_lifecycle_routes.py`](../../../../world-engine/world_engine/api/http_routes/story_session_lifecycle_routes.py) |
| Active | Executing Turn | turn accepted | session lock | [`world-engine/world_engine/story_runtime/manager/turn_execution.py`](../../../../world-engine/world_engine/story_runtime/manager/turn_execution.py) |
| Executing Turn | Active | commit or rejection completes | evidence persisted | [`world-engine/world_engine/story_runtime/narrative_commit_resolution.py`](../../../../world-engine/world_engine/story_runtime/narrative_commit_resolution.py) |
| Executing Turn | Degraded | dependency failure | no speculative commit | [`world-engine/world_engine/narrative/fallback_generator.py`](../../../../world-engine/world_engine/narrative/fallback_generator.py) |
| Degraded | Active | safe recovery | same committed revision | [`world-engine/world_engine/runtime/engine.py`](../../../../world-engine/world_engine/runtime/engine.py) |
| Active | Closed | session closed | final revision retained | [`world-engine/world_engine/api/http_routes/story_session_lifecycle_routes.py`](../../../../world-engine/world_engine/api/http_routes/story_session_lifecycle_routes.py) |
| Closed | Final | retention complete | immutable evidence | catalog contract |

Generated deterministically from Better Tomorrow's semantic model catalog; edit the catalog, not this projection.
