# Architecture evidence

Durable summaries of architecture documentation audits. These do not replace normative SADs, contracts,
UML, or gate results they reference.

| Report | Purpose |
| --- | --- |
| [2026-06-23 migration baseline audit](2026-06-23-migration-baseline-audit.md) | Pre-migration inventory and known gaps |
| [2026-06-23 SAD migration gate recheck](2026-06-23-sad-migration-gate-recheck.md) | Post-migration gate verification |
| [migration_inventory.csv](migration_inventory.csv) | Machine-readable source → SAD mapping (generated) |
| [architecture-drift-baseline.md](architecture-drift-baseline.md) | Git hotspots, renames and read-only April snapshot comparison |
| [architecture-drift-baseline.json](architecture-drift-baseline.json) | Machine-readable Git and archaeology evidence |
| [architecture-drift-reconciliation.md](architecture-drift-reconciliation.md) | Current/superseded/conflicting/open claims with target directions |

Generate inventory:

```powershell
python scripts/architecture_migration_inventory.py
python -m tools.architecture_assurance drift-evidence --archive-root "<read-only historical artifact root>" --dry-run
python -m tools.architecture_assurance reconcile-drift --dry-run
```
