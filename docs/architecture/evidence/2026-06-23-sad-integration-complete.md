# 2026-06-23 SAD/UML integration complete

## Scope

Full integration of internal SAD/UML architecture documentation per rollout plan:

- §9 decision anchors on all 15 SADs
- UML minimum packages for 8 components + 6 project UML folders (+ turn-execution-canonical)
- ADR absorption matrix and README column completion
- Normative contracts index (25 runtime Pi contracts + top-level contracts)
- MkDocs Developer → Architecture (internal)
- Extended architecture documentation gate + link audit

## Test evidence

```powershell
python -m pytest tests/gates/test_architecture_documentation_gate.py -v --tb=short --no-cov
```

Result: **52 passed, 0 failed, 0 skipped**

```powershell
python scripts/architecture_link_audit.py --check
```

Result: **OK: no broken links** (scoped: components/, project/, START-HERE, ADR README, normative index, UML/)

## Rollout

All ROLLOUT rows **Complete** with UML links except governance and quality-gates (process-only, UML `—`).

See [ROLLOUT.md](../project/ROLLOUT.md) and [DOC-HEALTH.md](../DOC-HEALTH.md).
