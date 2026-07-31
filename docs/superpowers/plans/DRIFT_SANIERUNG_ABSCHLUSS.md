# Abschluss Drift-Sanierung (Zwischenstand)

**Status:** IN PROGRESS — W0–W5 done; W6 **partial** (package rename); W7–W9 + DoD §9 open.  
**Branch:** `drift-sanierung/w6-package-retirement`  
**No push (G1). G4 user WIP preserved.**

## Commits (local)

| SHA | Note |
| --- | --- |
| … → `eb09085d` | W5 langgraph |
| `bf490078` | W5 backend game+governance |
| (pending) | W6 rename `app` → `world_engine` |

## Test counts (this session)

- W5 finish: game_routes **40 passed**; no-dynamic-source **7 passed**; product SOURCE/exec scan **0**
- W6 rename smoke: import_determinism + gates + capability **12 passed**
- Dual import: `world_engine` → `world-engine/world_engine`; backend `app` → `backend/app`

## Remaining

W6 retirement (backend cluster, orphans, model_governance, G2 DB) · W7–W9 · DoD §9
