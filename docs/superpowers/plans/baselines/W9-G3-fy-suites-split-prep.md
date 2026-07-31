# G3 — fy-suites repository split (Wave 9) — PREPARE ONLY

**Status:** Awaiting human approval (**G3**). Do **not** create an external repo until approved.

## Prepared command (dry documentation)

From repository root, after approval:

```bash
git subtree split --prefix="'fy'-suites" -b fy-suites-split
# Then in a new empty remote repository:
# git push <fy-suites-remote> fy-suites-split:main
```

Follow-up in this tree (only after remote exists):
1. Remove `'fy'-suites/**` from product consumption paths (`conftest.py` sys.path).
2. Relocate or delete `.github/workflows/fy-*-gate.yml`.
3. Adjust `pyproject.toml` package/scripts entries that only serve fy tooling.

## Current evidence
- Production imports of `'fy'-suites` should remain absent outside tooling/conftest (verify with `test_no_fy_suites_import_in_product` when landed).
- Direct-pytest allowlist still lists the three fy workflows until G3 lands.
