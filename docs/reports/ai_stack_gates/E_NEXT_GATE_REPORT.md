# E-next Gate Report — Audit, operations, governance, and release truthfulness

Date: 2026-04-04

## 1. Scope completed

- Tightened **Writers-Room retrieval readiness**: `writers_room_retrieval_evidence_surface` is `ready` only when the latest review’s `retrieval_trace.evidence_tier` is **`moderate` or `strong`** (no longer satisfied by `none`/`weak` tiers merely being present).
- Added **improvement retrieval backing** area: `improvement_retrieval_evidence_backing` is `partial` when the latest package’s `evidence_strength_map.retrieval_context` is **`none`**, even if comparison + `governance_review_bundle_id` exist.
- Fixed **latest improvement package selection**: chooses the package with the greatest **`generated_at`** ISO timestamp instead of relying on lexicographic filename order from `list_json`.
- Enriched **session evidence** with **`cross_layer_classifiers`** (explicit committed-vs-diagnostic note, last-turn presence, graph posture, retrieval tier class, tool influence, bridge reachability, degradation markers).
- Extended **reproducibility_metadata** with retrieval fingerprint fields from the last turn when available.
- Surfaced **`evidence_strength_map`** on **`repaired_layer_signals.improvement.evidence_influence`** and added **`review_readiness`** under Writers-Room signals.
- Extended **`build_release_readiness_report`** with per-area **`evidence_posture`**, top-level **`decision_support`**, and **`known_environment_sensitivities`**.
- **Administration-tool** governance page: load **`release-readiness`**, show a short **text summary** derived from the same JSON plus full JSON output (no separate scoring service).

## 2. Files changed

- `backend/app/services/ai_stack_evidence_service.py`
- `backend/tests/test_m11_ai_stack_observability.py`
- `administration-tool/static/manage_ai_stack_governance.js`
- `administration-tool/templates/manage/ai_stack_governance.html`
- `administration-tool/tests/test_manage_game_routes.py`
- `docs/architecture/observability_and_governance_in_world_of_shadows.md`
- `docs/reports/ai_stack_gates/E_NEXT_GATE_REPORT.md` (this file)
- `docs/reports/AI_STACK_MATURITY_CLOSURE.md`

## 3. What was deepened versus what already existed

- **Already existed:** Session evidence bundle, `execution_truth`, degraded signals, `repaired_layer_signals`, release-readiness areas, governance routes, admin JSON loaders for session evidence and improvement packages, E1 honesty constraints.
- **Deepened:** Stricter tier rules for WR and improvement retrieval, truthful “latest package” selection, explicit cross-layer classifiers for operators, richer release payload for decision support, admin surfacing of release-readiness.

## 4. Stronger audit / evidence distinctions

- **Committed vs diagnostic:** `cross_layer_classifiers.committed_vs_diagnostic` states authority split; `committed_narrative_surface` unchanged as authoritative committed view.
- **Graph primary vs fallback/degraded:** `cross_layer_classifiers.graph_execution_posture` and existing `last_turn_graph_mode` / `degraded_path_signals`.
- **Retrieval-backed vs weak:** WR area requires moderate/strong; improvement backing area requires non-`none` `retrieval_context` in `evidence_strength_map`; runtime tier in classifiers.
- **Tool-influenced vs plain:** `cross_layer_classifiers.tool_influenced_last_turn` and `tool_influence.material_influence`.
- **Review-ready vs partial:** `review_readiness` on Writers-Room signals; `decision_support` booleans for retrieval-graded review readiness.

## 5. Governance / admin surfaces

- Release-readiness **summary** (overall, decision_support lines, per-area status + posture, partiality and environment sensitivities) plus raw JSON in the administration-tool governance page.
- API consumers get structured **`evidence_posture`** and **`decision_support`** without replacing existing endpoints.

## 6. Stricter release-readiness logic

- Additional area **`improvement_retrieval_evidence_backing`**; stricter WR retrieval tier rule; explicit environment sensitivity list for local artifact layout and timestamp parsing.
- **`overall_status`** remains `partial` whenever any area is not `ready` (expected in typical dev/sparse artifact environments).

## 7. What remains partial

- Aggregate release report still does not substitute for **session-scoped** `execution_truth` (`story_runtime_cross_layer` stays `partial`).
- Writers-Room **LangGraph** depth remains a **seed stub** (`writers_room_langgraph_orchestration_depth` partial).
- **Local JSON** persistence, no signed immutable audit store.

## 8. What remains intentionally lightweight / local

- Admin UI: minimal buttons and preformatted text; no external monitoring stack.
- Artifact stores under `var/` (writers-room, improvement) remain **local** and layout-sensitive.

## 9. Tests added or updated

- `test_admin_session_evidence_returns_runtime_bundle` — `cross_layer_classifiers`, reproducibility retrieval keys.
- `test_session_evidence_includes_repaired_layer_signals` — `review_readiness`, `evidence_strength_map` on improvement influence.
- `test_session_evidence_surfaces_degraded_execution_health` — cross-layer posture + degradation markers.
- `test_session_evidence_empty_diagnostics_surfaces_no_turn_cross_layer`
- `test_latest_improvement_package_selects_newest_generated_at`
- `test_release_readiness_sparse_env_does_not_claim_ready` — new area and `decision_support` / sensitivities.
- `test_release_readiness_writers_room_weak_retrieval_is_not_ready`
- `test_release_readiness_improvement_weak_retrieval_backing_is_partial`
- `test_manage_ai_stack_governance_renders_template` — release-readiness UI markers.

## 10. Exact test commands run

```text
cd backend
python -m pytest tests/test_m11_ai_stack_observability.py -v --tb=short
```

```text
cd administration-tool
python -m pytest tests/test_manage_game_routes.py::test_manage_ai_stack_governance_renders_template -v --tb=short
```

Host: Windows, Python 3.13.12. Outcome: all of the above passed.

## 11. Verdict

**Pass**

## 12. Reason for verdict

Audit and governance payloads are **materially more discriminating** (tier rules, backing area, classifiers, latest-package fix), admin surfaces expose **release-readiness** with honest summary text, and tests **prove** weak retrieval and empty diagnostics visibility. Reports do not claim universal production readiness; aggregate `partial` remains normal.

## 13. Remaining risk

Operators may still misread **`overall_status`** without reading per-area rows; session evidence remains required for live runtime truth. Timestamp-based package selection assumes **parseable `generated_at`** on packages.
