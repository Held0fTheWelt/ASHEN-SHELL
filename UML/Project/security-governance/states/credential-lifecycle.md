# Security Governance - Credential Lifecycle

**Viewpoint:** `state`
**Concern:** Absent, sealed, active, rotating and revoked provider credentials

[PlantUML source](credential-lifecycle.puml)

## Modeled elements

| Element | Responsibility | Contract | Source |
| --- | --- | --- | --- |
| Absent | Represent unconfigured provider credential | Runtime not ready | [`backend/app/services/governance/governance_runtime/10_provider_listing_and_create.py`](../../../../backend/app/services/governance/governance_runtime/10_provider_listing_and_create.py) |
| Sealed | Store encrypted credential | Ciphertext only | [`backend/app/services/governance/governance_runtime/04_provider_secret_and_model_helpers.py`](../../../../backend/app/services/governance/governance_runtime/04_provider_secret_and_model_helpers.py) |
| Active | Permit scoped provider use | Health and policy valid | [`backend/app/services/governance/governance_runtime/12_provider_connection_health.py`](../../../../backend/app/services/governance/governance_runtime/12_provider_connection_health.py) |
| Rotating | Replace credential without plaintext exposure | Audited atomic replacement | [`backend/app/services/governance/governance_runtime/11_provider_update_and_credentials.py`](../../../../backend/app/services/governance/governance_runtime/11_provider_update_and_credentials.py) |
| Revoked | Prevent further resolution | Audit retained | [`backend/app/services/governance/governance_runtime/14_model_update_delete_rebind.py`](../../../../backend/app/services/governance/governance_runtime/14_model_update_delete_rebind.py) |

## Modeled relationships

| From | To | Semantics | Contract | Source |
| --- | --- | --- | --- | --- |
| Initial | Absent | provider created | no secret | catalog contract |
| Absent | Sealed | credential supplied | encrypt before persistence | [`backend/app/services/governance/governance_runtime/11_provider_update_and_credentials.py`](../../../../backend/app/services/governance/governance_runtime/11_provider_update_and_credentials.py) |
| Sealed | Active | health and policy pass | provider ready | [`backend/app/services/governance/governance_runtime/12_provider_connection_health.py`](../../../../backend/app/services/governance/governance_runtime/12_provider_connection_health.py) |
| Active | Rotating | rotation requested | old secret remains until replacement valid | [`backend/app/services/governance/governance_runtime/11_provider_update_and_credentials.py`](../../../../backend/app/services/governance/governance_runtime/11_provider_update_and_credentials.py) |
| Rotating | Active | replacement committed | audit and key version advance | catalog contract |
| Active | Revoked | provider disabled | resolution denied | [`backend/app/services/governance/governance_runtime/14_model_update_delete_rebind.py`](../../../../backend/app/services/governance/governance_runtime/14_model_update_delete_rebind.py) |

Generated deterministically from Better Tomorrow's semantic model catalog; edit the catalog, not this projection.
