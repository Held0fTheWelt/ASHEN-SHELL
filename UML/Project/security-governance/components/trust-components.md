# Security Governance - Trust Components

**Viewpoint:** `component`
**Concern:** Frontend, API, service, credential, runtime-secret, audit and MCP boundaries

[PlantUML source](trust-components.puml)

## Modeled elements

| Element | Responsibility | Contract | Source |
| --- | --- | --- | --- |
| Frontend Auth | Maintain browser session and CSRF policy | No credential authority | [`frontend/app/auth.py`](../../../../frontend/app/auth.py) |
| Security Governance API | Authenticate and authorize privileged requests | Role and CSRF guarded endpoints | [`backend/app/api/v1/security_governance_routes.py`](../../../../backend/app/api/v1/security_governance_routes.py) |
| Security Governance Service | Validate policy and credential operations | Fail-closed domain service | [`backend/app/services/governance/security_governance_service.py`](../../../../backend/app/services/governance/security_governance_service.py) |
| Provider Credential Service | Seal, rotate and resolve provider secrets | No plaintext persistence or response | [`backend/app/services/governance/governance_runtime/11_provider_update_and_credentials.py`](../../../../backend/app/services/governance/governance_runtime/11_provider_update_and_credentials.py) |
| Runtime Secret Resolver | Provide ephemeral secret material to authorized calls | Scoped in-memory use | [`backend/app/services/governance/governance_runtime/28_operational_activity_and_runtime_secret.py`](../../../../backend/app/services/governance/governance_runtime/28_operational_activity_and_runtime_secret.py) |
| Security Audit | Record privileged action without secret content | Actor, scope and outcome | [`backend/app/services/governance/observability_governance_service.py`](../../../../backend/app/services/governance/observability_governance_service.py) |
| MCP Boundary | Validate local tool scope and delegate privileged operations | No direct credential mutation | [`tools/mcp_server/server.py`](../../../../tools/mcp_server/server.py) |

## Modeled relationships

| From | To | Semantics | Contract | Source |
| --- | --- | --- | --- | --- |
| Frontend Auth | Security Governance API | submits authenticated intent | session, CSRF and role | [`frontend/app/auth.py`](../../../../frontend/app/auth.py) |
| Security Governance API | Security Governance Service | delegates authorized operation | validated request | [`backend/app/api/v1/security_governance_routes.py`](../../../../backend/app/api/v1/security_governance_routes.py) |
| Security Governance Service | Provider Credential Service | seals or rotates credential | plaintext ephemeral only | [`backend/app/services/governance/governance_runtime/11_provider_update_and_credentials.py`](../../../../backend/app/services/governance/governance_runtime/11_provider_update_and_credentials.py) |
| Provider Credential Service | Runtime Secret Resolver | resolves for provider call | scoped in-memory secret | [`backend/app/services/governance/governance_runtime/28_operational_activity_and_runtime_secret.py`](../../../../backend/app/services/governance/governance_runtime/28_operational_activity_and_runtime_secret.py) |
| Security Governance Service | Security Audit | records outcome | redacted security event | [`backend/app/services/governance/observability_governance_service.py`](../../../../backend/app/services/governance/observability_governance_service.py) |
| MCP Boundary | Security Governance API | delegates governed operation | same authorization policy | [`tools/mcp_server/backend_client.py`](../../../../tools/mcp_server/backend_client.py) |

Generated deterministically from Better Tomorrow's semantic model catalog; edit the catalog, not this projection.
