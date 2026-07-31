# Fortschritt Drift-Sanierung

## Zustand
Aktuelle Welle: 6 (partial — package rename landed; retirement/DB/orphans open)
Aktueller Schritt: `world-engine/app` → `world_engine`; dual-import smoke green; cluster deletion deferred
Letzter grüner Commit: `bf490078` (W5 complete); W6 rename commit pending
Baseline: import_determinism + gates **12 passed**; `import world_engine` + `import app` distinct

## Wellen
- [x] W0–W5
- [ ] W6 Paketnamen + Retirement — **partial**: rename + path hygiene; dormant backend cluster / orphans / G2 DB open
- [ ] W7–W9

## Entscheidungen
| Datum | Welle | Frage | Entscheidung | Begründung |
| --- | --- | --- | --- | --- |
| 2026-07-31 | 6 | Rewrite scope | Only under `world-engine/` (+ few explicit ai_stack WE imports) | `app.config`/`app.api` collide with backend |
| 2026-07-31 | 6 | Orphan deletion | Defer — tests still consume session_manager/turn_executor/actor_lane/… | Consumer search non-zero |
| 2026-07-31 | 6 | runtime_sessions drop | Park G2 | Human gate |

## Geparkte Probleme
| ID | Welle | Problem | Warum geparkt | Auflösung |
| --- | --- | --- | --- | --- |
| P-G2-DB | 6 | Drop `runtime_sessions` | Human gate | Operator approval |
| P-W6-CLUSTER | 6 | Delete dormant backend runtime cluster + move model_governance | Large; needs consumer proofs | Continue next session |
| P-W6-ORPHANS | 6 | Delete WE orphan runtime modules | Tests still import | Retire with tests |
| P-W6-EXT-REFS | 6 | Docs/UML still say `world-engine/app` | Volume | Sweep with SAD update |
| P-MCP-1 | * | claude-context offline | — | Plan anchors |
| P-G4-ASSURANCE | * | User WIP | G4 | Unstaged |

## Journal
- 2026-07-31 W5 complete `bf490078`.
- 2026-07-31 W6: `git mv app world_engine`; import rewrite; Dockerfile/CMD; root conftest append path; accidental backend rewrite reverted via `git checkout HEAD -- backend/app`.
