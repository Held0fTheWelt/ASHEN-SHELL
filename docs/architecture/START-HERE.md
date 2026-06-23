# Architecture Entry Document

Fast entry for World of Shadows internal architecture work. Find the normative SAD, contract, UML
package, gate, or evidence record without walking the full tree.

## First reading path

| Need | Read first | Then check |
| --- | --- | --- |
| Documentation standard | [Quality Standard](QUALITY-STANDARD.md) | [Architecture README](README.md#lookup-order) |
| System map | [Ecosystem Topology SAD](project/ecosystem-topology/architecture.md) | [Capability catalog](README.md#capability-catalog) |
| Play service / runtime authority | [world-engine SAD](components/world-engine/architecture.md) | [UML world-engine README](../../UML/Components/world-engine/README.md) |
| ADR absorption policy | [Governance SAD](project/governance/architecture.md) | [ADR README](../ADR/README.md) |
| Gates and test suites | [Quality Gates SAD](project/quality-gates/architecture.md) | `python tests/run_tests.py --help` |
| Migration status | [DOC-HEALTH](DOC-HEALTH.md) | [ROLLOUT](project/ROLLOUT.md) |

## Verification commands

From repository root:

```powershell
python scripts/architecture_migration_inventory.py
python tests/run_tests.py --suite engine
python -m pytest tests/gates/ -v --tb=short --no-cov
```

After SAD or UML changes, run the architecture documentation gate:

```powershell
python -m pytest tests/gates/test_architecture_documentation_gate.py -v
```

## Status and evidence

Prefer the latest file under [evidence/](evidence/README.md) over ad-hoc chat summaries.

| Question | Entry |
| --- | --- |
| Migration baseline | [2026-06-23 migration baseline audit](evidence/2026-06-23-migration-baseline-audit.md) |
| Gate recheck | [2026-06-23 SAD migration gate recheck](evidence/2026-06-23-sad-migration-gate-recheck.md) |
| ADR duplicate policy | [Governance SAD D4](project/governance/architecture.md#d4-adr-duplicate-resolution) |
