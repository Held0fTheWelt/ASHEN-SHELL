# Red / Yellow Remediation List (Baseline Backlog)

Grouped by **implementation order** aligned with `docs/GoC_Gate_Baseline_Audit_Plan.md` §6 and roadmap structural dependencies. Items are **evidence and contract gaps** identified in per-gate baselines—**not** implemented fixes.

This document is **not** a closure claim.

---

## Tier 0 — Phase 0 / mapping hygiene

| ID | Source gate(s) | Remediation target |
|----|----------------|-------------------|
| T0-1 | Phase 0 (Task 1 scope note) | Extend canonical-to-repo mapping beyond G1–G6 scope where later gates need frozen command inventories (grep patterns, module sets). See `docs/audit/canonical_to_repo_mapping_table.md` scope statement. |

---

## Tier 1 — Shared semantic contract + module + turn substrate (steps 1–2, 5)

| ID | Source gate(s) | Remediation target |
|----|----------------|-------------------|
| T1-1 | G1 | Map roadmap equality set names to code; run `python -m pytest ai_stack/tests/test_goc_frozen_vocab.py`; prove admin semantic lists are canonical-derived. |
| T1-2 | G3 | Execute `ai_stack/tests/test_goc_phase1_runtime_gate.py` (and frozen module set); capture runtime samples for full section/field parity vs `docs/CANONICAL_TURN_CONTRACT_GOC.md`. |
| T1-3 | G3 | Verify compact/expanded projection parity with runtime traces. |

---

## Tier 2 — Capability / policy / observation + scene direction (steps 3–4)

| ID | Source gate(s) | Remediation target |
|----|----------------|-------------------|
| T2-1 | G2 | Execute `cd backend && python -m pytest tests/runtime/test_model_routing_evidence.py tests/runtime/test_decision_policy.py -q --tb=short --no-cov`; attach outputs; capture live policy/version identity in routing traces. |
| T2-2 | G4 | Produce explicit subdecision matrix traceability artifact (or equivalent enumerated mapping) linked to `scene_director_goc.py`. |
| T2-3 | G4 | Execute `ai_stack/tests/test_goc_phase1_runtime_gate.py`, `ai_stack/tests/test_goc_phase2_scenarios.py`; attach bounded-behavior evidence. |

---

## Tier 3 — Retrieval governance + admin boundaries (steps 6–7)

| ID | Source gate(s) | Remediation target |
|----|----------------|-------------------|
| T3-1 | G5 | Execute `python -m pytest ai_stack/tests/test_rag.py` and `ai_stack/tests/test_goc_phase4_reliability_breadth_operator.py`; freeze retrieval scenario module scope per plan. |
| T3-2 | G5 | Capture runtime turn-level retrieval governance visibility traces. |
| T3-3 | G6 | Execute `cd backend && python -m pytest tests/test_game_admin_routes.py tests/test_admin_security.py -q --tb=short --no-cov`; extend proof for semantic-authoring boundary on all admin write paths. |
| T3-4 | G6 | Run `python -m pytest tests/smoke/test_admin_startup.py` in controlled environment if used as governance smoke. |

---

## Tier 4 — Writers' Room + Improvement operating contracts (steps 8–9)

| ID | Source gate(s) | Remediation target |
|----|----------------|-------------------|
| T4-1 | G7 | **Addressed (repo):** explicit `artifact_class` + roadmap §7.3 metadata on governed Writers' Room outputs; `test_writers_room_g7_operating_contract.py`; CI job `writers-room-g7-contract-tests`. T4-2 remains for adjacent surfaces. |
| T4-2 | G7 | Re-verify recommendation-only posture on adjacent publication/mutation surfaces. |
| T4-3 | G8 | **Addressed (repo):** `ImprovementEntryClass`, strict parsing, API/service tests; see `gate_G8_improvement_operating_baseline.md` and `tests/improvement/`. |
| T4-4 | G8 | **Addressed (repo):** `publication_verification_trace` + `post_change_verification` + `improvement_loop_progress`; see `improvement_service.apply_improvement_recommendation_decision` and G8 baseline. |

---

## Tier 5 — Experience acceptance + evaluator independence (step 10 roadmap slice / G9–G9B)

| ID | Source gate(s) | Remediation target |
|----|----------------|-------------------|
| T5-1 | G9 | Produce human 1–5 score matrix for all six roadmap scenarios with per-cell rationale; store as auditable artifacts. |
| T5-2 | G9 | Recompute §6.9 thresholds; document arithmetic. |
| T5-3 | G9 | **Addressed (repo):** explicit `test_goc_retrieval_heavy_scenario.py` + frozen `goc_roadmap_s6_retrieval_heavy` in `ai_stack/goc_g9_roadmap_scenarios.py` and G9 template. |
| T5-4 | G9 | Refresh `tests/reports/GOC_PHASE*.md` if scenario tables drift from tests. |
| T5-5 | G9B | Archive immutable raw evaluator sheets for the same run as G9; complete Level A package. |
| T5-6 | G9B | For Level B: second independent evaluator, preserved deltas, non-supplanting reconciliation discipline. |

---

## Tier 6 — End-to-end closure re-audit (step 11 / G10)

| ID | Source gate(s) | Remediation target |
|----|----------------|-------------------|
| T6-1 | G10 | **Addressed (repo witness):** trio executed with `backend/requirements-dev.txt`; transcript `tests/reports/evidence/g10_backend_e2e_20260409/pytest_g10_backend_trio.txt` (**15 passed**, `exit_code: 0`); `run_metadata.json` records command and Python version. First capture used `PYTHONPATH` = repo root; cwd-only from `backend/` also passed on re-verify — see `gate_G10_end_to_end_closure_baseline.md`. **CI parity:** Actions uses Python 3.10; re-run locally on 3.10 if merge-bar equivalence is the claim under test. **CI:** job `g10-backend-e2e-evidence-path` runs the same trio after `pip install -r backend/requirements-dev.txt`. |
| T6-2 | G10 | Optionally run root smoke suite / `run-smoke-tests.*` per audit plan; record results. |
| T6-3 | G10 | **Partially addressed:** eleven-step table and structural status updated in `gate_G10_end_to_end_closure_baseline.md`; `closure_level_status` remains `none` per §7A prerequisite gate health (G1–G6 `yellow`) read with G10 §H — revisit when Tier 1–5 structural movement supports promotion. |

---

## Severity legend (baseline-only)

- **Structural `yellow`:** partial evidence—closure not ready per plan §8.  
- **Structural `red`:** not present in this baseline matrix (no gate reported `red`).  
- **closure_level `none` on G10 (and global aggregation):** blocks program-level closure classification even when G9/G9B carry `level_a_capable` on authoritative evaluative evidence (`docs/audit/closure_level_classification_summary.md`).
