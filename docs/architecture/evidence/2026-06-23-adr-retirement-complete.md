# ADR retirement complete — 2026-06-23

## Summary

| Item | Count |
| --- | ---: |
| ADRs archived | 102 |
| ADR stub dir active files | 1 (README stub) |
| DECISION_REGISTRY rows | 98 |
| SAD files bulk-enriched | 10 |
| Reference files rewritten | 54 |

## Commands

```powershell
python scripts/sad_bulk_enrich_from_adr.py --apply
python scripts/adr_retirement_archive.py --apply
python scripts/adr_reference_rewrite.py --apply
python scripts/sad_post_retirement_fixup.py
python scripts/bootstrap_decision_registry.py
python scripts/adr_retirement_audit.py --report
python -m pytest tests/gates/test_architecture_documentation_gate.py -q --tb=short --no-cov
```

## Gate evidence

Architecture documentation gate: **55 passed** (includes `test_no_active_adr_files`, `test_sad_decision_prose_minimum`).

Link audit: `python scripts/architecture_link_audit.py --check` → OK.

## Normative surface

- Decisions: `docs/architecture/**/architecture.md` §9
- Index: `docs/architecture/project/DECISION_REGISTRY.md`
- Archive: `docs/archive/adr-retired-2026/manifest.json`
- Stub: [ADR README](../../ADR/README.md) → START-HERE + DECISION_REGISTRY

## Open exceptions (Not Finished / Proposed)

13 ADRs remain **open exceptions** in SAD §9 (governance D6–D10, world-engine W5, security D4, ai-stack D12 collision). Archive copies preserved; gates do not require parity closure for open status.

## Excluded

- `'fy'-suites/` — not rewritten (per plan)
