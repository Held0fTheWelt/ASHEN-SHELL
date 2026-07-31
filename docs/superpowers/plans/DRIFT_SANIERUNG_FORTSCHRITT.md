# Fortschritt Drift-Sanierung

## Zustand
Aktuelle Welle: 5 (partial — runtime_executor unshard done; backend game API still sharded)
Aktueller Schritt: Assembled `langgraph_runtime_executor_impl.py`; stubs for 63 SOURCE_LINES chunks; E7 reduced retry in bridges
Letzter grüner Commit: `b6111294` (W4); W5 commit pending on `drift-sanierung/w5-deshard-ai-backend`
Baseline-Testlauf: ai_stack boundary/gateway **8 passed**; WE gate+W4 **12 passed**

## Wellen
- [x] W0–W4
- [ ] W5 Entshardung Rest — **partial**: `ai_stack/langgraph/runtime_executor` unsharded; `backend/app` (~66) still open
- [ ] W6–W9

## Entscheidungen
| Datum | Welle | Frage | Entscheidung | Begründung |
| --- | --- | --- | --- | --- |
| 2026-07-31 | 5 | How to unshard runtime_executor | Assemble ordered SOURCE_LINES into one real module; stub chunks | Matches prior exec order; public.py imports impl without exec |
| 2026-07-31 | 5 | E7 growing prompt | Cap context/prior in `bridges.invoke_runtime_adapter_with_langchain` | Real Python path after unshard |

## Geparkte Probleme
| ID | Welle | Problem | Warum geparkt | Auflösung |
| --- | --- | --- | --- | --- |
| P-W5-BACKEND | 5 | backend/app SOURCE shards (~66) + game_routes exec | Session capacity | Continue W5: inventory routes → unshard game/** → remove _load_game_route_implementation |
| P-W5-AI-REST | 5 | Few remaining ai_stack shards outside langgraph | Smaller | Sweep after backend |
| P-MCP-1 | * | claude-context MCP error | Unavailable | Retry |
| P-G4-ASSURANCE | * | User WIP | G4 | Leave unstaged |

## Journal
- 2026-07-31 W3 `fc362157`, W4 `b6111294`.
- 2026-07-31 W5: assemble script + `langgraph_runtime_executor_impl.py` (~9.8k lines); stubbed 63 chunks; public no-exec; E7 in bridges; gates extended.
