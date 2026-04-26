# Legacy Test Quarantine Policy

**Status:** Active — 2026-04-26

---

## Principle

Legacy tests must not remain in primary gates. They must be deleted, rewritten, or explicitly
quarantined with an owner and removal condition.

---

## Quarantine Criteria

A test may be quarantined (retained outside primary gates) only if ALL of the following are true:

1. A current ADR or architecture contract explicitly requires temporary retention.
2. The test is NOT in any primary suite path.
3. The test is excluded from `--suite all` execution.
4. The test has an explicit owner and removal condition documented here.
5. The test name includes `legacy`, `compat`, or `quarantine` to signal its status.

---

## Default Action

If a test cannot satisfy all quarantine criteria, the default action is **deletion**.

Weak tests (assert True, presence-only, report-only, mock-only for claimed behavior) are deleted,
not quarantined. Quarantine is for tests that validate currently-transitional behavior, not for
tests that never validated real behavior.

---

## Currently Quarantined Tests

None. All previously quarantined tests have been deleted or rewritten as of 2026-04-26 cleanup.

---

## How to Quarantine

1. Move the test file to `tests/legacy_quarantine/`.
2. Prefix the filename with `legacy_` or `compat_`.
3. Add an entry in this document with: owner, removal condition, expiry date.
4. Ensure the path is excluded from `ALL_SUITE_SEQUENCE` in `tests/run_tests.py`.

---

## Cleanup Date

2026-04-26 — initial quarantine policy established.
