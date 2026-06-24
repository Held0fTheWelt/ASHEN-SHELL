# Migration baseline audit (2026-06-23)

**Inputs:** repository filesystem scan, [`migration_inventory.csv`](migration_inventory.csv) (158 rows), plan
`wos_sad-uml_migration`.

## Findings

| ID | Severity | Finding | Follow-up |
| --- | --- | --- | --- |
| B1 | Blocker | No `UML/` tree before migration | Created `UML/README.md` and pilot world-engine package |
| B2 | Major | `docs/architecture/README.md` was redirect-only | Replaced with capability catalog in Phase 2 |
| B3 | Major | `docs/archive/documentation-consolidation-2026/` missing ledgers | [README stub](../../archive/documentation-consolidation-2026/README.md) documents gap |
| B4 | Major | Duplicate ADRs: ADR-0058 (two files), ADR-0021 (root + legacy) | [Governance SAD D4](../project/governance/architecture.md#d4-adr-duplicate-resolution) |
| B5 | Major | ADR README catalog incomplete vs filesystem (0044–0071 subset missing) | Phase 4 README update |
| B6 | Minor | `docs/governance/README.md` missing | Created |

## ADR duplicate resolution (Phase 0 decision)

- **ADR-0058 canonical file:** `adr-0058-director-driven-pulse-block-stream-bus.md` (shorter slug matches code references). The variant `adr-0058-director-driven-pulse-and-block-stream-bus.md` is deprecated stub → canonical.
- **ADR-0021:** archived legacy copy `adr-0021-runtime-authority.md` under `docs/archive/adr-retired-2026/`; canonical authority is ADR-0001 / world-engine SAD D1.

## Status

Migration scaffolding **started**. Pilot target: world-engine SAD + UML.
