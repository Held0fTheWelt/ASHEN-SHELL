# Administration Tool — System Context

**Viewpoint:** `context`
**Concern:** Who operates the tool and where mutation authority resides

[PlantUML source](c4-context.puml)

## Modeled elements

| Element | Responsibility | Contract | Source |
| --- | --- | --- | --- |
| Operator | Inspect health and request governed changes | Authenticated browser session with explicit confirmation | [`docs/architecture/components/administration-tool/architecture.md`](../../../../docs/architecture/components/administration-tool/architecture.md) |
| Administration Tool | Render operator workbenches and translate intent into backend requests | Flask routes; no direct domain persistence | [`administration-tool/app.py`](../../../../administration-tool/app.py) |
| Backend Admin API | Authorize and execute governed mutations | HTTP /api/v1/admin and operator endpoints | [`backend/app/api/v1/security_governance_routes.py`](../../../../backend/app/api/v1/security_governance_routes.py) |

## Modeled relationships

| From | To | Semantics | Contract | Source |
| --- | --- | --- | --- | --- |
| Operator | Administration Tool | opens workbench | authenticated browser navigation | [`administration-tool/route_registration_manage_sections.py`](../../../../administration-tool/route_registration_manage_sections.py) |
| Administration Tool | Backend Admin API | queries and requests mutation | allow-listed backend API | [`administration-tool/route_registration_proxy.py`](../../../../administration-tool/route_registration_proxy.py) |

Generated deterministically from Better Tomorrow's semantic model catalog; edit the catalog, not this projection.
