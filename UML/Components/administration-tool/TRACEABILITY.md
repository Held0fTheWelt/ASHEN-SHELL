# Administration Tool UML traceability

| View | Kind | Decisions | Source anchors |
| --- | --- | --- | --- |
| [Administration Tool — System Context](components/c4-context.md) | `context` | D2 | `administration-tool/app.py`, `administration-tool/route_registration_manage_sections.py`, `administration-tool/route_registration_proxy.py`, `backend/app/api/v1/security_governance_routes.py`, `docs/architecture/components/administration-tool/architecture.md` |
| [Administration Tool — Internal Components](components/c4-component.md) | `component` | D1, D2 | `administration-tool/app.py`, `administration-tool/route_registration.py`, `administration-tool/route_registration_manage.py`, `administration-tool/route_registration_manage_sections.py`, `administration-tool/route_registration_pages.py`, `administration-tool/route_registration_proxy.py`, `administration-tool/route_registration_proxy_policy.py`, `administration-tool/route_registration_security.py`, `administration-tool/templates/manage/dashboard.html`, `backend/app/api/v1/security_governance_routes.py` |
| [Administration Tool — Governed Mutation](sequence/governed-mutation-sequence.md) | `sequence` | D2 | `administration-tool/app.py`, `administration-tool/route_registration_manage.py`, `administration-tool/route_registration_manage_sections.py`, `administration-tool/route_registration_proxy.py`, `administration-tool/route_registration_proxy_policy.py`, `administration-tool/route_registration_security.py`, `backend/app/api/v1/security_governance_routes.py`, `docs/architecture/components/administration-tool/architecture.md` |
| [Administration Tool — Deployment](deployment/administration-tool-deployment.md) | `deployment` | D2 | `administration-tool/Dockerfile`, `administration-tool/templates/manage/dashboard.html`, `backend/Dockerfile`, `docs/architecture/components/administration-tool/architecture.md` |

The table is a generated correspondence view. Source paths are validated before projection.
