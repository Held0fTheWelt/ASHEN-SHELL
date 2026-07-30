# Security Governance - Credential Mutation

**Viewpoint:** `sequence`
**Concern:** Privileged intent becomes encrypted state and redacted audit

[PlantUML source](credential-mutation.puml)

## Modeled elements

| Element | Responsibility | Contract | Source |
| --- | --- | --- | --- |
| Operator | Manage providers, policies and security settings | Privileged authenticated action | [`administration-tool/app.py`](../../../../administration-tool/app.py) |
| Security Governance | Authorize, protect and audit sensitive operations | Backend-owned policy boundary | [`backend/app/services/governance/security_governance_service.py`](../../../../backend/app/services/governance/security_governance_service.py) |
| Frontend Auth | Maintain browser session and CSRF policy | No credential authority | [`frontend/app/auth.py`](../../../../frontend/app/auth.py) |
| Security Governance API | Authenticate and authorize privileged requests | Role and CSRF guarded endpoints | [`backend/app/api/v1/security_governance_routes.py`](../../../../backend/app/api/v1/security_governance_routes.py) |
| Security Governance Service | Validate policy and credential operations | Fail-closed domain service | [`backend/app/services/governance/security_governance_service.py`](../../../../backend/app/services/governance/security_governance_service.py) |
| Provider Credential Service | Seal, rotate and resolve provider secrets | No plaintext persistence or response | [`backend/app/services/governance/governance_runtime/11_provider_update_and_credentials.py`](../../../../backend/app/services/governance/governance_runtime/11_provider_update_and_credentials.py) |
| Security Audit | Record privileged action without secret content | Actor, scope and outcome | [`backend/app/services/governance/observability_governance_service.py`](../../../../backend/app/services/governance/observability_governance_service.py) |

## Modeled relationships

| From | To | Semantics | Contract | Source |
| --- | --- | --- | --- | --- |
| Operator | Security Governance | requests privileged mutation | role and CSRF checks | catalog contract |
| Frontend Auth | Security Governance API | submits authenticated intent | session, CSRF and role | [`frontend/app/auth.py`](../../../../frontend/app/auth.py) |
| Security Governance API | Security Governance Service | delegates authorized operation | validated request | [`backend/app/api/v1/security_governance_routes.py`](../../../../backend/app/api/v1/security_governance_routes.py) |
| Security Governance Service | Provider Credential Service | seals or rotates credential | plaintext ephemeral only | [`backend/app/services/governance/governance_runtime/11_provider_update_and_credentials.py`](../../../../backend/app/services/governance/governance_runtime/11_provider_update_and_credentials.py) |
| Security Governance Service | Security Audit | records outcome | redacted security event | [`backend/app/services/governance/observability_governance_service.py`](../../../../backend/app/services/governance/observability_governance_service.py) |

Generated deterministically from Better Tomorrow's semantic model catalog; edit the catalog, not this projection.
