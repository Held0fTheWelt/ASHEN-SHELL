# ADR-0028: MCP Security Baseline — Phase A minimal policy

## Status
Proposed

## Date
2026-04-17

## Intellectual property rights
Repository authorship and licensing: see project LICENSE; contact maintainers for clarification.

## Privacy and confidentiality
This ADR contains no personal data. Implementers must follow the repository privacy and confidentiality policies, avoid committing secrets, and document any sensitive data handling in implementation steps.

## Context
Phase A for MCP requires conservative security defaults to prevent accidental state changes and exposure of secrets during operator workflows.

## Decision
- Restrict MCP to read/preview-only behavior in Phase A; `write` operations are forbidden.
- Use `Authorization: Bearer <SERVICE_TOKEN>` for backend calls; tokens stored securely and not committed to repo.
- Rate limit MCP locally to max 30 calls/min per token.
- Logs must not contain PII or secrets; request bodies should be hashed when stored.

## Consequences
- Tooling and endpoints must respect permission levels and logging constraints.
- Future phases may relax or change these rules with an ADR.

## Testing


## References
(Automated migration entry created 2026-04-17)
