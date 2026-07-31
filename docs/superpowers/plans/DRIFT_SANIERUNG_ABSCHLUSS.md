# Abschluss Drift-Sanierung (Zwischenstand)

**Status:** IN PROGRESS — W0–W6 code complete except **G2** `runtime_sessions` drop; W7–W9 + DoD §9 open.  
**Branch:** `drift-sanierung/w6-package-retirement`  
**Tip:** pending after W6 retirement commit  
**No push (G1). G4 user WIP preserved (assurance tooling left unstaged except intentional config census/subsystem).**

## Commits this continuation

| SHA | Note |
| --- | --- |
| `e12df6ef` | docs handoff refresh |
| *(next)* | W6 retirement: model_governance + cluster/orphan delete |

## Test evidence

- `python tests/run_tests.py --suite engine_foundation --quick` → **237 passed**
- `python tests/run_tests.py --suite backend_runtime --quick` → **89 passed**
- Focused pytest routing/W5/parity → **49 passed**
- Product smoke: `import world_engine` / `import app` / `import app.model_governance` distinct

## W6 retirement summary

- Moved keepers → `backend/app/model_governance/` (+ `adapter_registry`, `ai_adapter`, type copies)
- Deleted dormant `backend/app/runtime/**` and `backend/tests/runtime/**`
- Keeper tests → `backend/tests/model_governance/`
- Retired WE orphans: `session_manager`, `turn_executor`, `branching_turn_executor`, `actor_lane`, `object_admission`, `state_delta` + dedicated tests
- G2 audit: `docs/superpowers/plans/baselines/W6-G2-runtime-sessions-readers.md` — **awaiting human approval**

## Remaining

- **G2:** approve drop of `runtime_sessions`?
- W7 Content-Wahrheit · W8 Test/CI · W9 fy-suites (G3) · DoD §9
- P-W6-EXT-REFS: docs still mention `world-engine/app`
