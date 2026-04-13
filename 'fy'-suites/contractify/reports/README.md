# Contractify `reports/`

This directory holds **machine-generated JSON** from `discover` / `audit` runs. **Ephemeral** exports stay local; **reviewable** full payloads from the hermetic fixture live under [`committed/`](committed/README.md).

## Ephemeral vs committed

Root [`.gitignore`](../../../.gitignore) ignores `**/contractify/reports/*.json` **only for files directly under** `reports/` (single path segment). The subdirectory [`committed/`](committed/) holds **tracked** `*.hermetic-fixture.json` files — regenerate with [`../tools/freeze_committed_reports.py`](../tools/freeze_committed_reports.py).

## Regenerate locally

From the **repository root**:

```bash
python -m contractify.tools discover --json --out "'fy'-suites/contractify/reports/contract_discovery.json"
python -m contractify.tools audit --json --out "'fy'-suites/contractify/reports/contract_audit.json"
```

## Committed shape samples

For **small** schema samples see [`../examples/`](../examples/) (`*.sample.json`). For **full** discover/audit payloads matching the hermetic test tree, see [`committed/`](committed/).
