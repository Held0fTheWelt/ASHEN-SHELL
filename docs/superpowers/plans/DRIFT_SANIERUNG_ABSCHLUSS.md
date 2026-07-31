# Drift-Sanierung — Abschlussbericht (PARTIAL)

**Date:** 2026-07-31  
**Branch:** `drift-sanierung/w1-unshard-authority` (from `drift-sanierung/w0-cost-truth`)  
**Status:** **Partially complete** — Wave 0 done (W0-C emitter hooked after W1 unshard); Wave 1 authority-path unshard done for world-engine manager; Wave 2 started (`PersistOutcome` + `session.revision`); Waves 3–9 not executed in this session.

This report is required even when incomplete (Auftrag §10 point 6).

---

## 1. Per-wave summary

### Wave 0 — Cost truth
**Built**
- `story_runtime_core/model_call_accounting.py` — `TurnCallLedger`, `CountingModelAdapter`, phase contextvars, soft/hard budgets (defaults 12/24, A10).
- Wrapped adapters in `governed_runtime_adapters.py`.
- Ledger bind in `turn_execution.py`; `aggregate_phase_costs` extended with call counts.
- Budgets in `runtime_config._turn_call_budgets`.
- UML `UML/Project/architecture-drift/turn-cost-ledger.puml`.
- Drift edges + `turn-cost-envelope-v1`.
- W0-C: unsharded `_emit_langfuse_evidence_observations` emits one generation observation per ledger row; judge filters remain pinned to `story.model.generation`.

**Deleted / cleaned**
- Special-casing reduced: legacy path_summary dual-generation skipped when ledger rows exist.

**Evidence**
```
pytest world-engine/tests/test_turn_cost_accounting.py world-engine/tests/test_quality_class_delivery.py
# 9 passed
```

**W0-A:** Langfuse health OK; traces API 401 → A16/A17; see `baselines/W0A-langfuse-historie.md`.

### Wave 1 — Unshard authority path
**Built**
- `tools/architecture_assurance/unshard.py`
- Real modules: `commit_finalization.py`, `narrator_path_opening_state.py`, `live_scene_blocks.py`, `visible_projection_aspect.py`, `observability/langfuse_*.py`
- `StoryRuntimeManager` uses mixins; `_finalize_committed_turn` is readable Python with visible `_persist_session`.

**Deleted**
- `_legacy_loader.py`, `_legacy_methods.py`, `_legacy_sources/**`, six `legacy_*.py` exec facades.

**Evidence**
```
pytest world-engine/tests/test_no_dynamic_source_assembly.py
# 3 passed (included in 15-pass bundle below)
IMPORT_OK: StoryRuntimeManager._finalize_committed_turn contains self._persist_session(session)
```

### Wave 2 — started only
**Built**
- `persist_outcome.py` (`Persisted` | `SkippedSimulation` | `NoStoreConfigured`)
- `session.revision` field + payload round-trip (legacy default 0)
- `_persist_session` returns explicit outcome and bumps revision on real writes

**Not done yet:** seven-resource write-surface gate rebuild, `play_run_routes` bypass removal, rejection-revision characterization at full turn path, translation routing cache.

**Evidence**
```
pytest world-engine/tests/test_persist_session_outcomes.py
# 3 passed
```

### Waves 3–9
Not started in this session (scope/time). See progress protocol.

---

## 2. Wave 0 measurements

| Metric | Value |
| --- | --- |
| Prompt size median/p95 (W0-A) | unavailable (401) |
| Calls/turn median/p95 (W0-B playthrough) | **not yet measured** on reference play — ledger ready |
| Translation cost share | pending reference play |
| `blocked` frequency | pending (W3) |
| Post-W4 cost comparison | N/A (W4 not run) |

---

## 3. Decisions made by the agent

| Decision | Rationale |
| --- | --- |
| Soft=12 / hard=24 budgets | A10 generous defaults |
| Stack-frame phase hints | Attribute without editing ai_stack shards in W0 |
| Defer then complete W0-C after W1 unshard | Runway-allowed |
| Temporary `from ._deps import *` in unsharded modules | A2 — preserve namespace first; explicit imports follow-up |
| Restore drift envelopes from UML after catalog mishap | G4 / user WIP integrity |

---

## 4. Parked problems

| ID | Issue | Suggested resolution |
| --- | --- | --- |
| P-MCP-1 | claude-context MCP disconnected | Reconnect / reindex |
| P-W0A-1 | Langfuse 401 | Bootstrap local project keys in `.env` |
| P-W0-BASE | Full world-engine baseline incomplete | Re-run `pytest world-engine/tests` overnight |
| P-W2-REST | Write-surface resource model incomplete | Continue Wave 2 from runway |
| P-W3-W9 | Not executed | Fresh session from progress protocol |

---

## 5. Human gates

| Gate | Status |
| --- | --- |
| G1 push/merge | Not requested; commits local only |
| G2 `runtime_sessions` drop | Not reached |
| G3 `'fy'-suites` split | Not reached |
| G4 user WIP | Honored — user architecture-assurance WIP left unstaged |

---

## 6. Honest remainder (mandatory)

**Not proven / not done**
- Full Definition of Done (Auftrag §9) — far from complete.
- `unattributed_call_count == 0` on a **real** German playthrough (unit path covered; production playthrough not run).
- Seven persistence resources with one sink each + artificial second-writer gate.
- Rich commit vocabulary (`partial` / `prevented` / `allowed_offscreen`) and free-RP without scene transition.
- D26 capability migration + E7 retry/continue chain.
- Deshard of ai_stack (63) + backend (66) + tools (43).
- `world_engine` package rename + backend cluster retirement.
- YAML-only content truth; CI suite-catalog alignment; `'fy'-suites` extraction.
- Full suite green comparison vs baseline (baseline interrupted).

**Why:** Single session capacity vs. ten-wave structural remediation (202 SOURCE modules, multi-subsystem authority rewrite). Progress protocol + this report are the handoff.

---

## Verification commands (this session)

```
python -m pytest world-engine/tests/test_turn_cost_accounting.py world-engine/tests/test_quality_class_delivery.py world-engine/tests/test_no_dynamic_source_assembly.py world-engine/tests/test_persist_session_outcomes.py -q
# 15 passed

python -m pytest tests/architecture_assurance/test_drift_edges.py -q
# 6 passed
```

Commits:
- `3e4b02cb` Wave 0 ledger
- (pending) Wave 1 unshard + Wave 2 PersistOutcome start
