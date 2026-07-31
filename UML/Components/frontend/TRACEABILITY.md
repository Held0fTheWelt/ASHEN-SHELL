# Frontend UML traceability

| View | Kind | Decisions | Source anchors |
| --- | --- | --- | --- |
| [Frontend - System Context](context/frontend-context.md) | `context` | D1 | `backend/app/api/v1/__init__.py`, `backend/app/services/game/game_service.py`, `frontend/app/__init__.py`, `frontend/app/api_client.py`, `frontend/app/routes.py`, `frontend/templates/session_shell.html`, `world-engine/world_engine/api/story_ws.py` |
| [Frontend - Browser and Route Components](components/frontend-components.md) | `component` | D1, D2 | `frontend/app/api_client.py`, `frontend/app/routes.py`, `frontend/app/routes_play.py`, `frontend/static/play_block_renderer.js`, `frontend/static/play_controls.js`, `frontend/static/play_narrative_stream.js`, `frontend/static/play_runtime_bootstrap.js` |
| [Frontend - Player Turn](sequence/player-turn-sequence.md) | `sequence` | D1 | `frontend/app/api_client.py`, `frontend/app/routes_play.py`, `frontend/static/play_block_renderer.js`, `frontend/static/play_controls.js`, `frontend/static/play_narrative_stream.js`, `frontend/static/play_runtime_bootstrap.js`, `frontend/templates/session_shell.html` |
| [Frontend - Shell Lifecycle](states/shell-lifecycle.md) | `state` | D2, D3 | `frontend/static/play_live_ws.js`, `frontend/static/play_runtime_bootstrap.js`, `frontend/static/play_session_start.js`, `frontend/static/play_shell.js` |
| [Frontend - Deployment](deployment/frontend-deployment.md) | `deployment` | D1 | `backend/Dockerfile`, `frontend/Dockerfile`, `frontend/app/api_client.py`, `frontend/run.py` |

The table is a generated correspondence view. Source paths are validated before projection.
