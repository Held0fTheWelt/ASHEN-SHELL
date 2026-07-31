# Abschluss Drift-Sanierung (Zwischenstand)

**Status:** IN PROGRESS — Waves 0–4 implemented locally; Waves 5–9 and DoD §9 open.  
**Branch:** `drift-sanierung/w4-capability-migration`  
**Do NOT push (G1).** User architecture-assurance WIP preserved (G4).

## Completed

| Wave | Commit | Evidence |
| --- | --- | --- |
| W0 | `3e4b02cb` | Cost ledger / budgets |
| W1 | `7959c848` (+ `6f6015f6`) | Manager unshard |
| W2 | `5122b1d4` | Write topology + translation cache |
| W3 | `fc362157` | Rich SituationStatus / partial / mapping |
| W4 | (this wave) | D26 models, permissive MutationPolicy, E7 policies, switches |

## Remaining

W5 deshard (171 modules; includes P-W4-SHARD-E7) · W6 rename/retire (G2 DB) · W7 · W8 · W9 (G3) · DoD §9

## Latest test counts

- W4 focused: **10 passed**, 0 failed  
  `python -m pytest world-engine/tests/test_state_delta_partial_acceptance.py world-engine/tests/test_capability_switch_defaults.py world-engine/tests/test_technical_failure_fallback_chain.py`
- W3 unit (earlier): **7 passed**
