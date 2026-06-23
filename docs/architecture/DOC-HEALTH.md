# Documentation health (architecture migration)

Last updated: 2026-06-23 (ADR retirement complete)

| Package | SAD | UML | Links | Gate |
| --- | --- | --- | --- | --- |
| world-engine | ok | ok | ok | ok |
| project SADs (7) | ok | ok | ok | ok |
| component SADs (7) | ok | ok | ok | ok |
| contracts migration | ok | — | ok | ok |
| ADR absorption | **retired** | — | ok | ok |

Verification:

```powershell
python -m pytest tests/gates/test_architecture_documentation_gate.py -v --tb=short --no-cov
```

```powershell
python scripts/adr_retirement_audit.py --check
python scripts/architecture_link_audit.py --check
```

Evidence:

- [2026-06-23 ADR retirement complete](evidence/2026-06-23-adr-retirement-complete.md)
- [ADR retirement audit](evidence/adr-retirement-audit.md)
- [Archive manifest](../archive/adr-retired-2026/manifest.json)
