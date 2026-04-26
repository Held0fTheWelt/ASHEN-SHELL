# Legacy Documentation Artifacts — To Delete or Rewrite

**Generated:** 2026-04-26

---

## Status After Cleanup

All major legacy documentation artifacts have been addressed in this cleanup pass.

---

## Artifacts Addressed

### Root-Level Session Reports → Archived
All root-level WORKSTREAM_*.md, PHASE_*.md, LANGFUSE_*.md, AUDIT_*.md, Plan*.md, STORY_RUNTIME_*.md,
REPAIR_*.md, and related session reports have been moved to `docs/archive/session-reports-2026/`.

These were classified as:
- `false_pass_report` (IMPLEMENTATION_COMPLETE.md, GOVERNANCE_*.md with no source evidence)
- `obsolete_report` (PHASE_*.md, WORKSTREAM_*.md — historical checkpoints)
- `legacy_assumption_doc` (Plan*.md referencing old architecture phases)

### Required New Docs → Created
| Document | Status |
|----------|--------|
| docs/architecture/current_service_boundaries.md | CREATED |
| docs/architecture/god_of_carnage_current_contract.md | CREATED |
| docs/architecture/runtime_profile_vs_content_contract.md | CREATED |
| docs/architecture/observability_traceability_contract.md | CREATED |
| docs/testing/TEST_SUITE_CONTRACT.md | CREATED |
| docs/testing/LEGACY_TEST_QUARANTINE_POLICY.md | CREATED |
| docs/testing/DOCS_TRUTH_POLICY.md | CREATED |

---

## Remaining Active Docs Requiring Monitoring

| Document | Classification | Issue | Priority |
|----------|---------------|-------|----------|
| docs/72_V24_LEAN_SCOPE_AND_KEEP_RULES.md | needs_review | Root-level doc with V24 scope rules — may be stale | LOW |
| docs/73_V24_AUDIT_MASTERPROMPT.md | needs_review | V24 audit prompt — historical artifact | LOW |
| docs/74_V24_IMPLEMENTATION_MASTERPROMPT_TEMPLATE.md | needs_review | Implementation prompt template | LOW |
| docs/75_V24_REAUDIT_CHECKLIST.md | needs_review | Reaudit checklist — may be superseded | LOW |
| docs/RepairPlan.md | needs_review | Old repair plan — may be historical | LOW |

These are low-priority — they don't actively contradict current architecture but may need
archiving in a future cleanup pass.

---

## Docs Not Touched (Currently Valid)

| Path | Classification |
|------|---------------|
| docs/ADR/*.md | current_ADR |
| docs/ADR/MVP_Live_Runtime_Completion/*.md | current_ADR |
| docs/architecture/ai_story_contract.md | current_contract_doc |
| docs/architecture/god_of_carnage_module_contract.md | current_contract_doc |
| docs/architecture/session_runtime_contract.md | current_contract_doc |
| docs/architecture/mvp_definition.md | current_contract_doc |
| docs/admin/*.md | current_runbook |
| docs/testing/*.md | current_testing_contract |
| docs/MVPs/ | current_mvp_docs |
