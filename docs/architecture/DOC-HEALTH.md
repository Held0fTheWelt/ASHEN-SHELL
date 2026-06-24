# Documentation health (architecture migration)

Last updated: 2026-06-23 (SAD restructure complete)

| Package | SAD | UML | Links | Gate |
| --- | --- | --- | --- | --- |
| world-engine | ok | ok | ok | ok |
| project SADs (7) | ok | ok | ok | ok |
| component SADs (8) | ok | ok | ok | ok |
| contracts migration | ok | — | ok | ok |
| SAD restructure | **complete** | decisions/ | ok | ok |

Verification:

```powershell
python -m pytest tests/gates/test_architecture_documentation_gate.py -v --tb=short --no-cov
python scripts/sad_section9_hygiene.py --check
python scripts/rebuild_decision_registry.py --apply
```

Evidence:

- [2026-06-23 SAD restructure complete](evidence/2026-06-23-sad-restructure-complete.md)
- [2026-06-23 world-engine restructure](evidence/2026-06-23-world-engine-restructure.md)
- [ADR retirement complete](evidence/2026-06-23-adr-retirement-complete.md)
