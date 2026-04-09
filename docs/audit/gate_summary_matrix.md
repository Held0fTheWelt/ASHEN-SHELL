# Gate Summary Matrix (GoC Baseline Audit)

Dual-status model per `docs/ROADMAP_MVP_GoC.md` §11.1 and `docs/GoC_Gate_Baseline_Audit_Plan.md`: each gate has **structural_status** and **closure_level_status**. This matrix summarizes the baseline captured in per-gate reports under `docs/audit/`.

| Gate | structural_status | closure_level_status | evidence_quality | Per-gate report |
|------|-------------------|----------------------|------------------|-----------------|
| G1 Shared Semantic Contract | `yellow` | `level_a_capable` | `medium` | [gate_G1_semantic_contract_baseline.md](gate_G1_semantic_contract_baseline.md) |
| G2 Capability / Policy / Observation | `yellow` | `level_a_capable` | `medium` | [gate_G2_capability_policy_observation_baseline.md](gate_G2_capability_policy_observation_baseline.md) |
| G3 Canonical Dramatic Turn Record | `yellow` | `level_a_capable` | `medium` | [gate_G3_turn_record_baseline.md](gate_G3_turn_record_baseline.md) |
| G4 Scene Direction Boundary | `yellow` | `level_a_capable` | `medium` | [gate_G4_scene_direction_boundary_baseline.md](gate_G4_scene_direction_boundary_baseline.md) |
| G5 Retrieval Governance | `yellow` | `level_a_capable` | `medium` | [gate_G5_retrieval_governance_baseline.md](gate_G5_retrieval_governance_baseline.md) |
| G6 Admin Governance | `yellow` | `level_a_capable` | `medium` | [gate_G6_admin_governance_baseline.md](gate_G6_admin_governance_baseline.md) |
| G7 Writers' Room Operating | `green` | `level_a_capable` | `high` | [gate_G7_writers_room_operating_baseline.md](gate_G7_writers_room_operating_baseline.md) |
| G8 Improvement Path Operating | `green` | `level_a_capable` | `high` | [gate_G8_improvement_operating_baseline.md](gate_G8_improvement_operating_baseline.md) |
| G9 Experience Acceptance | `green` | `level_a_capable` | `high` | [gate_G9_experience_acceptance_baseline.md](gate_G9_experience_acceptance_baseline.md) |
| G9B Evaluator Independence | `green` | `level_a_capable` | `high` | [gate_G9B_evaluator_independence_baseline.md](gate_G9B_evaluator_independence_baseline.md) |
| G10 End-to-End Closure | `green` | `none` | `high` | [gate_G10_end_to_end_closure_baseline.md](gate_G10_end_to_end_closure_baseline.md) |

## Notes

- **Structural `green`:** G7, G8, **G9**, **G9B**, **G10** (operational + evaluative + integrative where evidenced). **G9** is structural `green` on authoritative run `g9_level_a_fullsix_20260410` (complete six-scenario pytest witness, capture, 6×5 matrix, validator `pass_all: true` — see `gate_G9_experience_acceptance_baseline.md`). **G9B** is structural `green` for evaluator-discipline artifacts on the **same** `audit_run_id`: separate Evaluator A and B matrices, raw sheet pointers, and full `g9b_score_delta_record.json` from frozen matrices (current B pass: `evaluator_b_claude_system_20260409`, ingested strict-blind handoff return; delta recomputed); manifest `evaluator_mode_declared` = `level_b_attempt_insufficient_independence`; **`closure_level_status` stays `level_a_capable`** — `level_b_attempt_status` = `failed_insufficient_independence` (`g9b_level_b_attempt_record.json`); `level_b_capable` requires evidentiary independence (process, authorship, separate score generation), not merely two files plus deltas. **G10** is structural `green` on integrated backend trio `g10_backend_e2e_20260409` (15 passed, `exit_code: 0`) plus step 11 on that same authoritative G9 bundle — see `gate_G10_end_to_end_closure_baseline.md`. G1–G6 remain structural `yellow` unless their per-gate report states otherwise.
- **`closure_level_status` and program closure:** Per-gate `level_a_capable` on G1–G9B does **not** aggregate to “Level A program closure achieved” (`docs/GoC_Gate_Baseline_Audit_Plan.md` §7A). **G10** remains `closure_level_status: none` (prerequisite gate health G1–G6 still `yellow`; §7A rule 3 read with G10 §H — see `gate_G10_end_to_end_closure_baseline.md`); global program closure is still not supported (`docs/audit/closure_level_classification_summary.md`).
- **G9B** is listed after G9; ordering follows audit dependency (`docs/GoC_Gate_Baseline_Audit_Plan.md` §5).
- Operational gates G7/G8 use `structural_status` for operational sufficiency per their baseline notes—not G1–G6 static-only semantics.
