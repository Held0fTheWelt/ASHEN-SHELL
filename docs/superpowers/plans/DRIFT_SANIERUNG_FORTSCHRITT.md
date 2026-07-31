# Fortschritt Drift-Sanierung

## Zustand
Aktuelle Welle: 7 (started — content contract provenance landed; builtins retirement open)
Aktueller Schritt: authored_facts + deterministic compile; G2 still awaiting approval
Letzter grüner Commit: `…` (W7 content contract) after `7d408799` (W6 retirement)
Baseline: engine_foundation **237**; backend_runtime **89**; content compiler **5 passed**

## Wellen
- [x] W0–W5
- [x] W6 Paketnamen + Retirement — **code complete except G2 table drop**
- [ ] W7 Content-Wahrheit — **partial** (contract + tests; builtins/ai_stack still open)
- [ ] W8–W9

## Entscheidungen
| Datum | Welle | Frage | Entscheidung | Begründung |
| --- | --- | --- | --- | --- |
| 2026-07-31 | 6 | runtime_sessions drop | Park G2 — ask operator | Audit: ORM export only, no live R/W |
| 2026-07-31 | 7 | ReviewExportSeed.generated_at | Default `None` on compile | Deterministic byte-identical exports |

## Geparkte Probleme
| ID | Welle | Problem | Warum geparkt | Auflösung |
| --- | --- | --- | --- | --- |
| P-G2-DB | 6 | Drop `runtime_sessions` | Human gate | `baselines/W6-G2-runtime-sessions-readers.md` — **needs approval** |
| P-W7-BUILTINS | 7 | Delete `goc_solo_builtin_*` | Still wired via `builtin_experience_templates.py` | Generate from YAML or rewire loaders first |
| P-W6-EXT-REFS | 6 | Docs/UML still say `world-engine/app` | Volume | Sweep with SAD / W8 |
| P-W6-CONFIG | 6 | `model-governance` in working `config.json` | Mixed with G4 WIP | Commit with assurance WIP or cherry-pick |
| P-G4-ASSURANCE | * | User WIP | G4 | Unstaged |

## Journal
- 2026-07-31 W6 retirement `7d408799`.
- 2026-07-31 W7: content_version + authored_facts + determinism tests.
