# Administration Tool — Governed Mutation

**Viewpoint:** `sequence`
**Concern:** End-to-end authorization and delegation of an operator mutation

[PlantUML source](governed-mutation-sequence.puml)

## Modeled elements

| Element | Responsibility | Contract | Source |
| --- | --- | --- | --- |
| Operator | Inspect health and request governed changes | Authenticated browser session with explicit confirmation | [`docs/architecture/components/administration-tool/architecture.md`](../../../../docs/architecture/components/administration-tool/architecture.md) |
| Administration Tool | Render operator workbenches and translate intent into backend requests | Flask routes; no direct domain persistence | [`administration-tool/app.py`](../../../../administration-tool/app.py) |
| Manage Route Catalog | Expose named operator workbench surfaces | Stable /manage route vocabulary | [`administration-tool/route_registration_manage_sections.py`](../../../../administration-tool/route_registration_manage_sections.py) |
| Security Routes | Apply session and operator security checks | Authenticated, CSRF-aware browser mutation boundary | [`administration-tool/route_registration_security.py`](../../../../administration-tool/route_registration_security.py) |
| Backend Proxy | Forward allow-listed reads and mutations to backend | Method, path, timeout and response policy | [`administration-tool/route_registration_proxy.py`](../../../../administration-tool/route_registration_proxy.py) |
| Proxy Policy | Classify mutation endpoints and confirmation requirements | Default-deny unsafe or undeclared proxy operations | [`administration-tool/route_registration_proxy_policy.py`](../../../../administration-tool/route_registration_proxy_policy.py) |
| Backend Admin API | Authorize and execute governed mutations | HTTP /api/v1/admin and operator endpoints | [`backend/app/api/v1/security_governance_routes.py`](../../../../backend/app/api/v1/security_governance_routes.py) |

## Modeled relationships

| From | To | Semantics | Contract | Source |
| --- | --- | --- | --- | --- |
| Operator | Administration Tool | opens workbench | authenticated browser navigation | [`administration-tool/route_registration_manage_sections.py`](../../../../administration-tool/route_registration_manage_sections.py) |
| Manage Route Catalog | Security Routes | requires operator session | authorization before rendering or mutation | [`administration-tool/route_registration_security.py`](../../../../administration-tool/route_registration_security.py) |
| Manage Route Catalog | Backend Proxy | submits requested operation | normalized proxy request | [`administration-tool/route_registration_proxy.py`](../../../../administration-tool/route_registration_proxy.py) |
| Backend Proxy | Proxy Policy | classifies request | default-deny mutation policy | [`administration-tool/route_registration_proxy_policy.py`](../../../../administration-tool/route_registration_proxy_policy.py) |
| Proxy Policy | Backend Admin API | forwards approved operation | service key and operator evidence | [`administration-tool/route_registration_proxy.py`](../../../../administration-tool/route_registration_proxy.py) |

Generated deterministically from Better Tomorrow's semantic model catalog; edit the catalog, not this projection.
