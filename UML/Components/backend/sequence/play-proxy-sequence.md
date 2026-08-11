# Backend — Player Turn Proxy

**Viewpoint:** `sequence`
**Concern:** How backend creates trace/ticket context and delegates the live turn

[PlantUML source](play-proxy-sequence.puml)

## Modeled elements

| Element | Responsibility | Contract | Source |
| --- | --- | --- | --- |
| Player | Authenticate, browse community and start or continue play | Browser/API session | [`docs/architecture/components/backend/architecture.md`](../../../../docs/architecture/components/backend/architecture.md) |
| Backend | Own platform data and governed control-plane operations | Flask /api/v1 | [`backend/app/factory_app.py`](../../../../backend/app/factory_app.py) |
| Game API | Create run bindings and proxy live play operations | No backend-local narrative commit | [`backend/app/api/v1/game/player_turn_execution_and_flush.py`](../../../../backend/app/api/v1/game/player_turn_execution_and_flush.py) |
| Game Service | Call world-engine and map service responses | Internal HTTP and signed ticket | [`backend/app/services/game/game_service.py`](../../../../backend/app/services/game/game_service.py) |
| World Engine | Own live story sessions and commits | Internal story HTTP API plus signed ticket | [`world-engine/world_engine/main.py`](../../../../world-engine/world_engine/main.py) |
| Observability | Record platform traces, metrics and diagnostic evidence | Trace correlation with redaction | [`backend/app/observability/__init__.py`](../../../../backend/app/observability/__init__.py) |

## Modeled relationships

| From | To | Semantics | Contract | Source |
| --- | --- | --- | --- | --- |
| Player | Backend | uses platform API | authenticated HTTP | [`backend/app/api/v1/auth_routes.py`](../../../../backend/app/api/v1/auth_routes.py) |
| Backend | Game API | routes authenticated player turn | validated game API request | [`backend/app/api/v1/game/player_turn_execution_and_flush.py`](../../../../backend/app/api/v1/game/player_turn_execution_and_flush.py) |
| Game API | Game Service | delegates live operation | proxy-only service seam | [`backend/app/api/v1/game/player_turn_execution_and_flush.py`](../../../../backend/app/api/v1/game/player_turn_execution_and_flush.py) |
| Game Service | World Engine | calls story API | ticketed HTTP request | [`backend/app/services/game/game_service.py`](../../../../backend/app/services/game/game_service.py) |
| Game Service | Observability | records proxy outcome | trace-correlated redacted evidence | [`backend/app/services/game/game_service.py`](../../../../backend/app/services/game/game_service.py) |

Generated deterministically from Better Tomorrow's semantic model catalog; edit the catalog, not this projection.
