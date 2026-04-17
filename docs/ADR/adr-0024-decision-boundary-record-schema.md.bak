# ADR-0024: Decision Boundary Record — minimum schema for decision boundary recording

Date: 2026-04-17

Status: Accepted

## Context

The `ROADMAP_MVP_GoC.md` documents a set of minimum fields for runtime records including a Decision Boundary Record. Capturing decision boundary metadata consistently supports auditability and governance.

## Decision

- Standardize a `Decision Boundary Record` with the following minimum fields:
  - `decision_name`
  - `decision_class`
  - `owner_layer`
  - `input_seam_ref`
  - `chosen_path`
  - `validation_result`
  - `failure_seam_used`
  - `notes_code`

- Ensure runtime and governance layers emit this record when a decision boundary is crossed.

## Rationale

- Provides structured metadata for post-hoc review, auditing, and reproducible validation of decisions taken during execution.
- Enables consistent tooling for analysis, reporting, and governance workflows.

## Consequences

- Instrumentation work required in runtime components to populate the record.
- Downstream storage, retrieval, and reporting should include these fields for governance views.

## Migrated from

`docs/MVPs/MVP_VSL_And_GoC_Contracts/ROADMAP_MVP_GoC.md` ("Decision Boundary Record")

---

(Automated migration entry created 2026-04-17)
