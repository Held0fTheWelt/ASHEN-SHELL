# Abschluss Drift-Sanierung (Zwischenstand)

**Status:** IN PROGRESS — W0–W5 done; W6 **partial** (rename + test import fixes); W7–W9 + DoD §9 open.  
**Branch:** `drift-sanierung/w6-package-retirement`  
**Tip:** `1b73147d`  
**No push (G1). G4 user WIP preserved.**

## Commits this continuation

| SHA | Note |
| --- | --- |
| `bf490078` | W5 finish — game_routes + governance_runtime unshard |
| `4c358c65` | W6 rename `app` → `world_engine` |
| `cd950072` | W6 API-key facade + patch strings |
| `1b73147d` | W6 more test import cleanups |

## Test evidence

- W5: game_routes **40 passed**; no-dynamic-source **7 passed**; SOURCE/exec product scan **0**
- W6 focused: api_key_guard + config_contract + import_determinism **80 passed**
- W6 startup/auth + environment_security **62 passed**
- `python tests/run_tests.py --suite engine_foundation --quick` still may fail until remaining foundation files are fully greened (continue next)

## Remaining

W6: dormant backend cluster delete, model_governance move, orphans, G2 DB · W7–W9 · DoD §9
