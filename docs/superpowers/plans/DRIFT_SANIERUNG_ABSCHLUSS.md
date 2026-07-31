# Abschluss Drift-Sanierung (Zwischenstand)

**Status:** IN PROGRESS — W0–W6 code complete except **G2**; W7 **partial**; W8–W9 + DoD §9 open.  
**Branch:** `drift-sanierung/w6-package-retirement`  
**Tip:** `95ee9180`  
**No push (G1). G4 user WIP preserved.**

## Commits this continuation

| SHA | Note |
| --- | --- |
| `7d408799` | W6 retirement: model_governance + cluster/orphan delete |
| `95ee9180` | W7: content_version + authored_facts + determinism tests |

## Test evidence

- `python tests/run_tests.py --suite engine_foundation --quick` → **237 passed**
- `python tests/run_tests.py --suite backend_runtime --quick` → **89 passed**
- Focused routing/W5/parity → **49 passed**
- `pytest backend/tests/content/test_content_compiler.py` → **5 passed**

## W6 retirement

- `backend/app/model_governance/` owns routing keepers
- Deleted dormant `backend/app/runtime/**` + `backend/tests/runtime/**`
- Retired WE orphans + dedicated tests
- G2 audit: `baselines/W6-G2-runtime-sessions-readers.md` — **awaiting human approval**

## W7 partial

- `CanonicalCompileOutput.content_version` + `authored_facts` with `source_provenance`
- Deterministic compile (`generated_at=None`)
- Still open: delete `goc_solo_builtin_*`, shrink `ai_stack/.../god_of_carnage`, lane-root correction in assurance config (G4-mixed)

## Human gates pending

1. **G2:** Drop DB table `runtime_sessions`? (audit shows no live Python R/W)
2. **G3:** fy-suites subtree split (W9) — not reached yet
3. **G1:** no push
4. **G4:** assurance WIP left unstaged

## Remaining toward DoD §9

W7 builtins retirement · W8 suite/CI/trace · W9 fy-suites/hygiene · full suite green evidence · SAD/UML path sweep
