# Abschluss Drift-Sanierung (Zwischenstand)

**Status:** IN PROGRESS — Waves 0–3 landed (W3 commit pending at write time); Waves 4–9 open.  
**Branch tip (before W3 commit):** `drift-sanierung/w3-commit-vocabulary`  
**Do NOT push (G1).** User architecture-assurance WIP preserved (G4).

## Completed

| Wave | Evidence |
| --- | --- |
| W0 | Turn call ledger, budgets, counting adapter; Langfuse history unusable (401) → A16/A17 |
| W1 | world-engine manager unsharded; no SOURCE/exec loader |
| W2 | PersistOutcome + revision; 7-resource write gate; play_run bypass removed; translation cache; D18 characterization |
| W3 | Rich `SituationStatus`; off-map → `partial`; mapping table; beat advance reasons; unit tests green |

## Remaining

W4 capability migration (D26) + E7 · W5 deshard · W6 rename/retire · W7 content · W8 CI · W9 fy-suites (G3) · DoD §9

## Test counts (latest focused)

- W3 unit: **7 passed**, 0 failed (`test_partial_action_commit` + `test_blocked_is_rare` + beat carry-forward)
- W3 narrative_commit (excl. concurrent): **13 passed** then environment hang on Langfuse flush (not assertion failure)

## Commits (local)

`3e4b02cb` → `7959c848` → `6f6015f6` → `5122b1d4` → (W3 next)
