# Architecture documentation health

**Reconciled:** 2026-08-11 at `a1b5db907b0484f8898f5caf3fdc57edd6efb46c`
**Posture:** structurally operational; known product-architecture nonconformance remains open

| Concern | State | Evidence / gap |
| --- | --- | --- |
| Whole-system authority | Active | [System SAD](system/architecture.md) |
| Current vs target separation | Active | statement types + [violation register](violations/README.md) |
| Active decisions | Active | [ADR index](decisions/README.md) |
| L3 runtime architecture | Active for canonical turn | [Canonical turn](scenarios/canonical-turn.md) |
| Data ownership | Active | [Writer matrix](data/data-ownership.md) |
| Git/AKDB lineage | Active and included in canon | [Lineage](evidence/architecture-lineage.md) |
| Component SAD synthesis | In progress | World Engine complete; AI/governance/MVP portfolios still contain historical accumulation (`AR-V008`) |
| UML single-source concerns | Resolved for World Engine | duplicate sequence/state projections removed (`AR-V007`) |
| Direct architecture coverage | Operational and enforced | 7,500 / 7,500 discovered semantic units represented; 0 `unmapped` (`AR-V009` resolved) |

The census counts discovered semantic units such as functions, routes, schema objects, content keys,
web assets and deployment services. It is not a raw file count and may contain the same source unit
in more than one project-level concern.

`Complete` is not used as a synonym for “files exist.” A scope becomes `Conforming` only when its
normative decisions, implementation, runtime scenarios and closure evidence agree.
