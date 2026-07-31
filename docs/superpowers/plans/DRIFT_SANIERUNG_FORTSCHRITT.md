# Fortschritt Drift-Sanierung

## Zustand
Aktuelle Welle: 8 (near-complete) / W9 (safe subset)
Aktueller Schritt: CI suite-catalog drain + TurnTrace/out_of_scope gates; G2/G3 still human-blocked
Letzter grüner Commit tip (pre-this wave): `61517caa`
Baseline evidence (this session):
- Focused W8/W9 gates: **14 passed** (`test_no_direct_pytest*`, `out_of_scope*`, element-alias freeze, fy-import, suite orphan, TurnTrace gap)
- `engine_foundation --quick`: **237 passed**

## Wellen
- [x] W0–W6 (G2 DB drop **blocked** — awaiting human approval)
- [x] W7 Content-Wahrheit — builtins → YAML runtime profile; contract provenance landed
- [x] W8 Test-/CI-/Gate-Wahrheit — **allowlist drained to G4-only**; out_of_scope categories; TurnTrace gap contract; element-alias residual freeze
- [ ] W9 fy-suites / hygiene — **G3 prep only** + safe `test_no_fy_suites_import_in_product`; no subtree split

## Human gates (blocked without explicit yes)
| Gate | Status | Notes |
| --- | --- | --- |
| **G1** | Honored | No push |
| **G2** | **BLOCKED** | Do not drop `runtime_sessions` / `RuntimeSessionRecord` |
| **G3** | **BLOCKED** | Prep only: `baselines/W9-G3-fy-suites-split-prep.md` |
| **G4** | Honored | Leave architecture_assurance user WIP unstaged |

## Entscheidungen
| Datum | Welle | Frage | Entscheidung | Begründung |
| --- | --- | --- | --- | --- |
| 2026-07-31 | 6 | runtime_sessions drop | **Blocked G2** | Awaiting explicit user approval; audit only |
| 2026-07-31 | 7 | GoC solo builtins | YAML under `runtime_profiles/` | No hand-maintained content Python |
| 2026-07-31 | 8 | Direct pytest in CI | Migrate workflows to `tests/run_tests.py` | Allowlist ≤1 (`architecture-assurance.yml` G4) |
| 2026-07-31 | 8 | out_of_scope | Closed categories + share baseline | Cap at 1.0 until ownership mapping improves |
| 2026-07-31 | 8 | Element aliasing | Freeze known residuals | Catalog edits need G4 WIP clearance |
| 2026-07-31 | 9 | fy-suites split | **Blocked G3** | Prep doc + import gate only |

## Geparkte Probleme
| ID | Welle | Problem | Warum geparkt | Auflösung |
| --- | --- | --- | --- | --- |
| P-G2-DB | 6 | Drop `runtime_sessions` | Human gate | `baselines/W6-G2-runtime-sessions-readers.md` |
| P-G3-FY | 9 | subtree split | Human gate | `baselines/W9-G3-fy-suites-split-prep.md` |
| P-W8-ASSURE-CI | 8 | `architecture-assurance.yml` still direct pytest | G4 | Migrate after WIP lands |
| P-W8-ALIAS | 8 | validation/commit etc. dual roles | G4 catalog WIP | Resolve anchors in model_catalog |
| P-W7-AISTACK | 7 | ai_stack GoC package still large | YAML-backed adapters | Further shrink follow-up |
| P-G4-ASSURANCE | * | User WIP | G4 | Unstaged |
| P-DoD-PLAYTHROUGH | 9/DoD | Full playthrough metrics refresh | Needs live stack | Re-run W0-B ledger when stack up |

## Journal
- 2026-07-31 W7: `1377486b` YAML profile + delete `goc_solo_builtin_*`.
- 2026-07-31 W8 partial: `ed981782` / tip `61517caa`.
- 2026-07-31 W8 continue: migrate admin/ai-stack/backend/engine/frontend/pre-deployment/quality-gate → suite catalog; TurnTrace + out_of_scope gates; W9 fy-import gate.
