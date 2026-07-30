# World Engine - System Context

**Viewpoint:** `context`
**Concern:** Live authority among player, backend, content and AI proposal collaborators

[PlantUML source](c4-context.puml)

## Modeled elements

| Element | Responsibility | Contract | Source |
| --- | --- | --- | --- |
| Player | Submit semantic intent and observe committed narrative | Ticket-bound session | [`world-engine/app/api/story_ws.py`](../../../../world-engine/app/api/story_ws.py) |
| Backend | Authenticate and proxy play operations | Signed internal request | [`backend/app/services/game/game_service.py`](../../../../backend/app/services/game/game_service.py) |
| World Engine | Own sessions, validate proposals and commit story truth | HTTP/WebSocket story API | [`world-engine/app/main.py`](../../../../world-engine/app/main.py) |
| AI Stack | Produce bounded narrative proposals | Proposal and evidence, never commit | [`ai_stack/langgraph/langgraph_runtime_executor.py`](../../../../ai_stack/langgraph/langgraph_runtime_executor.py) |
| Content Authority | Supply versioned authored facts and policy | Immutable bound content version | [`content/modules/god_of_carnage/module.yaml`](../../../../content/modules/god_of_carnage/module.yaml) |

## Modeled relationships

| From | To | Semantics | Contract | Source |
| --- | --- | --- | --- | --- |
| Player | Backend | submits intent | authenticated player request | [`backend/app/api/v1/game/player_turn_execution_and_flush.py`](../../../../backend/app/api/v1/game/player_turn_execution_and_flush.py) |
| Backend | World Engine | proxies turn | signed story request | [`backend/app/services/game/game_service.py`](../../../../backend/app/services/game/game_service.py) |
| Content Authority | World Engine | supplies authored truth | bound immutable content version | [`world-engine/app/content/backend_loader.py`](../../../../world-engine/app/content/backend_loader.py) |
| World Engine | AI Stack | requests proposal | bounded context and trace | [`world-engine/app/story_runtime/governed_runtime_adapters.py`](../../../../world-engine/app/story_runtime/governed_runtime_adapters.py) |

Generated deterministically from Better Tomorrow's semantic model catalog; edit the catalog, not this projection.
