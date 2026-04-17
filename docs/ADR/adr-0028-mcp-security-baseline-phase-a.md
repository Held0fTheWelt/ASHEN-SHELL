# ADR-0028: MCP Security Baseline — Phase A minimal policy

Date: 2026-04-17

Status: Accepted

## Context

Phase A for MCP requires conservative security defaults to prevent accidental state changes and exposure of secrets during operator workflows.

## Decision

- Restrict MCP to read/preview-only behavior in Phase A; `write` operations are forbidden.
- Use `Authorization: Bearer <SERVICE_TOKEN>` for backend calls; tokens stored securely and not committed to repo.
- Rate limit MCP locally to max 30 calls/min per token.
- Logs must not contain PII or secrets; request bodies should be hashed when stored.

## Rationale

- Minimizes risk during operator-driven debugging and prevents unintended writes.
- Keeps early-stage tooling safe for use with production-like backends.

## Consequences

- Tooling and endpoints must respect permission levels and logging constraints.
- Future phases may relax or change these rules with an ADR.

## Migrated from

`docs/mcp/03_M0_security_baseline.md` (Decision (Phase A))

---

(Automated migration entry created 2026-04-17)
