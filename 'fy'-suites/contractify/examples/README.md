# Contractify example machine outputs

These **committed** JSON files are **shape samples** for integrators and reviewers. They are smaller than a full monorepo audit.

- **`contract_discovery.sample.json`** — output shape of `python -m contractify.tools discover` (contracts, projections, relations).
- **`contract_audit.sample.json`** — output shape of `python -m contractify.tools audit` (adds drift, conflicts, `actionable_units`).

Regenerate from a real repo when the payload schema changes (keep samples small):

```bash
python -m contractify.tools discover --out "'fy'-suites/contractify/examples/_tmp_discovery.json" --quiet
python -m contractify.tools audit --out "'fy'-suites/contractify/examples/_tmp_audit.json" --quiet
```

Then trim large arrays and copy to `*.sample.json`. Ephemeral `_tmp_*.json` under `examples/` should be deleted and is gitignored if you add a local ignore pattern.

Live machine exports during day-to-day work belong under `reports/` (gitignored `*.json` at that path).

**Packaging hygiene:** do not ship `__pycache__` or `*.pyc` inside suite ZIPs; the repository root [`.gitignore`](../../.gitignore) already ignores them — use `git archive` or `pytest` from a clean tree before publishing extracts.
