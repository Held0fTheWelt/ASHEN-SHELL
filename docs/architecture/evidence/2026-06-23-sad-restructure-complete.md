# SAD restructure complete — 2026-06-23

## Summary

| Item | Count |
| --- | ---: |
| Component SADs with mechanism-catalog | 8 |
| Project SADs with mechanism-catalog | 7 |
| UML decisions/ packages | 15 |
| DECISION_REGISTRY rows | 98 (manifest-backed) |
| Architecture doc gate tests | see command output |

## Commands

```powershell
python scripts/sad_restructure_scaffold.py --apply
python scripts/rebuild_decision_registry.py --apply
python scripts/sad_section9_hygiene.py --check
python scripts/adr_retirement_audit.py --report
python -m pytest tests/gates/test_architecture_documentation_gate.py -v --tb=short --no-cov
```

## Pilot highlights

- **world-engine:** mechanism-catalog, evidence-matrix, UML `decisions/`, TRACEABILITY Decision column
- **ai-stack:** removed duplicate D8–D14 block; split D12 capability / D15 pause / D16 pulse; expanded §8 cross-links

## Governance

- [QUALITY-STANDARD §3.1–3.2](../QUALITY-STANDARD.md)
- [AUTHORING-GUIDE restructure workflow](../components/_template/AUTHORING-GUIDE.md)
