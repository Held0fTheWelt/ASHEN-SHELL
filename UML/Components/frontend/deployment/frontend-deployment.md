# Frontend - Deployment

**Viewpoint:** `deployment`
**Concern:** Browser, frontend process and backend API boundary

[PlantUML source](frontend-deployment.puml)

## Modeled elements

| Element | Responsibility | Contract | Source |
| --- | --- | --- | --- |
| Browser | Execute player shell | HTML/CSS/JavaScript | [`frontend/Dockerfile`](../../../../frontend/Dockerfile) |
| Frontend Process | Serve routes and assets | Flask HTTP | [`frontend/run.py`](../../../../frontend/run.py) |
| Backend Process | Serve identity and play proxy | Internal/public HTTP | [`backend/Dockerfile`](../../../../backend/Dockerfile) |

## Modeled relationships

| From | To | Semantics | Contract | Source |
| --- | --- | --- | --- | --- |
| Browser | Frontend Process | HTTPS | page and asset delivery | catalog contract |
| Frontend Process | Backend Process | HTTP | backend API client | [`frontend/app/api_client.py`](../../../../frontend/app/api_client.py) |

Generated deterministically from Better Tomorrow's semantic model catalog; edit the catalog, not this projection.
