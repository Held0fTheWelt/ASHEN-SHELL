# Architecture decision records (ADR)

This directory holds **lightweight ADRs** for decisions that affect multiple services or long-lived boundaries. **Program audit** and **task closure** evidence remain under `docs/audit/` and `docs/governance/audit_resolution/`; they are not ADRs.

## Index

| ADR | Title | Status |
|-----|--------|--------|
| [ADR-0001](adr-0001-runtime-authority-in-world-engine.md) | Runtime authority in world-engine | Accepted |
| [ADR-0002](adr-0002-backend-session-surface-quarantine.md) | Backend session / transitional runtime quarantine | Accepted |
| [ADR-0003](adr-0003-scene-identity-canonical-surface.md) | Canonical scene identity across compile, AI, commit | Accepted |

## When to write an ADR

- Changing **ownership** of session lifecycle, persistence, or turn commit authority.
- Introducing a **second** runtime graph or duplicate content authority without removing the first.
- materially changing **security boundaries** between admin, player, MCP, and internal APIs.

## Template

Use [adr-template.md](adr-template.md) for new decisions.

## Related

- [Architecture overview](../architecture/README.md)
- [Normative contracts index](../dev/contracts/normative-contracts-index.md)
- [Audit resolution (master prompt, case input, living state)](../governance/audit_resolution/README.md) - not ADRs; closure governance for audit programs
