# Architecture decision records (ADR)

This directory is the **canonical ADR collection** for architecture decisions that affect multiple services or long-lived boundaries. **Program audit** and **task closure** evidence remain under `docs/audit/` and are not ADRs.

## Index

| ADR | Title | Status |
|-----|--------|--------|
| [ADR-0001](adr-0001-runtime-authority-in-world-engine.md) | Runtime authority in world-engine | Accepted |
| [ADR-0002](adr-0002-backend-session-surface-quarantine.md) | Backend session surface quarantine and authority labeling | Accepted |
| [ADR-0003](adr-0003-scene-identity-canonical-surface.md) | Single canonical scene identity surface across AI guidance and runtime commit | Accepted |

## When to write an ADR

- Changing **ownership** of session lifecycle, persistence, or turn commit authority.
- Introducing a **second** runtime graph or duplicate content authority without removing the first.
- materially changing **security boundaries** between admin, player, MCP, and internal APIs.

## Template

Use [adr-template.md](adr-template.md) for new decisions.

Legacy note: `docs/governance/` remains only as a compatibility location during migration. New governance attachment and normative indexing should point to `docs/ADR/`.

## Related

- [Architecture overview](../architecture/README.md)
- [Normative contracts index](../dev/contracts/normative-contracts-index.md)
