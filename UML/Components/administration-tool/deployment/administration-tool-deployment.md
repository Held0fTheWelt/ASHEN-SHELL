# Administration Tool — Deployment

**Viewpoint:** `deployment`
**Concern:** Browser, administration process and backend trust boundary

[PlantUML source](administration-tool-deployment.puml)

## Modeled elements

| Element | Responsibility | Contract | Source |
| --- | --- | --- | --- |
| Operator | Inspect health and request governed changes | Authenticated browser session with explicit confirmation | [`docs/architecture/components/administration-tool/architecture.md`](../../../../docs/architecture/components/administration-tool/architecture.md) |
| Browser | Host the operator session | HTTPS, cookies and CSRF token | [`administration-tool/templates/manage/dashboard.html`](../../../../administration-tool/templates/manage/dashboard.html) |
| Administration Flask Process | Serve pages and proxy requests | Port 5002 in local Compose | [`administration-tool/Dockerfile`](../../../../administration-tool/Dockerfile) |
| Backend Flask Process | Provide authoritative control-plane APIs | Internal HTTP service | [`backend/Dockerfile`](../../../../backend/Dockerfile) |

## Modeled relationships

| From | To | Semantics | Contract | Source |
| --- | --- | --- | --- | --- |
| Operator | Browser | uses | browser session | catalog contract |
| Browser | Administration Flask Process | HTTPS | public administration endpoint | catalog contract |
| Administration Flask Process | Backend Flask Process | internal HTTP | BACKEND_URL and service credentials | catalog contract |

Generated deterministically from Better Tomorrow's semantic model catalog; edit the catalog, not this projection.
