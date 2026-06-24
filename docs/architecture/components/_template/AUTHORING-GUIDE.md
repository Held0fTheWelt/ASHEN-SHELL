# Authoring a component SAD

Produces `docs/architecture/components/<slug>/architecture.md`.

## Procedure

1. Copy [`architecture.template.md`](architecture.template.md) to `components/<slug>/architecture.md`.
2. Read implementation entry points, tests, and related decisions in owning SAD §9 / DECISION_REGISTRY first.
3. Read archived ADR under `docs/archive/adr-retired-2026/` when consolidating §9.
4. Fill §1–§8 in prose; link UML companions from `UML/Components/<slug>/`.
5. Consolidate related decisions into §9 with stable `### Dn:` anchors per [`QUALITY-STANDARD.md`](../QUALITY-STANDARD.md) §3.
6. Add [`mechanism-catalog.md`](mechanism-catalog.template.md) and [`evidence-matrix.md`](evidence-matrix.template.md) when required (see QUALITY-STANDARD §3.1–3.2).
7. Extract per-decision diagrams into `UML/Components/<slug>/decisions/`; update TRACEABILITY **Decision** column.
8. Register new or migrated decisions in [`project/DECISION_REGISTRY.md`](../project/DECISION_REGISTRY.md).
9. Run `python scripts/sad_section9_hygiene.py --check` and architecture documentation gate.
10. Update [`project/ROLLOUT.md`](../project/ROLLOUT.md) and [`DOC-HEALTH.md`](../DOC-HEALTH.md).

## Editorial workflow (restructure pass)

```text
archive ADR → distill SAD §9 → mechanism catalog → UML decisions/ → TRACEABILITY → registry
```

Do **not** re-run `sad_bulk_enrich_from_adr.py --apply` on restructured SADs.

## Rules

- Internal only: do not publish SAD text to player docs.
- Contracts stay in `docs/architecture/contracts/`; SAD summarizes and links.
- PlantUML under `UML/` is authoritative; Markdown companions include Mermaid previews.
- Do not create new active `adr-*.md` decision files — use SAD §9 + UML ([governance D5](../project/governance/architecture.md#d5-sad-only-decision-retirement)).
