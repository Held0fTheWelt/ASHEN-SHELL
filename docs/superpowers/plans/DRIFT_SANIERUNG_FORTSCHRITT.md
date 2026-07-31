# Fortschritt Drift-Sanierung

## Zustand
Aktuelle Welle: 5 complete → starting 6
Aktueller Schritt: Backend game + governance unsharded; zero SOURCE/exec(compile) under ai_stack, backend/app, world-engine/app
Letzter grüner Commit: `eb09085d` (W5 langgraph); W5 backend commit pending
Baseline-Testlauf: game_routes **40 passed**; no-dynamic-source **7 passed**; product-tree SOURCE/exec scan **0/0**

## Wellen
- [x] W0–W4
- [x] W5 Entshardung (runtime_executor + game_routes + governance_runtime; leftover ai_stack shards already 0)
- [ ] W6 Paketnamen + Retirement
- [ ] W7 Content-Wahrheit
- [ ] W8 Test-/CI-/Gate-Wahrheit
- [ ] W9 Werkzeugplattform + Hygiene

## Entscheidungen
| Datum | Welle | Frage | Entscheidung | Begründung |
| --- | --- | --- | --- | --- |
| 2026-07-31 | 5 | game_routes / governance loader | Assemble SOURCE → `*_impl.py`; `sys.modules[__name__] = impl` | Preserves monkeypatch namespace; removes exec(compile) |
| 2026-07-31 | 5 | Route inventory | 29 routes baseline `W5-game-route-inventory.txt` | Exit criterion proof |

## Geparkte Probleme
| ID | Welle | Problem | Warum geparkt | Auflösung |
| --- | --- | --- | --- | --- |
| P-MCP-1 | * | claude-context offline | Unavailable | Plan anchors |
| P-LANGFUSE-FLUSH | * | Manager tests hang on flush | Env | Disable in test env |
| P-G4-ASSURANCE | * | User WIP | G4 | Leave unstaged |
| P-G2-DB | 6 | Drop `runtime_sessions` | Human gate | Document; do not drop without G2 |

## Journal
- 2026-07-31 W5 langgraph `eb09085d`.
- 2026-07-31 W5 backend: assembled game_routes_impl + governance_runtime_service_impl; stubbed 66 segments; structure+routes 40 passed.
