# Better Tomorrow - Authority Use Cases

**Viewpoint:** `usecase`
**Concern:** Player experience, operator governance and automated inspection remain separated

[PlantUML source](authority-use-cases.puml)

## Modeled elements

| Element | Responsibility | Contract | Source |
| --- | --- | --- | --- |
| Player | Experience and influence a live dramatic scene | Authenticated semantic interaction | [`frontend/templates/session_shell.html`](../../../../frontend/templates/session_shell.html) |
| Operator | Inspect and govern the platform | Privileged audited operation | [`administration-tool/app.py`](../../../../administration-tool/app.py) |
| Frontend | Present player interaction and transient UI state | Browser shell | [`frontend/app/__init__.py`](../../../../frontend/app/__init__.py) |
| Administration Tool | Present governed operator workflows | Backend-delegated mutations | [`administration-tool/app.py`](../../../../administration-tool/app.py) |
| MCP Server | Expose bounded local automation capabilities | JSON-RPC adapter | [`tools/mcp_server/server.py`](../../../../tools/mcp_server/server.py) |
| World Engine | Own live sessions and commit story truth | Story HTTP/WebSocket API | [`world-engine/world_engine/main.py`](../../../../world-engine/world_engine/main.py) |
| Backend | Own identity, community and control-plane truth | Flask API | [`backend/app/factory_app.py`](../../../../backend/app/factory_app.py) |

## Modeled relationships

| From | To | Semantics | Contract | Source |
| --- | --- | --- | --- | --- |
| Player | Frontend | interacts | browser session | [`frontend/app/routes_play.py`](../../../../frontend/app/routes_play.py) |
| Operator | Administration Tool | operates | privileged browser workflow | [`administration-tool/app.py`](../../../../administration-tool/app.py) |
| MCP Server | Backend | delegates tools | governed API | [`tools/mcp_server/backend_client.py`](../../../../tools/mcp_server/backend_client.py) |
| Backend | World Engine | delegates live turn | signed proxy request | [`backend/app/services/game/game_service.py`](../../../../backend/app/services/game/game_service.py) |

Generated deterministically from Better Tomorrow's semantic model catalog; edit the catalog, not this projection.
