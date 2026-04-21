# World of Shadows — MVP v22 Current-State Package

This package is a **current-state-overhauled MVP delivery** built on top of the v21 canonical package.
It preserves the canonical target, keeps the runnable reference scaffold, and adds explicit current-state honesty, validation evidence, and an audit-cycle control layer.

It should be used when you need to:
- understand what the MVP proves now,
- decide what still belongs to repository implementation work,
- hand the next field to a separate implementation AI,
- and re-audit the returned work without losing continuity.

## What this package now combines

- the canonical product and runtime specification,
- the implementation rules and repository target mapping,
- machine-readable workstream manifests,
- a runnable reference scaffold with passing scaffold tests in this delivery environment,
- and audit-cycle documents for iterative improvement.

## Start order

1. Read `START_HERE.md`
2. Read `docs/57_CURRENT_STATE_PROTOCOL.md`
3. Read `docs/61_CURRENT_STATE_VALIDATION_REPORT.md`
4. Read `docs/00_MASTER_MVP.md`
5. Read `docs/42_IMPLEMENTATION_TRUTH_MATRIX.md`
6. Read `docs/50_IMPLEMENTATION_WORKSTREAMS.md`
7. Read `docs/58_AUDIT_CYCLE_PROTOCOL.md`
8. Read `docs/62_AUDIT_SYSTEM_MASTERPROMPT.md`

## Package structure

- `docs/` — canonical MVP chapters plus current-state and audit-cycle chapters
- `examples/` — payload and content examples
- `implementation/` — machine-readable execution guidance plus current-state manifests
- `reference_scaffold/` — runnable proof slice with tests
- `ui_mockups/` — target surface illustrations
- `validation/` — delivery validation artifacts

## Important operating rule

When this MVP is used for implementation work, patch the **real owning component** in the real repository where available.
The scaffold exists to prove seams and payloads, not to replace the repository.
