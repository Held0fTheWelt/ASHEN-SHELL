# Drift-Sanierung Abschluss

**Status:** WAVE WORK COMPLETE for gated items G2/G4; G3 parked with trigger; DoD §9 remainder still open (playthrough / suite-all / UML publish). Architecture-assurance path residue fixed.  
**Branch:** `drift-sanierung/w6-package-retirement`  
**No push (G1).** Gate authority: `DRIFT_SANIERUNG_GATE_ENTSCHEIDUNGEN.md`.

## Waves (summary)

| Wave | Result |
| --- | --- |
| W0–W5 | Cost ledger, write topology, SituationStatus, D26, E7, SOURCE unshard (prior commits) |
| W6 | Package rename + retirement; **G2 `runtime_sessions` dropped** (COUNT=0; Alembic 049) |
| W7 | Content contract + YAML GoC solo; builtins deleted |
| W8 | Suite-catalog CI; **direct-pytest allowlist = 0**; dual-role aliases resolved; out_of_scope; TurnTrace |
| W9 | G3 prep only + `test_no_fy_suites_import_in_product`; **subtree split not now** |
| DoD (ungated) | Architecture assurance path truth → `world-engine/world_engine`; AA suite green |

## Human gates

| Gate | Status |
| --- | --- |
| G1 No push | Honored |
| G2 Drop runtime_sessions | **DONE** — COUNT=0; no archive; migration 049 up/down evidenced; model removed; gate added |
| G3 fy-suites subtree split | **Parked** — trigger: after this branch is **merged and pushed**, as a separate operation. Prep doc retained. No `fy-suites/**` delete/move. |
| G4 assurance WIP | **DONE** — landed in `de2cff5b`; ASSURE-CI + ALIAS executed afterward |

## Test evidence (this continuation)

### Architecture assurance path retarget
Command:
```bash
python tests/run_tests.py --suite architecture_assurance --quick
```
Result: **30 passed, 0 failed, 0 skipped, 0 errors**

Depth gate (pre-fix ~3210 failures → after):
```bash
python -c "from pathlib import Path; from tools.architecture_assurance.audit import build_report; r=build_report(Path('tools/architecture_assurance/config.json'), Path('.').resolve()); print(r['gate']['status'], len(r['gate']['failures']))"
```
Result: **PASS**, **0** failures (census discovered/represented=7500; subsystems=17; views model=94)

Also:
```bash
python -m pytest tests/gates/test_better_tomorrow_architecture_assurance.py -v --tb=short --no-cov
```
Result: **1 passed, 0 failed, 0 skipped, 0 errors**

### Prior focused W8/W9/G2 gates (unchanged claim)
Command:
```bash
python -m pytest tests/gates/test_no_direct_pytest_in_workflows.py \
  tests/gates/test_out_of_scope_requires_reason.py \
  tests/gates/test_no_element_has_two_authority_roles.py \
  tests/gates/test_no_fy_suites_import_in_product.py \
  tests/gates/test_every_test_file_has_suite_or_exception.py \
  tests/gates/test_trace_gap_is_reported_as_partial.py \
  tests/gates/test_runtime_sessions_table_absent.py -v --tb=short --no-cov
```
Result (prior session): **15 passed, 0 failed, 0 skipped, 0 errors**

## §9 Honest remainder (still open — with reason)

| Item | Status | Reason |
| --- | --- | --- |
| G2 persistence drop | **Done** | Prior session |
| G3 external fy-suites repo | Open (parked) | Trigger = after merge **and** push; not now |
| architecture-assurance.yml direct pytest | **Done** | Migrated to `tests/run_tests.py` |
| Model-catalog dual authority roles | **Done** | Distinct anchors; gate asserts zero |
| Architecture assurance path convention / depth gate | **Done** | Product paths use `world-engine/world_engine`; AA suite 30/30 |
| Full playthrough / `unattributed_call_count == 0` | Open | Needs live attribution / playthrough stack pass |
| UML CI artifact publish / SARIF-JUnit identity | Open | Not re-verified as publish pipeline this session |
| Full `--suite all` green | Open | Not claimed / not run as full suite here |
| Reconnect player-visible block ordering/dedup gate | Open | Existing `tests/e2e/test_phase5_reconnect_reentry.py` only; dedicated gate not newly added |

**Do not declare remediation complete solely from W0–W9 checkboxes while §9 open items remain.** Path-residue gate is cleared; remaining DoD items need their own evidence.
