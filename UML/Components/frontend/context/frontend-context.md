# Frontend - System Context

**Viewpoint:** `context`
**Concern:** Presentation boundary across player, backend and world-engine

[PlantUML source](frontend-context.puml)

## Modeled elements

| Element | Responsibility | Contract | Source |
| --- | --- | --- | --- |
| Player | Launch and interact with a story session | Authenticated browser interaction | [`frontend/templates/session_shell.html`](../../../../frontend/templates/session_shell.html) |
| Frontend | Render platform pages and live play shell | Flask blueprint plus browser assets | [`frontend/app/__init__.py`](../../../../frontend/app/__init__.py) |
| Backend | Own identity and proxy play operations | HTTP API | [`backend/app/api/v1/__init__.py`](../../../../backend/app/api/v1/__init__.py) |
| World Engine | Stream authoritative session updates | Ticketed WebSocket/HTTP via backend | [`world-engine/app/api/story_ws.py`](../../../../world-engine/app/api/story_ws.py) |

## Modeled relationships

| From | To | Semantics | Contract | Source |
| --- | --- | --- | --- | --- |
| Player | Frontend | uses | browser session | [`frontend/app/routes.py`](../../../../frontend/app/routes.py) |
| Frontend | Backend | requests platform and play services | authenticated HTTP | [`frontend/app/api_client.py`](../../../../frontend/app/api_client.py) |
| Backend | World Engine | delegates live operations | signed story request | [`backend/app/services/game/game_service.py`](../../../../backend/app/services/game/game_service.py) |

Generated deterministically from Better Tomorrow's semantic model catalog; edit the catalog, not this projection.
