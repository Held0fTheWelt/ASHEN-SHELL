# Area 2 — Runtime ranking stage closure report

This report records **Area 2 Closure Task 1 — Runtime Ranking Closure**: a first-class **`ranking`** stage between **signal / consistency** and **synthesis** in the canonical staged Runtime pipeline (`backend/app/runtime/runtime_ai_stages.py`).

**Explicit unchanged semantics:** Task 2A **`route_model` policy precedence and routing semantics**, the **`StoryAIAdapter` contract**, **guard legality**, **commit semantics**, **reject semantics**, and **authoritative Runtime mutation rules** in `execute_turn` were **not** changed — only staged orchestration, bounded stage contracts, traces, rollups, tests, and architecture text were extended.

---

## Binding ranking-stage interpretation

| Topic | Definition |
|-------|------------|
| **What ranking does** | After signal / consistency, **narrows or ranks candidate interpretations** (bounded hypotheses, confidence, ambiguity residual) and **refines whether LLM synthesis** should run, subject to deterministic merge rules. |
| **What ranking does not do** | It does **not** emit canonical story JSON (`scene_interpretation`, deltas, etc.); that remains **synthesis** (or deterministic SLM-only packaging). It does **not** replace signal’s repetition / consistency role. |
| **vs signal_consistency** | Signal answers **consistency / coarse `needs_llm_synthesis`**. Ranking **refines** the branch when the base gate still allows or requests synthesis; it does not re-validate signal fields. |
| **vs synthesis** | Synthesis is **generation** (`WorkflowPhase.generation`, narrative task kinds). Ranking is **interpretation** (`WorkflowPhase.interpretation`, `TaskKind.ranking`) with a **RankingStageOutput** contract only. |
| **Bounded output** | `RankingStageOutput` in code: capped string lists, scores in `[0, 1]`, `recommend_skip_synthesis` requires `skip_synthesis_after_ranking_reason` when true (Pydantic validation). |
| **Downstream orchestration** | `compute_synthesis_gate_after_ranking` merges **base signal gate** + **ranking outcome**. **Degraded policy:** ranking **parse failure** after a bounded call **forces synthesis** (`degraded_ranking_parse_forcing_synthesis`). Ranking **no-eligible** **falls back** to the base signal decision (`degraded_ranking_no_eligible_adapter_fallback_to_signal_gate`). Upstream **signal/preflight parse degradation** **ignores** ranking skip recommendations (synthesis still forced from the base reason). |
| **SLM-only path (binding)** | If `base_needs_llm` is **false** after signal: a **`ranking`** trace row is **always** recorded with the **intended** `build_ranking_routing_request` payload, **`decision: null`**, **`bounded_model_call: false`**, **`skip_reason: "ranking_not_required_signal_allows_slm_only"`**, and **`route_model` is not invoked**. |

---

## Gate outcomes (PASS/FAIL)

| Gate | Pass condition | Failure meaning | Result |
|------|----------------|-----------------|--------|
| **G-RANK-01** | `RuntimeStageId.ranking` exists and is used in traces | Ranking not a first-class stage | **PASS** (see `test_g_rank_01_stage_existence_gate`) |
| **G-RANK-02** | `RankingStageOutput` validates bounded payloads | Missing or placeholder-only contract | **PASS** (`test_g_rank_02_stage_contract_gate`) |
| **G-RANK-03** | Ranking routing uses `interpretation` + `TaskKind.ranking` | Ranking reuses signal/synthesis requests | **PASS** (`test_g_rank_03_stage_routing_gate`) |
| **G-RANK-04** | Ranked-skip, ranked-then-synthesis, and degraded ranking parse change outcomes | No material orchestration effect | **PASS** (`test_g_rank_04_orchestration_effect_gate` + `test_compute_synthesis_gate_after_ranking_no_eligible_fallback`) |
| **G-RANK-05** | Ranking in `runtime_stage_traces`, summary, audit timeline | Ranking invisible to operators | **PASS** (`test_g_rank_05_trace_and_audit_visibility_gate`) |
| **G-RANK-06** | SLM-only suppressed ranking + paths in G-RANK-04 / staged tests | Missing path coverage | **PASS** (`test_g_rank_06_*`) |
| **G-RANK-07** | Inventory + docs describe ranking | Documentation drift | **PASS** (`test_g_rank_07_documentation_truth_gate`) |
| **G-RANK-08** | `execute_turn` success on ranked-skip; guard outcome present | Authority regression | **PASS** (`test_g_rank_08_legacy_authority_safety_gate`) |

