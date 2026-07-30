# Better Tomorrow - Canonical Turn

**Viewpoint:** `sequence`
**Concern:** Whole-system player turn across all authority boundaries

[PlantUML source](canonical-turn-sequence.puml)

## Modeled elements

| Element | Responsibility | Contract | Source |
| --- | --- | --- | --- |
| Player | Experience and influence a live dramatic scene | Authenticated semantic interaction | [`frontend/templates/session_shell.html`](../../../../frontend/templates/session_shell.html) |
| Frontend | Present player interaction and transient UI state | Browser shell | [`frontend/app/__init__.py`](../../../../frontend/app/__init__.py) |
| Backend | Own identity, community and control-plane truth | Flask API | [`backend/app/factory_app.py`](../../../../backend/app/factory_app.py) |
| World Engine | Own live sessions and commit story truth | Story HTTP/WebSocket API | [`world-engine/app/main.py`](../../../../world-engine/app/main.py) |
| Content Authority | Own authored experience facts and policy | Versioned YAML modules | [`content/modules/god_of_carnage/module.yaml`](../../../../content/modules/god_of_carnage/module.yaml) |
| AI Stack | Propose dramatically informed outcomes | Proposal-only runtime | [`ai_stack/langgraph/langgraph_runtime_executor.py`](../../../../ai_stack/langgraph/langgraph_runtime_executor.py) |

## Modeled relationships

| From | To | Semantics | Contract | Source |
| --- | --- | --- | --- | --- |
| Player | Frontend | interacts | browser session | [`frontend/app/routes_play.py`](../../../../frontend/app/routes_play.py) |
| Frontend | Backend | authenticates and launches | HTTP API | [`frontend/app/api_client.py`](../../../../frontend/app/api_client.py) |
| Backend | World Engine | delegates live turn | signed proxy request | [`backend/app/services/game/game_service.py`](../../../../backend/app/services/game/game_service.py) |
| Content Authority | World Engine | binds authored truth | content version | [`world-engine/app/content/backend_loader.py`](../../../../world-engine/app/content/backend_loader.py) |
| World Engine | AI Stack | requests proposal | bounded context | [`world-engine/app/story_runtime/governed_runtime_adapters.py`](../../../../world-engine/app/story_runtime/governed_runtime_adapters.py) |
| World Engine | Frontend | streams committed blocks | post-commit events | [`world-engine/app/api/story_ws.py`](../../../../world-engine/app/api/story_ws.py) |

Generated deterministically from Better Tomorrow's semantic model catalog; edit the catalog, not this projection.
