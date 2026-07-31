# Abschluss Drift-Sanierung (Zwischenstand)

**Status:** IN PROGRESS — W0–W7 done for planned builtins/contract work; **G2 blocked**; W8 partial; W9 G3 prep only; DoD §9 open.  
**Branch:** `drift-sanierung/w6-package-retirement`  
**Tip:** `ed981782`  
**No push (G1). G4 assurance WIP preserved. G2 must not drop `runtime_sessions`.**

## Commits this continuation

| SHA | Note |
| --- | --- |
| `1377486b` | W7: GoC solo YAML runtime profile; delete builtins |
| *(next)* | W8 partial: CI catalog gates + mvp workflow migration |

## Test evidence

- `python tests/run_tests.py --suite engine_foundation --quick` → **237 passed** (junit)
- `pytest tests/gates/test_w7_*` + content compiler (earlier) → **8 passed** focused content set
- `pytest tests/gates/test_table_b_anti_hardcoding_gate.py` → **18 passed**
- `pytest tests/gates/test_adr0039_runtime_surface_governance.py` → **6 passed**
- New W8 gates (`no_direct_pytest`, `every_test_file_has_suite`) → **7 passed** with related W7 gates

## Human gates

| Gate | Status |
| --- | --- |
| G1 no push | Honored |
| G2 `runtime_sessions` drop | **Awaiting explicit user approval** — audit kept |
| G3 fy-suites split | **Awaiting approval** — prep only |
| G4 assurance WIP | Unstaged |

## Remaining toward DoD §9

Drain CI pytest allowlist · out_of_scope reasons · element aliasing · TurnTrace gaps · playthrough metrics refresh · W9 hygiene · full suite green evidence
