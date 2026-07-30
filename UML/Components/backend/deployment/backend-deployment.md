# Backend — Deployment

**Viewpoint:** `deployment`
**Concern:** Backend process, persistence, shared governance store and world-engine boundary

[PlantUML source](backend-deployment.puml)

## Modeled elements

| Element | Responsibility | Contract | Source |
| --- | --- | --- | --- |
| Browser Clients | Host player and operator sessions | HTTPS | [`frontend/app/routes.py`](../../../../frontend/app/routes.py) |
| Backend Process | Serve Flask API and platform pages | Port 5000 | [`backend/Dockerfile`](../../../../backend/Dockerfile) |
| Backend Database | Persist platform and governance truth | SQLAlchemy/Alembic | [`backend/app/extensions.py`](../../../../backend/app/extensions.py) |
| Redis | Share governed runtime configuration and rate-limit state | Explicit bootstrap and health policy | [`docker-compose.yml`](../../../../docker-compose.yml) |
| World Engine Process | Execute authoritative play | Internal HTTP | [`world-engine/Dockerfile`](../../../../world-engine/Dockerfile) |

## Modeled relationships

| From | To | Semantics | Contract | Source |
| --- | --- | --- | --- | --- |
| Browser Clients | Backend Process | HTTPS | public API boundary | catalog contract |
| Backend Process | Backend Database | SQL | transactional persistence | [`backend/app/extensions.py`](../../../../backend/app/extensions.py) |
| Backend Process | Redis | runtime governance | shared configured state | [`backend/app/services/governance/runtime_config_truth_service.py`](../../../../backend/app/services/governance/runtime_config_truth_service.py) |
| Backend Process | World Engine Process | internal HTTP | play proxy boundary | [`backend/app/services/game/game_service.py`](../../../../backend/app/services/game/game_service.py) |

Generated deterministically from Better Tomorrow's semantic model catalog; edit the catalog, not this projection.
