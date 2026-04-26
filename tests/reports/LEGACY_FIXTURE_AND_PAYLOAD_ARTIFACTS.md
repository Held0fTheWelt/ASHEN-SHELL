# Legacy Fixture and Payload Artifacts

**Generated:** 2026-04-26

---

## Summary

No fixture or payload files were found that use `visitor` as a live actor or
`god_of_carnage_solo` as canonical content in test fixtures.

---

## Fixtures Reviewed

| Location | Status | Notes |
|----------|--------|-------|
| tests/e2e/conftest.py | current_valid | Flask test client fixtures, no legacy roles |
| tests/gates/conftest.py | current_valid | sys.path setup for world-engine imports |
| tests/smoke/conftest.py | current_valid | Smoke test fixtures |
| backend/tests/runtime/staged_test_payloads.py | needs_review | Staged payloads — not yet audited for visitor/legacy roles |
| backend/tests/runtime/conftest.py | needs_review | Backend conftest |
| world-engine/tests/conftest.py | needs_review | Engine conftest |

---

## Reports as Evidence (Not Proof)

The following report files exist in `tests/reports/` and are historical records only.
They are NOT active gate evidence:

| File | Classification |
|------|---------------|
| GOC_MVP2_SOURCE_LOCATOR.md | obsolete_report |
| GOC_MVP3_HANDOFF.md | obsolete_report |
| GOC_MVP4_HANDOFF.md | obsolete_report |
| GOC_PHASE*_*.md | obsolete_report |
| PHASE_*_DIAGNOSIS_*.md | obsolete_report |
| REQUIREMENTS_AUDIT_REPORT.md | obsolete_report |
| E2E_ACCEPTANCE_REPORT.md | needs_verification |

These reports were generated during prior sessions and may not reflect current state.

---

## XML Test Result Files

| Files | Status |
|-------|--------|
| tests/reports/pytest_*.xml | historical artifacts — current test runs would replace |

---

## Evidence Directories

| Path | Status |
|------|--------|
| tests/reports/evidence/ | historical evidence directories — not active proof |
| tests/reports/langfuse/ | historical Langfuse report — not active trace proof |
