# Backend — Core Components

**Viewpoint:** `component`
**Concern:** Identity, play proxy, content and governance collaborations

[PlantUML source](c4-component.puml)

## Modeled elements

| Element | Responsibility | Contract | Source |
| --- | --- | --- | --- |
| Authentication API | Issue and revoke platform sessions and tokens | Password/session/refresh-token policy | [`backend/app/api/v1/auth_routes.py`](../../../../backend/app/api/v1/auth_routes.py) |
| Domain Services | Implement platform and governance use cases | Transaction-scoped service operations | [`backend/app/services/__init__.py`](../../../../backend/app/services/__init__.py) |
| Game API | Create run bindings and proxy live play operations | No backend-local narrative commit | [`backend/app/api/v1/game/player_turn_execution_and_flush.py`](../../../../backend/app/api/v1/game/player_turn_execution_and_flush.py) |
| Game Service | Call world-engine and map service responses | Internal HTTP and signed ticket | [`backend/app/services/game/game_service.py`](../../../../backend/app/services/game/game_service.py) |
| World Engine | Own live story sessions and commits | Internal story HTTP API plus signed ticket | [`world-engine/world_engine/main.py`](../../../../world-engine/world_engine/main.py) |
| Governance Services | Validate provider, route, security and runtime settings | Audit-producing admin mutation boundary | [`backend/app/services/governance/governance_runtime_service.py`](../../../../backend/app/services/governance/governance_runtime_service.py) |
| Content Services | Compile, review and publish authored content versions | Immutable version plus active pointer | [`backend/app/services/game/game_content_service.py`](../../../../backend/app/services/game/game_content_service.py) |
| Persistence Models | Represent backend and narrative-governance durable truth | SQLAlchemy models and Alembic schema | [`backend/app/models/__init__.py`](../../../../backend/app/models/__init__.py) |
| Observability | Record platform traces, metrics and diagnostic evidence | Trace correlation with redaction | [`backend/app/observability/__init__.py`](../../../../backend/app/observability/__init__.py) |

## Modeled relationships

| From | To | Semantics | Contract | Source |
| --- | --- | --- | --- | --- |
| Authentication API | Domain Services | authenticates | identity and token services | [`backend/app/api/v1/auth_routes.py`](../../../../backend/app/api/v1/auth_routes.py) |
| Game API | Game Service | delegates live operation | proxy-only service seam | [`backend/app/api/v1/game/player_turn_execution_and_flush.py`](../../../../backend/app/api/v1/game/player_turn_execution_and_flush.py) |
| Game Service | World Engine | calls story API | ticketed HTTP request | [`backend/app/services/game/game_service.py`](../../../../backend/app/services/game/game_service.py) |
| Governance Services | Persistence Models | persists settings and audit | validated governance transaction | [`backend/app/services/governance/governance_runtime_service.py`](../../../../backend/app/services/governance/governance_runtime_service.py) |
| Content Services | Persistence Models | persists package lifecycle | immutable versions and events | [`backend/app/services/game/game_content_service.py`](../../../../backend/app/services/game/game_content_service.py) |
| Domain Services | Observability | emits evidence | redacted trace correlation | [`backend/app/observability/trace.py`](../../../../backend/app/observability/trace.py) |

Generated deterministically from Better Tomorrow's semantic model catalog; edit the catalog, not this projection.
