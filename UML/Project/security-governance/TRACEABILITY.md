# Security Governance UML traceability

| View | Kind | Decisions | Source anchors |
| --- | --- | --- | --- |
| [Security Governance - Context](context/security-context.md) | `context` | D1 | `administration-tool/app.py`, `backend/app/services/governance/security_governance_service.py`, `frontend/app/auth.py` |
| [Security Governance - Trust Components](components/trust-components.md) | `component` | D1, D2 | `backend/app/api/v1/security_governance_routes.py`, `backend/app/services/governance/governance_runtime_service_impl.py`, `backend/app/services/governance/observability_governance_service.py`, `backend/app/services/governance/security_governance_service.py`, `frontend/app/auth.py`, `tools/mcp_server/backend_client.py`, `tools/mcp_server/server.py` |
| [Security Governance - Credential Mutation](sequence/credential-mutation.md) | `sequence` | D1, D2 | `administration-tool/app.py`, `backend/app/api/v1/security_governance_routes.py`, `backend/app/services/governance/governance_runtime_service_impl.py`, `backend/app/services/governance/observability_governance_service.py`, `backend/app/services/governance/security_governance_service.py`, `frontend/app/auth.py` |
| [Security Governance - Data Model](classes/security-data-model.md) | `class` | D2 | `backend/app/services/governance/governance_runtime_service_impl.py`, `backend/app/services/governance/observability_governance_service.py`, `backend/app/services/governance/security_governance_service.py` |
| [Security Governance - Credential Lifecycle](states/credential-lifecycle.md) | `state` | D3 | `backend/app/services/governance/governance_runtime_service_impl.py` |
| [Security Governance - Deployment](deployment/security-deployment.md) | `deployment` | D1, D3 | `backend/Dockerfile`, `backend/app/extensions.py`, `backend/app/services/governance/governance_runtime_service_impl.py`, `frontend/app/auth.py` |

The table is a generated correspondence view. Source paths are validated before projection.
