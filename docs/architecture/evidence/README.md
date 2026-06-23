# Architecture evidence

Durable summaries of architecture documentation audits. These do not replace normative SADs, contracts,
UML, or gate results they reference.

| Report | Purpose |
| --- | --- |
| [2026-06-23 migration baseline audit](2026-06-23-migration-baseline-audit.md) | Pre-migration inventory and known gaps |
| [2026-06-23 SAD migration gate recheck](2026-06-23-sad-migration-gate-recheck.md) | Post-migration gate verification |
| [migration_inventory.csv](migration_inventory.csv) | Machine-readable source → SAD mapping (generated) |

Generate inventory:

```powershell
python scripts/architecture_migration_inventory.py
```
