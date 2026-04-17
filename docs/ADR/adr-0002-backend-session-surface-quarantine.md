# ADR-0002: Backend session / transitional runtime surface - quarantine and retirement

## Status
Accepted

## Date
2026-04-17

## Intellectual property rights
Repository authorship and licensing: see project LICENSE; contact maintainers for clarification.

## Privacy and confidentiality
This ADR contains no personal data. Implementers must follow the repository privacy and confidentiality policies, avoid committing secrets, and document any sensitive data handling in implementation steps.

## Context
The platform historically exposed backend-local session and runtime-shaped APIs. The world-engine is the **authoritative** live and story runtime for committed play state. A large transitional surface on the backend increases the risk that tools, tests, or new features attach to the wrong authority layer (audit finding class "backend transitional session drift").

## Decision
1. **Inventory** all backend routes and services under `backend/app/runtime/`, `session_service.py`, `session_start.py`, and session-related API modules (normative list: **Appendix A**).
2. **Classify** each entry point as: **retire** (remove when no caller), **quarantine** (explicit non-authoritative labeling, narrow compatibility window), or **compat** (documented operator-only surface with no player truth claims).
3. **Quarantine** non-authoritative surfaces in naming and documentation so they cannot be mistaken for production authority (prefixes, deprecation notices, ADR links).

## Consequences
- Positive: Reduced drift; clearer onboarding for engineers.
- Negative: Migration work for any remaining callers of retired surfaces; coordination with product for compat timelines.

## Testing


## References
