# Authoring a component SAD

Produces `docs/architecture/components/<slug>/architecture.md`.

## Procedure

1. Copy [`architecture.template.md`](architecture.template.md) to `components/<slug>/architecture.md`.
2. Read implementation entry points, tests, and related decisions in owning SAD §9 / DECISION_REGISTRY first.
3. Fill §1–§8 in prose; link UML companions from `UML/Components/<slug>/`.
4. Consolidate related decisions into §9 with stable `### Dn:` anchors per [`QUALITY-STANDARD.md`](../QUALITY-STANDARD.md) §3.
5. Register new or migrated decisions in [`project/DECISION_REGISTRY.md`](../project/DECISION_REGISTRY.md).
6. Update [`project/ROLLOUT.md`](../project/ROLLOUT.md) and [`DOC-HEALTH.md`](../DOC-HEALTH.md).
7. Apply [`QUALITY-STANDARD.md`](../QUALITY-STANDARD.md) before marking Complete.

## Rules

- Internal only: do not publish SAD text to player docs.
- Contracts stay in `docs/architecture/contracts/`; SAD summarizes and links.
- PlantUML under `UML/` is authoritative; Markdown companions include Mermaid previews.
- Do not create new `docs/ADR/adr-*.md` files — use SAD §9 + UML ([governance D5](../project/governance/architecture.md#d5-sad-only-decision-retirement)).
