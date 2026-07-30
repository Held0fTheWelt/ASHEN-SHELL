# Administration Tool — Internal Components

**Viewpoint:** `component`
**Concern:** How routes, policy, security and templates collaborate without owning domain state

[PlantUML source](c4-component.puml)

## Modeled elements

| Element | Responsibility | Contract | Source |
| --- | --- | --- | --- |
| Administration Tool | Render operator workbenches and translate intent into backend requests | Flask routes; no direct domain persistence | [`administration-tool/app.py`](../../../../administration-tool/app.py) |
| Page Routes | Route public and manage page requests to bounded templates | GET-only page composition | [`administration-tool/route_registration_pages.py`](../../../../administration-tool/route_registration_pages.py) |
| Manage Route Catalog | Expose named operator workbench surfaces | Stable /manage route vocabulary | [`administration-tool/route_registration_manage_sections.py`](../../../../administration-tool/route_registration_manage_sections.py) |
| Manage Templates | Present backend-derived read models and mutation forms | Escaped HTML and explicit form intent | [`administration-tool/templates/manage/dashboard.html`](../../../../administration-tool/templates/manage/dashboard.html) |
| Security Routes | Apply session and operator security checks | Authenticated, CSRF-aware browser mutation boundary | [`administration-tool/route_registration_security.py`](../../../../administration-tool/route_registration_security.py) |
| Backend Proxy | Forward allow-listed reads and mutations to backend | Method, path, timeout and response policy | [`administration-tool/route_registration_proxy.py`](../../../../administration-tool/route_registration_proxy.py) |
| Proxy Policy | Classify mutation endpoints and confirmation requirements | Default-deny unsafe or undeclared proxy operations | [`administration-tool/route_registration_proxy_policy.py`](../../../../administration-tool/route_registration_proxy_policy.py) |
| Backend Admin API | Authorize and execute governed mutations | HTTP /api/v1/admin and operator endpoints | [`backend/app/api/v1/security_governance_routes.py`](../../../../backend/app/api/v1/security_governance_routes.py) |

## Modeled relationships

| From | To | Semantics | Contract | Source |
| --- | --- | --- | --- | --- |
| Administration Tool | Page Routes | dispatches public pages | page route registration | [`administration-tool/route_registration.py`](../../../../administration-tool/route_registration.py) |
| Administration Tool | Manage Route Catalog | dispatches manage pages | named manage route registration | [`administration-tool/route_registration_manage.py`](../../../../administration-tool/route_registration_manage.py) |
| Manage Route Catalog | Manage Templates | renders workbench | template plus backend read model | [`administration-tool/route_registration_manage_sections.py`](../../../../administration-tool/route_registration_manage_sections.py) |
| Manage Route Catalog | Security Routes | requires operator session | authorization before rendering or mutation | [`administration-tool/route_registration_security.py`](../../../../administration-tool/route_registration_security.py) |
| Manage Route Catalog | Backend Proxy | submits requested operation | normalized proxy request | [`administration-tool/route_registration_proxy.py`](../../../../administration-tool/route_registration_proxy.py) |
| Backend Proxy | Proxy Policy | classifies request | default-deny mutation policy | [`administration-tool/route_registration_proxy_policy.py`](../../../../administration-tool/route_registration_proxy_policy.py) |
| Proxy Policy | Backend Admin API | forwards approved operation | service key and operator evidence | [`administration-tool/route_registration_proxy.py`](../../../../administration-tool/route_registration_proxy.py) |

Generated deterministically from Better Tomorrow's semantic model catalog; edit the catalog, not this projection.
