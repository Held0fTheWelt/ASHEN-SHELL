# Retirement Record (`MVP/` tree)

## Current Decision

**`MVP/` is retained** in the workspace as the intake snapshot and evidence baseline. It has **not** been removed.

This matches the explicit **operator decision** recorded in repository-root [`Task.md`](../../../Task.md): retention for auditability and future diffs, not because integration failed.

## Phase 6 — Verification and deletion gate (2026-04-21)

Executed per [`Plan.md`](../../../Plan.md) Phase 6 (verification and deletion gate), without performing destructive removal:

| Gate / check | Outcome |
|---|---|
| Mapping-table verification | **Pass** — `python scripts/mvp_verify_mapping_table.py --repo-root <repo>` refreshed statuses for **27,890** rows; see [`mapping_verification_report.md`](./mapping_verification_report.md). Follow-up buckets remain triaged per [`PHASE_3_FINAL_RECONCILIATION_CLOSURE.md`](./PHASE_3_FINAL_RECONCILIATION_CLOSURE.md) and class-level closure in [`mapping_closure_decisions.md`](./mapping_closure_decisions.md). |
| Byte reconcile (compared domains) | **Pass** — `python scripts/mvp_reconcile.py` → **1683** reconciliation rows, **0** conflicts after excluding local **`.wos/`** persistence (RAG corpus under `backend/.wos/rag/` is runtime state, not shipped source; see [`scripts/mvp_reconcile.py`](../../../scripts/mvp_reconcile.py) `SKIP_SNIPPETS`). [`integration_conflict_register.md`](./integration_conflict_register.md) has no `CON-*` data rows. |
| Runtime / tests (active tree) | **Partial with documented waiver for `backend` full suite** — smoke `python -m pytest backend/tests/test_app_init.py -q` → **4 passed** (2026-04-21 session). Other domains unchanged vs [`domain_validation_matrix.md`](./domain_validation_matrix.md) prior **pass** entries. |
| Canonical docs + navigation | **Pass** — primary doc entrypoints do not require raw `MVP/` URLs; canonical bundle is the operator path (see [`navigation_update_record.md`](./navigation_update_record.md)). |
| Evidence traceability | **Pass (bundle posture)** — implementation-grade bundle docs remain the canonical narrative; no Phase 6 change to claims. |
| Destructive deletion of `MVP/` | **Not executed** — not required for success criteria while retention is the recorded decision; Plan deletion gate is **not invoked** for removal. |

## Why `MVP/` Was Not Deleted (even though integration is complete)

- **Policy:** [`Plan.md`](../../../Plan.md) allows retirement only when every gate passes **and** stakeholders choose removal. The project instead **signed retention** (see `Task.md`).
- **Practical:** `MVP/` remains a **byte-comparable snapshot** and inventory anchor; cost is low; value for audits and future intake refresh is high.

## If Destructive Retirement Is Revisited Later

- Re-run **`python tools/mvp_reintegration_intake.py`** after any `MVP/` tree change; align `source_baseline_lock.txt`.
- Re-run **`python scripts/mvp_reconcile.py`**; resolve any new `CON-*` rows (or extend documented skips only for true non-source noise).
- Re-run **`python scripts/mvp_verify_mapping_table.py`** until follow-up posture matches the then-current policy.
- Optionally complete **full** `backend` suite in CI or locally if a stricter deletion-only gate is adopted.
- Confirm navigation still has no **required** dependency on raw `MVP/` paths.

## Legacy Remainder

The full `MVP/` directory remains available for diff-backed reconciliation and optional future intake refreshes.
