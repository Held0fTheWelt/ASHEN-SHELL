# Fortschritt Drift-Sanierung

## Zustand
Aktuelle Welle: 8 (partial) / W7 complete for builtins
Aktueller Schritt: CI suite-catalog gates + MVP workflow migration; G2/G3 still human-blocked
Letzter grüner Commit: pending W8 partial after `1377486b` (W7 YAML builtins)
Baseline: engine_foundation **237 passed**; W7 content tests **3 passed**; table_b **18 passed**; adr0039 **6 passed**

## Wellen
- [x] W0–W6 (G2 DB drop **blocked** — awaiting human approval)
- [x] W7 Content-Wahrheit — builtins → YAML runtime profile; contract provenance landed
- [ ] W8 Test-/CI-/Gate-Wahrheit — **partial** (no-direct-pytest gate + allowlist; mvp1/mvp2 workflows on catalog; suite orphan test)
- [ ] W9 fy-suites / hygiene — G3 prep only (`baselines/W9-G3-fy-suites-split-prep.md`)

## Entscheidungen
| Datum | Welle | Frage | Entscheidung | Begründung |
| --- | --- | --- | --- | --- |
| 2026-07-31 | 6 | runtime_sessions drop | **Blocked G2** | Awaiting explicit user approval; audit only |
| 2026-07-31 | 7 | GoC solo builtins | YAML under `runtime_profiles/` | No hand-maintained content Python |
| 2026-07-31 | 8 | Direct pytest in CI | Allowlist remaining workflows | Shrink until empty |
| 2026-07-31 | 9 | fy-suites split | **Blocked G3** | Prep doc only; no external repo |

## Geparkte Probleme
| ID | Welle | Problem | Warum geparkt | Auflösung |
| --- | --- | --- | --- | --- |
| P-G2-DB | 6 | Drop `runtime_sessions` | Human gate | `baselines/W6-G2-runtime-sessions-readers.md` |
| P-G3-FY | 9 | subtree split | Human gate | `baselines/W9-G3-fy-suites-split-prep.md` |
| P-W8-CI | 8 | Remaining direct-pytest workflows | Volume | Drain allowlist |
| P-W7-AISTACK | 7 | ai_stack GoC package still large | Already YAML-backed adapters | Further shrink in follow-up |
| P-G4-ASSURANCE | * | User WIP | G4 | Unstaged |

## Journal
- 2026-07-31 W7: `1377486b` YAML profile + delete `goc_solo_builtin_*`.
- 2026-07-31 W8: mvp1/mvp2 workflows → `tests/run_tests.py`; gates for catalog + no-direct-pytest; ADR0039 path fix.
