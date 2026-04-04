# D1 Gate Report — Writers-Room Human-in-the-Loop Production Workflow

Date: 2026-04-04

## Scope completed

- Added explicit **`workflow_manifest`** with ordered **`stages`** (timestamps + optional `artifact_key`) covering intake through human review pending.
- Added structured **`review_summary`** (issue/recommendation counts, evidence tier, retrieval hit count, governance bundle id/status, top issue ids, proposal/comment bundle ids).
- Aligned **`outputs_are_recommendations_only`** to **`true`** (advisory / no auto-publish).
- Extended HITL **`POST .../decision`** to support **`revise`** (non-terminal `pending_revision`) in addition to **`accept`** / **`reject`**, with history entries and **`last_hitl_action`** on revise.
- Kept canonical stack: LangGraph seed, **`wos.context_pack.build`**, LangChain generation bridge, **`wos.review_bundle.build`** tool bridge, LangChain retriever preview.
- Surfaced workflow summary fields in the **writers-room** Flask template (secondary UX).
- Updated architecture doc stage list and decision API note.

## Files changed

- `backend/app/services/writers_room_service.py`
- `backend/tests/test_writers_room_routes.py`
- `writers-room/app/templates/index.html`
- `docs/architecture/writers_room_on_unified_stack.md`
- `docs/reports/ai_stack_gates/D1_GATE_REPORT.md`
- `CHANGELOG.md` (single-line correction for `outputs_are_recommendations_only` semantics)

## What was deepened versus what already existed

- **Already existed**: unified POST review, persistence, proposal/comment/patch/variant artifacts, retrieval + review bundle wiring, accept/reject.
- **Deepened**: explicit stage manifest; first-class review summary; recommendation-only flag aligned with governance docs; **revise** loop; tests that prove retrieval and review-bundle outputs **materially** change persisted artifacts; stricter invalid/finalized decision handling.

## Workflow stages now explicit

| Stage id | Role |
|----------|------|
| `request_intake` | Request accepted |
| `workflow_seed` | LangGraph seed graph |
| `retrieval_analysis` | `wos.context_pack.build` |
| `proposal_generation` | Model routing + generation / fallback |
| `artifact_packaging` | Proposal + comment + patch + variant artifacts |
| `governance_envelope` | `wos.review_bundle.build` |
| `retrieval_bridge_preview` | LangChain retriever preview |
| `human_review_pending` | Initial HITL state |

HITL transitions (after create): **`pending_human_review`** or **`pending_revision`** → **`accept`** / **`reject`** (terminal); **`revise`** → **`pending_revision`** (repeatable).

## Artifact types truly produced

- **`workflow_manifest`**, **`review_summary`**, **`proposal_package`**, **`comment_bundle`**, **`patch_candidates`**, **`variant_candidates`**, **`review_bundle`**, **`review_state`** (+ **`last_hitl_action`** on revise).
- **`human_decision`** only on terminal accept/reject.

## Where retrieval / tool usage is truly involved

- **Retrieval**: `wos.context_pack.build` drives `issues`, `evidence_sources`, and proposal linkage; **route test** swaps controlled context-pack sources and asserts different **`proposal_package.evidence_sources`** and issue **`evidence_source`**.
- **Tool / capability**: `wos.review_bundle.build` (via tool bridge) supplies **`bundle_id`** / **`status`** reflected in **`review_summary`** and response **`review_bundle`**; **route test** varies mocked bundle ids and asserts **`review_summary.bundle_id`** tracks the tool output.
- **LangChain**: generation bridge and retriever preview unchanged; primary path remains structured where the adapter supports it.

## What remains chat-like or intentionally lightweight

- **Legacy oracle** route in the writers-room app remains transitional chat-style (explicitly secondary).
- **Model generation** content may still be prose-heavy when adapters fall back to raw/mock output; workflow shape and artifacts are not chat-only.
- **LangGraph** seed graph remains a thin anchor (not a full multi-node dramaturgy graph).

## Tests added / updated

- Updated unified-flow assertions for **`outputs_are_recommendations_only`**, **`workflow_manifest`**, **`review_summary`**.
- **`test_writers_room_retrieval_sources_materially_change_proposal_artifacts`**
- **`test_writers_room_review_bundle_tool_output_in_review_summary`**
- **`test_writers_room_revise_then_accept_hitl_loop`**
- **`test_writers_room_invalid_decision_rejected`** (parametrized)
- **`test_writers_room_cannot_finalize_twice`**
- Extended **`test_writers_room_review_state_transition_and_fetch`** for decision in history.

## Exact test commands run

```powershell
cd backend
python -m pytest tests/test_writers_room_routes.py -v --tb=short
```

Result: **11 passed**, exit code **0** (Windows, Python 3.13.12).

## Verdict

**Pass**

## Reason for verdict

- Primary path is **workflow-shaped** with explicit stages, structured artifacts, and persisted review files.
- **HITL** is **test-covered** including **revise** and terminal **accept**/**reject** rules.
- **Retrieval** and **review-bundle tool** effects are **proven** by controlled-workflow tests (not cosmetic).
- **Recommendation-only** semantics are explicit in the API contract.

## Remaining risk

- File-backed review storage is local; concurrent writers to the same `review_id` are not transactionally isolated.
- Controlled tests bypass the default capability registry; regressions in the **default** registry wiring rely on the integration test path (`test_writers_room_review_runs_unified_stack_flow`).
