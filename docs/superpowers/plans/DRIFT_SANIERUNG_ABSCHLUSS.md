# Drift-Sanierung Abschluss (running)

**Status:** IN PROGRESS — W0–W8 advanced; **G2 blocked**; **G3 blocked**; W9 safe subset only; DoD §9 not fully evidenced.  
**Branch:** `drift-sanierung/w6-package-retirement`  
**No push (G1). G4 architecture_assurance WIP left unstaged.**

## Waves (summary)

| Wave | Result |
| --- | --- |
| W0–W5 | Cost ledger, write topology, SituationStatus, D26, E7, SOURCE unshard (prior commits) |
| W6 | Package rename + retirement; **G2 table drop parked** |
| W7 | Content contract + YAML GoC solo; builtins deleted |
| W8 | Suite-catalog CI; allowlist → G4-only; out_of_scope categories; TurnTrace gaps; alias residual freeze |
| W9 | G3 prep only + `test_no_fy_suites_import_in_product` |

## Test evidence (this continuation)

### Focused W8/W9 gates
Command:
```bash
python -m pytest tests/gates/test_no_direct_pytest_in_workflows.py \
  tests/gates/test_out_of_scope_requires_reason.py \
  tests/gates/test_no_element_has_two_authority_roles.py \
  tests/gates/test_no_fy_suites_import_in_product.py \
  tests/gates/test_every_test_file_has_suite_or_exception.py \
  tests/gates/test_trace_gap_is_reported_as_partial.py -v --tb=short --no-cov
```
Result: **14 passed, 0 failed, 0 skipped, 0 errors**

### engine_foundation
Command: `python tests/run_tests.py --suite engine_foundation --quick`  
Result: **237 passed, 0 failed, 0 skipped, 0 errors** (86.11s)

### Known non-blocking / parked failures
- Full `gates --quick` may fail on `test_better_tomorrow_architecture_assurance_gate` when **G4 WIP** `tools/architecture_assurance/config.json` is dirty in the working tree — do not “fix” by staging that WIP.
- Element dual-authority residuals remain frozen until G4 catalog cleanup.

## Human gates

| Gate | Status |
| --- | --- |
| G1 No push | Honored |
| G2 Drop runtime_sessions | **BLOCKED** — needs explicit user yes |
| G3 fy-suites subtree split | **BLOCKED** — prep only |
| G4 Leave assurance WIP | Honored |

## Honest rest list (DoD §9 — not yet fully evidenced)
- G2 persistence drop still open (intentionally).
- G3 external fy-suites repo not created (intentionally).
- architecture-assurance workflow still direct pytest (G4).
- Model-catalog dual authority roles not resolved (G4).
- Full playthrough / `unattributed_call_count == 0` live metrics need stack re-run.
- UML CI artifact publish / SARIF-JUnit identity not re-verified this session.
- Full `--suite all` green not claimed.
- Reconnect player-visible block ordering/dedup gate not newly added this session (`tests/e2e/test_phase5_reconnect_reentry.py` pre-exists).
