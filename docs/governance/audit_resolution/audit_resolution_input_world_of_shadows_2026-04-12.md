# Audit resolution — case input (World of Shadows technical audit)

**Case id:** `world_of_shadows_technical_audit_2026-04-12`  
**Document type:** Case input only (no CAPA register, no closure status — see [audit_resolution_state_world_of_shadows.md](audit_resolution_state_world_of_shadows.md)).

---

## Audit source

- **Primary artifact:** External technical audit report (DOCX), narrative dated **2026-04-12**, title along the lines of *World of Shadows - Technical Audit Report* (runtime, content pipeline, persistence, fairness, live session integration).
- **Repository artifact referenced by audit:** Packaged snapshot cited as `ai_stack.zip` in report narrative (context only; not re-verified in this input file).

**Evidence tag:** `reported_not_independently_verified` for any table-only metrics in the DOCX if tables were not extracted into this repository.

---

## Scope (as stated in audit narrative)

- `content/modules/`
- `world-engine/`
- `backend/`
- `ai_stack/`
- `docs/`
- Selected tests

**Evidence tag:** `reported_not_independently_verified` for exact test counts unless reproduced in-repo.

---

## Extracted findings (audit labels)

Summarized from audit narrative. Detailed RCA, CAPA, and status live in the **state** document.

| Audit id | Severity (audit) | Short title |
|----------|------------------|-------------|
| C1 | Critical | Canonical content-to-commit seam / runtime projection scene identity mismatch at story commit resolver |
| H1 | High | Story-session state not durably persisted across process restart |
| H2 | High | Backend transitional runtime/session surface vs world-engine authority drift risk |
| H3 | High | Dual interpretation surfaces (compiled projection vs direct YAML guidance helpers) |
| M1 | Medium | Story-session concurrency semantics less explicit than live-run |
| M2 | Medium | Monorepo bootstrap / import hygiene (`app` package collision risk) |
| M3 | Medium | Content version pinning / provenance across runtime creation paths |
| L1 | Low | Test and resource hygiene rough edges |

---

## Key evidence claims (with classification)

| Claim | Classification | Notes |
|-------|----------------|-------|
| Narrative commit path must recognize scene rows from backend compiler shape | `verified` (in-repo after remediation) | World-engine accepts canonical keys per implementation; see state evidence index after CI |
| Compiler historically used one key shape and resolver another | `reported_not_independently_verified` | Asserted in audit narrative; treat as hypothesis until pinned to commit range |
| Story sessions held only in-process | `verified` | Confirmed by code review of world-engine story runtime manager prior to persistence work |
| DOCX table cells (severity summary, quality tables) | `blocked_missing_evidence` | Unless pasted into repo or exported |

---

## Constraints and assumptions

- Governance text is **English** per repository language policy.
- Closure and registers are maintained in the **state** file, not here.
- Multi-service monorepo: cross-package imports must not be assumed safe without isolated service roots.

---

## Open uncertainties

1. Full numeric tables from the audit DOCX not present in repo input.
2. Exact container reproduction commands for audit-only runs (if required for Part K) may need to be attached by audit owner.
3. Product/marketing claims (“persistent consequences”, “fair”) for external risk alignment — **not** in repo; needs business owner input for residual risk acceptance.