---

## Ranking-stage contract summary

- **Enum:** `RuntimeStageId.ranking` → `"ranking"`.
- **Model:** `RankingStageOutput` in `runtime_ai_stages.py` (`runtime_stage`, `ranked_hypotheses`, `preferred_hypothesis_index`, `recommend_skip_synthesis`, `skip_synthesis_after_ranking_reason`, `synthesis_recommended`, `ambiguity_residual`, `ranking_confidence`, `ranking_notes`).
- **Parser:** `parse_ranking_payload`.

---

## Stage routing summary

- **Builder:** `build_ranking_routing_request(session, extra_hints=...)` → `WorkflowPhase.interpretation`, `TaskKind.ranking`, `requires_structured_output=True`.
- **SLM-only:** No `route_model` for ranking; trace carries intended `request` JSON only (binding rule above).
- **Synthesis path:** `route_model(ranking_rr)` then bounded `generate` when an adapter is eligible.

---

## Orchestration-impact summary

- **Merge:** `compute_synthesis_gate_after_ranking` → `needs_llm` + `synthesis_gate_reason` + `ranking_effect`.
- **Final paths (additive):** `ranked_then_llm`, `ranked_slm_only`, `degraded_ranking_parse_forcing_synthesis`, `degraded_ranking_no_eligible_fallback` (see `OrchestrationFinalPath`).
- **SLM packaging:** `build_slm_only_structured_payload` may append ranking rationale when `ranking_skip_synthesis` applies.

---

## Trace, rollup, and audit summary

- **`runtime_stage_traces`:** One row per ranking execution path (suppressed, skipped no-eligible, bounded, or parse failure).
- **`runtime_orchestration_summary`:** `ranking_effect`, `ranking_bounded_model_call`, `ranking_suppressed_for_slm_only`, `ranking_no_eligible_adapter`.
- **`model_routing_trace`:** Additive `ranking_context`; `rollup_mode` **`slm_only_after_ranking_skip`** when synthesis skipped after a successful ranking route + bounded call; otherwise legacy modes preserved where applicable.
- **`operator_audit`:** Timeline includes `stage_key` **`ranking`** when traced.

---

## Tests run and results

From repository `backend/` as current working directory:

```text
python -m pytest tests/runtime/test_runtime_ranking_closure_gates.py tests/runtime/test_runtime_staged_orchestration.py tests/runtime/test_runtime_task4_hardening.py tests/runtime/test_area2_convergence_gates.py tests/runtime/test_area2_final_closure_gates.py tests/test_bootstrap_staged_runtime_integration.py tests/runtime/test_model_inventory_bootstrap.py tests/runtime/test_cross_surface_operator_audit_contract.py -q --tb=short --no-cov
```

Last verified: **60 passed**, **0 failed** (local run, `--no-cov`).

---

## Changed files (implementation)

- `backend/app/runtime/runtime_ai_stages.py`
- `backend/app/runtime/model_inventory_contract.py`
- `backend/app/runtime/ai_adapter.py` (`MockStoryAIAdapter` ranking payload)
- `backend/tests/runtime/test_runtime_staged_orchestration.py`
- `backend/tests/runtime/test_runtime_task4_hardening.py`
- `backend/tests/test_bootstrap_staged_runtime_integration.py`
- `backend/tests/runtime/test_runtime_ranking_closure_gates.py` (new)
- `docs/architecture/llm_slm_role_stratification.md`
- `docs/architecture/ai_story_contract.md`
- `docs/architecture/area2_runtime_ranking_closure_report.md` (this file)

---

## Residual risks

- **Registry coverage:** Staged tests and production operators must keep `AdapterModelSpec.supported_task_kinds` including **`ranking`** for interpretation-phase routing where the ranking stage should execute; otherwise honest `no_eligible_adapter_for_ranking_stage` degradation applies.
- **Rollup consumers:** New `ranking_context` and `slm_only_after_ranking_skip` are additive; legacy readers that ignore unknown keys remain safe.

---

## Cross-reference

- Inventory tuple: `RUNTIME_STAGED_REQUIRED` includes `(interpretation, ranking)`.
- Closure gates **G-RANK-01** … **G-RANK-08** are enforced in `backend/tests/runtime/test_runtime_ranking_closure_gates.py`.

**Routing policy (`route_model`) and authoritative Runtime semantics remain unchanged** aside from **invoking** additional stage-shaped `route_model` calls when the base synthesis gate is true, as documented above.
