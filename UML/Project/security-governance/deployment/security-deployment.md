# Security Governance - Deployment

**Viewpoint:** `deployment`
**Concern:** Browser trust boundary, backend secret authority, encrypted store and provider call

[PlantUML source](security-deployment.puml)

## Modeled elements

| Element | Responsibility | Contract | Source |
| --- | --- | --- | --- |
| Browser | Hold protected user session | Secure cookie and CSRF | [`frontend/app/auth.py`](../../../../frontend/app/auth.py) |
| Backend Security Boundary | Authorize and manage encrypted secrets | Private application process | [`backend/Dockerfile`](../../../../backend/Dockerfile) |
| Encrypted Governance Store | Persist ciphertext and audit events | Encryption at rest | [`backend/app/extensions.py`](../../../../backend/app/extensions.py) |
| External Model Provider | Accept authenticated inference call | TLS and scoped provider key | [`backend/app/services/governance/governance_runtime/03_provider_contracts_remote_and_mock.py`](../../../../backend/app/services/governance/governance_runtime/03_provider_contracts_remote_and_mock.py) |

## Modeled relationships

| From | To | Semantics | Contract | Source |
| --- | --- | --- | --- | --- |
| Browser | Backend Security Boundary | HTTPS | secure session and CSRF | catalog contract |
| Backend Security Boundary | Encrypted Governance Store | encrypted persistence | ciphertext and audit | [`backend/app/extensions.py`](../../../../backend/app/extensions.py) |
| Backend Security Boundary | External Model Provider | TLS inference call | ephemeral scoped secret | [`backend/app/services/governance/governance_runtime/05_provider_probe_http.py`](../../../../backend/app/services/governance/governance_runtime/05_provider_probe_http.py) |

Generated deterministically from Better Tomorrow's semantic model catalog; edit the catalog, not this projection.
