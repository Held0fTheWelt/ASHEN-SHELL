# Better Tomorrow - System Context

**Viewpoint:** `context`
**Concern:** Players, operators and bounded systems with explicit authority

[PlantUML source](system-context.puml)

## Modeled elements

| Element | Responsibility | Contract | Source |
| --- | --- | --- | --- |
| Player | Experience and influence a live dramatic scene | Authenticated semantic interaction | [`frontend/templates/session_shell.html`](../../../../frontend/templates/session_shell.html) |
| Operator | Inspect and govern the platform | Privileged audited operation | [`administration-tool/app.py`](../../../../administration-tool/app.py) |
| Frontend | Present player interaction and transient UI state | Browser shell | [`frontend/app/__init__.py`](../../../../frontend/app/__init__.py) |
| Backend | Own identity, community and control-plane truth | Flask API | [`backend/app/factory_app.py`](../../../../backend/app/factory_app.py) |
| World Engine | Own live sessions and commit story truth | Story HTTP/WebSocket API | [`world-engine/world_engine/main.py`](../../../../world-engine/world_engine/main.py) |
| AI Stack | Propose dramatically informed outcomes | Proposal-only runtime | [`ai_stack/langgraph/langgraph_runtime_executor.py`](../../../../ai_stack/langgraph/langgraph_runtime_executor.py) |
| Content Authority | Own authored experience facts and policy | Versioned YAML modules | [`content/modules/god_of_carnage/module.yaml`](../../../../content/modules/god_of_carnage/module.yaml) |
| Administration Tool | Present governed operator workflows | Backend-delegated mutations | [`administration-tool/app.py`](../../../../administration-tool/app.py) |
| MCP Server | Expose bounded local automation capabilities | JSON-RPC adapter | [`tools/mcp_server/server.py`](../../../../tools/mcp_server/server.py) |

## Modeled relationships

| From | To | Semantics | Contract | Source |
| --- | --- | --- | --- | --- |
| Player | Frontend | interacts | browser session | [`frontend/app/routes_play.py`](../../../../frontend/app/routes_play.py) |
| Frontend | Backend | authenticates and launches | HTTP API | [`frontend/app/api_client.py`](../../../../frontend/app/api_client.py) |
| Backend | World Engine | delegates live turn | signed proxy request | [`backend/app/services/game/game_service.py`](../../../../backend/app/services/game/game_service.py) |
| Content Authority | World Engine | binds authored truth | content version | [`world-engine/world_engine/content/backend_loader.py`](../../../../world-engine/world_engine/content/backend_loader.py) |
| World Engine | AI Stack | requests proposal | bounded context | [`world-engine/world_engine/story_runtime/governed_runtime_adapters.py`](../../../../world-engine/world_engine/story_runtime/governed_runtime_adapters.py) |
| World Engine | Frontend | streams committed blocks | post-commit events | [`world-engine/world_engine/api/story_ws.py`](../../../../world-engine/world_engine/api/story_ws.py) |
| Operator | Administration Tool | operates | privileged browser workflow | [`administration-tool/app.py`](../../../../administration-tool/app.py) |
| Administration Tool | Backend | delegates governance | audited backend mutation | [`backend/app/services/governance/governance_runtime_service.py`](../../../../backend/app/services/governance/governance_runtime_service.py) |
| MCP Server | Backend | delegates tools | governed API | [`tools/mcp_server/backend_client.py`](../../../../tools/mcp_server/backend_client.py) |

Generated deterministically from Better Tomorrow's semantic model catalog; edit the catalog, not this projection.
