# Security Governance - Context

**Viewpoint:** `context`
**Concern:** Player and operator trust relationships with backend security authority

[PlantUML source](security-context.puml)

## Modeled elements

| Element | Responsibility | Contract | Source |
| --- | --- | --- | --- |
| Player | Authenticate and access owned sessions | Least-privilege user session | [`frontend/app/auth.py`](../../../../frontend/app/auth.py) |
| Operator | Manage providers, policies and security settings | Privileged authenticated action | [`administration-tool/app.py`](../../../../administration-tool/app.py) |
| Security Governance | Authorize, protect and audit sensitive operations | Backend-owned policy boundary | [`backend/app/services/governance/security_governance_service.py`](../../../../backend/app/services/governance/security_governance_service.py) |

## Modeled relationships

| From | To | Semantics | Contract | Source |
| --- | --- | --- | --- | --- |
| Player | Security Governance | authenticates | user session | catalog contract |
| Operator | Security Governance | requests privileged mutation | role and CSRF checks | catalog contract |

Generated deterministically from Better Tomorrow's semantic model catalog; edit the catalog, not this projection.
