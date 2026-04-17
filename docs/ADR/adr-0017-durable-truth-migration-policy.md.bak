# ADR-0017: Durable-truth migration verification and archive policy

Date: 2026-04-17

Status: Accepted (documentation consolidation policy)

## Context

During a documentation consolidation effort, many source documents were merged into canonical technical pages, while historical plans and specs were moved to `docs/archive/` for evidence preservation. The consolidation requires a clear, auditable policy for where decisions live and how archival sources are referenced.

## Decision

- Canonical Architecture Decision Records live under `docs/ADR/` and are the single source of truth for architecture decisions and long-lived boundaries.
- Migration verification tables and consolidation ledgers remain in `docs/archive/documentation-consolidation-2026/` as evidence, but any explicit decision text discovered in those sources must be migrated into a new or existing ADR.
- Archived files that contained decisions must be updated with a short "Migrated Decision" pointer line referencing the canonical ADR (e.g., `Migrated Decision: See ADR-XXXX`) and left in archive for historical context.
- Where migration moves a decision into an existing ADR, append a `Migrated Decision (...)` section into the ADR to preserve provenance and source file references.
- Evidence-only archival materials (gate tables, test matrices, historical plans) may remain in `docs/archive/` without ADR counterparts, provided their role is explicitly documented in the migration verification table.

## Rationale

- Prevent duplication of authoritative decision text and reduce drift between docs and code.
- Preserve historical evidence for audits, but avoid active documentation divergence.
- Provide automated discoverability for contractify and other tooling that expects ADRs in `docs/ADR/`.

## Consequences

- Some archive files will be edited to include pointer lines; CI tests that reference archived paths must be updated to expect pointers or canonical ADR paths.
- Contractify discovery should be configured to prefer `docs/ADR/` while allowing archive evidence to remain discoverable for audit purposes.

## Migrated from

Consolidation artifacts: `docs/archive/documentation-consolidation-2026/DURABLE_TRUTH_MIGRATION_VERIFICATION_TABLE.md` and related consolidation ledgers.

---

(Automated migration entry created 2026-04-17)
