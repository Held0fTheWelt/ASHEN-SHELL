# Security Governance - Data Model

**Viewpoint:** `class`
**Concern:** Authorization grant, encrypted secret and redacted audit event

[PlantUML source](security-data-model.puml)

## Modeled elements

| Element | Responsibility | Contract | Source |
| --- | --- | --- | --- |
| Authorization Grant | Bind actor, scope and allowed operation | Least privilege and expiry | [`backend/app/services/governance/security_governance_service.py`](../../../../backend/app/services/governance/security_governance_service.py) |
| Provider Secret | Represent encrypted provider credential material | Ciphertext at rest | [`backend/app/services/governance/governance_runtime_service_impl.py`](../../../../backend/app/services/governance/governance_runtime_service_impl.py) |
| Security Audit Event | Record safe mutation evidence | No secret payload | [`backend/app/services/governance/observability_governance_service.py`](../../../../backend/app/services/governance/observability_governance_service.py) |

## Modeled relationships

| From | To | Semantics | Contract | Source |
| --- | --- | --- | --- | --- |
| Authorization Grant | Provider Secret | permits scoped resolution | least privilege | [`backend/app/services/governance/security_governance_service.py`](../../../../backend/app/services/governance/security_governance_service.py) |
| Provider Secret | Security Audit Event | changes emit | no plaintext | [`backend/app/services/governance/observability_governance_service.py`](../../../../backend/app/services/governance/observability_governance_service.py) |

Generated deterministically from Better Tomorrow's semantic model catalog; edit the catalog, not this projection.
