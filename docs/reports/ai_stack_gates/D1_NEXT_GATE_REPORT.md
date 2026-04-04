# D1-next Gate Report — Writers-Room workflow suite maturity

Date: 2026-04-04

## 1. Scope completed

- Made `workflow_stages` the ordered list of stage ids derived from `workflow_manifest.stages` (single source of truth), including `retrieval_bridge_preview` before `human_review_pending`.
- Deepened packaged artifacts: `proposal_package` now includes `retrieval_digest` (hit count, evidence tier/strength, top paths, short context fingerprint), `langchain_preview_paths` (material bridge output), and `governance_readiness` (checklist + counts, no new publish paths).
- Enriched `issues`, `patch_candidates`, and `variant_candidates` with explicit `evidence_tier`, `confidence_kind`, linkage fields, and short rationales where appropriate.
- Extended `review_summary` with `evidence_strength`, `model_output_descriptor`, and a structured `review_checkpoint` separating retrieval strength from model-output semantics.
- Implemented an explicit revision cycle: `POST /api/v1/writers-room/reviews/<review_id>/revision-submit` (JWT) when `review_state.status == pending_revision`, re-running the same pipeline, appending `revision_cycles[]` with a `prior_snapshot` of key artifacts, then returning the review to `pending_human_review`.

## 2. Files changed

- `backend/app/services/writers_room_service.py`
- `backend/app/api/v1/writers_room_routes.py`
- `backend/tests/test_writers_room_routes.py`
- `docs/reports/ai_stack_gates/D1_NEXT_GATE_REPORT.md`

## 3. What was deepened versus what already existed

- **Already existed:** End-to-end Writers-Room flow with `wos.context_pack.build`, model generation, `wos.review_bundle.build` via tool bridge, LangChain retriever preview on the response, persisted reviews, HITL `accept` / `reject` / `revise`.
- **Deepened:** Artifact fidelity for governance handoff, explicit alignment between manifest and `workflow_stages`, LangChain preview paths copied into `proposal_package`, and a **second-pass workflow** after `revise` instead of only a status flag.

## 4. Workflow stages that became more explicit or stronger

- `workflow_stages` now mirrors `workflow_manifest.stages` exactly (test-enforced).
- `revision-submit` adds a durable `revision_cycles` record with a snapshot of the prior package for audit/diff-oriented review.

## 5. Artifact types that became more production-useful

- `proposal_package`: retrieval digest + preview paths + governance readiness checklist.
- `patch_candidates`: `review_bundle_id` anchor, `confidence_kind`, `evidence_tier`, `linked_source_path`, `rationale`.
- `variant_candidates`: `evidence_anchor`, `confidence` / `confidence_kind`, `revision_sensitivity`.
- `review_summary`: `review_checkpoint` and explicit separation hints between evidence strength and model output class.

## 6. Where retrieval / tool usage became more material

- **Retrieval:** Still drives issues, patch targets, and `retrieval_digest` / fingerprint in `proposal_package` (existing materiality tests preserved; strengthened metadata expectations).
- **Review bundle tool:** Bundle id continues to flow into `review_summary` and now into each `patch_candidates[]` entry.
- **LangChain retriever bridge:** Preview source paths are duplicated into `proposal_package.langchain_preview_paths` so the bridge is not only a sidecar field on the HTTP payload.

## 7. What remains intentionally lightweight

- No automatic patch application or diff engine; patch entries remain **hints** for human editors.
- LangGraph depth remains a seed graph stub; orchestration is not expanded.
- No export to external review tools; administration/governance remains the authority for publishing.

## 8. Tests added / updated

- Updated unified-stack test to assert manifest/`workflow_stages` parity and new summary/proposal fields.
- Extended patch-candidate assertions for governance anchor and confidence kind.
- Added: LangChain preview paths materialized in `proposal_package`.
- Added: revision-submit appends `revision_cycles`, preserves prior snapshot, refreshes artifacts; rejection when not `pending_revision`.

## 9. Exact test commands run

```text
cd backend
python -m pytest tests/test_writers_room_routes.py -v --tb=short
```

Note: `backend/pyproject.toml` enables coverage reporting by default for this project’s pytest configuration; the run completed with exit code **0** and **14 passed** on Windows (Python 3.13.12).

## 10. Verdict

**Pass**

## 11. Reason for verdict

- Writers-Room is **materially** stronger for workflow use than before: revision is an executable cycle with persisted history, artifacts carry clearer governance-oriented metadata, and retrieval plus LangChain preview influence is **test-proven** on packaged outputs.
- The implementation does **not** claim full editorial-suite or production-hardened autonomy; remaining gaps are stated above.

## 12. Remaining risk

- Real corpus sparsity can still yield empty `patch_candidates` when no retrieval sources return; behavior is honest but operationally thin for some modules.
- Revision re-runs duplicate full pipeline cost; no incremental partial recompute.
