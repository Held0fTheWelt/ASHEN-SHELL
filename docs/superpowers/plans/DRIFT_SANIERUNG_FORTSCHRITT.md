# Fortschritt Drift-Sanierung

## Zustand
Aktuelle Welle: 6 (near-complete — G2 DB drop parked for human gate)
Aktueller Schritt: dormant backend cluster deleted; model_governance landed; WE orphans retired
Letzter grüner Commit: pending W6 retirement commit
Baseline: `engine_foundation` **237 passed**; `model_governance` **89 passed**; routing/W5/parity **49 passed**

## Wellen
- [x] W0–W5
- [x] W6 Paketnamen + Retirement — **code complete except G2 table drop**
- [ ] W7–W9

## Entscheidungen
| Datum | Welle | Frage | Entscheidung | Begründung |
| --- | --- | --- | --- | --- |
| 2026-07-31 | 6 | Rewrite scope | Only under `world-engine/` (+ few explicit ai_stack WE imports) | `app.config`/`app.api` collide with backend |
| 2026-07-31 | 6 | Orphan deletion | Delete modules **and** dedicated tests | Exact-import consumers were tests only |
| 2026-07-31 | 6 | Keeper deps | Move `adapter_registry` + `ai_adapter` with governance; copy AIActionType/ResponderSection types | Bootstrap/`route_model` require them; avoid keeping dormant cluster |
| 2026-07-31 | 6 | Leftover runtime files | Delete with cluster (no external prod imports) | A11: consumers obsolete |
| 2026-07-31 | 6 | runtime_sessions drop | Park G2 — ask operator | Audit: ORM export only, no live R/W |

## Geparkte Probleme
| ID | Welle | Problem | Warum geparkt | Auflösung |
| --- | --- | --- | --- | --- |
| P-G2-DB | 6 | Drop `runtime_sessions` | Human gate | See `baselines/W6-G2-runtime-sessions-readers.md` — **needs approval** |
| P-W6-EXT-REFS | 6 | Docs/UML still say `world-engine/app` | Volume | Sweep with SAD update / W8–W9 |
| P-MCP-1 | * | claude-context offline | — | Plan anchors |
| P-G4-ASSURANCE | * | User WIP | G4 | Leave unstaged except intentional `config.json` model-governance entry |

## Journal
- 2026-07-31 W5 complete `bf490078`.
- 2026-07-31 W6 rename `4c358c65` + follow-ups.
- 2026-07-31 W6 retirement: `backend/app/model_governance/` created; `backend/app/runtime/**` + `backend/tests/runtime/**` removed; keeper tests under `backend/tests/model_governance/`; WE orphans + tests removed; G2 audit written.
