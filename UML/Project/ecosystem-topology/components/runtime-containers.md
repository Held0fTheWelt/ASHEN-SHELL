# Better Tomorrow - Canonical Runtime Containers

**Viewpoint:** `container`
**Concern:** Identity, proxy, authored truth, live commit and proposal runtime boundaries

[PlantUML source](runtime-containers.puml)

## Modeled elements

| Element | Responsibility | Contract | Source |
| --- | --- | --- | --- |
| Identity and Platform | Authenticate users and serve platform data | Backend ownership | [`backend/app/api/v1/auth_routes.py`](../../../../backend/app/api/v1/auth_routes.py) |
| Play Proxy | Bridge player requests to live authority | No local story commit | [`backend/app/services/game/game_service.py`](../../../../backend/app/services/game/game_service.py) |
| Authored Truth | Supply experience identity and policy | Immutable bound module version | [`content/modules/god_of_carnage/module.yaml`](../../../../content/modules/god_of_carnage/module.yaml) |
| Live Runtime | Coordinate and commit canonical turns | World-engine ownership | [`world-engine/app/story_runtime/manager/runtime_manager.py`](../../../../world-engine/app/story_runtime/manager/runtime_manager.py) |
| Proposal Runtime | Interpret, retrieve, plan, realize and validate candidates | AI proposal only | [`ai_stack/langgraph/langgraph_runtime_executor.py`](../../../../ai_stack/langgraph/langgraph_runtime_executor.py) |

## Modeled relationships

| From | To | Semantics | Contract | Source |
| --- | --- | --- | --- | --- |
| Identity and Platform | Play Proxy | authorizes launch | player and run binding | [`backend/app/api/v1/game/player_turn_execution_and_flush.py`](../../../../backend/app/api/v1/game/player_turn_execution_and_flush.py) |
| Play Proxy | Live Runtime | forwards command | signed ticket | [`backend/app/services/game/game_service.py`](../../../../backend/app/services/game/game_service.py) |
| Authored Truth | Live Runtime | bounds session | immutable module version | [`world-engine/app/content/backend_loader.py`](../../../../world-engine/app/content/backend_loader.py) |
| Live Runtime | Proposal Runtime | requests candidate | proposal-only call | [`world-engine/app/story_runtime/governed_runtime_adapters.py`](../../../../world-engine/app/story_runtime/governed_runtime_adapters.py) |
| Proposal Runtime | Live Runtime | returns candidate | validation evidence and no commit | [`world-engine/app/story_runtime/narrative_commit_resolution.py`](../../../../world-engine/app/story_runtime/narrative_commit_resolution.py) |

Generated deterministically from Better Tomorrow's semantic model catalog; edit the catalog, not this projection.
