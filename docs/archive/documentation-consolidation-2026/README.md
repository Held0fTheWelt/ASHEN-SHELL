# Documentation consolidation archive (2026)

This folder is referenced from [`docs/README.md`](../../README.md) and
[`docs/technical/README.md`](../../technical/README.md) as the home for the 2026 documentation
overhaul ledgers (`TOPIC_CONSOLIDATION_MAP.md`, `DURABLE_TRUTH_MIGRATION_LEDGER.md`, etc.).

## Current repository state

Those ledger files are **not present** in this workspace snapshot. They may exist on other branches
or were never committed to this clone. Do not recreate historical audit content here during the
SAD/UML migration.

## Where active truth lives now

- Architecture SADs: [`docs/architecture/`](../../architecture/START-HERE.md)
- Technical runtime contracts (transition): [`docs/technical/runtime/`](../../technical/runtime/)
- Migration baseline: [`docs/architecture/evidence/2026-06-23-migration-baseline-audit.md`](../../architecture/evidence/2026-06-23-migration-baseline-audit.md)

## Policy

Per [ADR-0029](../../ADR/adr-0029-residue-removal-policy.md) and [ADR-0017](../../ADR/adr-0017-durable-truth-migration-policy.md),
use traceable moves (stub + owning SAD) instead of silent drift.
