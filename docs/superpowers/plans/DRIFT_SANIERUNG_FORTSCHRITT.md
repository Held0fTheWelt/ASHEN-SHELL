# Fortschritt Drift-Sanierung

## Zustand
Aktuelle Welle: 8 complete / W9 (G3 parked post-merge) / DoD remainder open
Aktueller Schritt: Architecture-assurance path truth retargeted (`world-engine/app` → `world-engine/world_engine`); AA suite green
Letzter grüner Commit tip: (this session; see journal)
Baseline evidence (this session): AA suite `--quick` **30 passed**; depth gate PASS (0 failures)

## Wellen
- [x] W0–W6 including **G2** `runtime_sessions` drop (COUNT=0; migration 049; up/down evidenced)
- [x] W7 Content-Wahrheit — builtins → YAML runtime profile; contract provenance landed
- [x] W8 Test-/CI-/Gate-Wahrheit — direct-pytest allowlist **0**; dual-role aliases resolved; out_of_scope; TurnTrace
- [ ] W9 fy-suites / hygiene — **G3 parked** until branch merged **and** pushed; import gate already landed

## Human gates
| Gate | Status | Notes |
| --- | --- | --- |
| **G1** | Honored | No push (never) |
| **G2** | **DONE** | COUNT=0; no archive; Alembic 049; model removed; gate green; up/down logged |
| **G3** | Parked | Trigger: after sanierung branch **merged and pushed**, as separate operation. Prep: `baselines/W9-G3-fy-suites-split-prep.md`. No fy-suites/** delete/move until then. |
| **G4** | **DONE** | Landed in `de2cff5b`; ASSURE-CI + ALIAS unblocked and executed |

Authority: `docs/superpowers/plans/DRIFT_SANIERUNG_GATE_ENTSCHEIDUNGEN.md` supersedes stale “awaiting yes” lines.

## Entscheidungen
| Datum | Welle | Frage | Entscheidung | Begründung |
| --- | --- | --- | --- | --- |
| 2026-07-31 | 6 | runtime_sessions drop | **Approved G2** (executed) | Gate decisions + COUNT=0 + up/down evidence |
| 2026-07-31 | 7 | GoC solo builtins | YAML under `runtime_profiles/` | No hand-maintained content Python |
| 2026-07-31 | 8 | Direct pytest in CI | Migrated to `tests/run_tests.py` | Allowlist = 0 |
| 2026-07-31 | 8 | Element aliasing | Distinct role-accurate anchors | Residuals cleared |
| 2026-07-31 | 9 | fy-suites split | **Not now** | After merge+push only |
| 2026-07-31 | DoD | AA path convention | `world-engine/world_engine` only | No dual `world-engine/app` product truth |

## Geparkte Probleme
| ID | Welle | Problem | Warum geparkt | Auflösung |
| --- | --- | --- | --- | --- |
| P-G3-FY | 9 | subtree split | Trigger: after merge+push | `baselines/W9-G3-fy-suites-split-prep.md` |
| P-W7-AISTACK | 7 | ai_stack GoC package still large | YAML-backed adapters | Further shrink follow-up |
| P-DoD-PLAYTHROUGH | 9/DoD | Full playthrough metrics refresh | Needs live stack + attribution pass | Re-run W0-B ledger when ready |
| P-DoD-UML-SARIF | DoD | UML CI artifact / SARIF-JUnit identity | Not re-verified as publish pipeline this session | Separate evidence publish pass |
| P-DoD-SUITE-ALL | DoD | `--suite all` green | Not claimed | Full suite run |

## Journal
- 2026-07-31 W7: `1377486b` YAML profile + delete `goc_solo_builtin_*`.
- 2026-07-31 W8 partial: `ed981782` / tip `61517caa`.
- 2026-07-31 W8 continue: migrate admin/ai-stack/backend/engine/frontend/pre-deployment/quality-gate → suite catalog; TurnTrace + out_of_scope gates; W9 fy-import gate.
- 2026-07-31 G4 landed in `de2cff5b` (assurance WIP + runway docs).
- 2026-07-31 G2: COUNT(*)=0 on `backend/instance/wos.db`; migration 049 up/down/up; model deleted; `test_runtime_sessions_table_absent`.
- 2026-07-31 P-W8-ASSURE-CI: `architecture-assurance.yml` → `tests/run_tests.py --suite architecture_assurance`; allowlist 0.
- 2026-07-31 P-W8-ALIAS: world-engine catalog dual-role anchors separated; freeze gate now asserts zero offenders.
- 2026-07-31 P-DoD-ASSURE-GATE: retarget product paths `world-engine/app` → `world-engine/world_engine`; retire `backend_runtime_session` write surfaces; add `model-governance` catalog/SAD; regenerate bindings/views/canon. Suite: **30 passed, 0 failed**.
