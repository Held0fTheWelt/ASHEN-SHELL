# Manifest-first Contractify governance closure report

## What changed

- Added repo-root `fy-manifest.yaml`.
- Pinned `suites.contractify.openapi` to `docs/api/openapi.yaml`.
- Pinned `suites.contractify.max_contracts` to `60` so the runtime/MVP spine is reproducible from the default repo-root CLI.
- Updated `contractify.tools.hub_cli` so `discover` / `audit` read the manifest-backed ceiling when `--max-contracts` is omitted.
- Added `execution_profile` to Contractify discover/audit payloads.
- Extended the curated runtime/MVP spine with runtime commit, authoritative interaction, WebSocket, routing/operator-audit, evidence-baseline, and API projection governance.
- Closed the deterministic OpenAPI → Postman projection drift by regenerating generated collections and manifest metadata from the canonical OpenAPI anchor.
- Added explicit `contractify-projection:` markers to audience and API-readable projection docs.
- Refreshed tracked artifacts:
  - `reports/contract_audit.json`
  - `reports/contract_discovery.json`
  - `reports/runtime_mvp_attachment_report.md`
  - `state/RUNTIME_MVP_SPINE_ATTACHMENT.md`
- Added projection-governance regression tests for repo-root audit cleanliness and projection inventory visibility.

## Canonical audit execution

Run from repository root:

```bash
python -m contractify.tools audit --json --out "'fy'-suites/contractify/reports/contract_audit.json"
```

Because `fy-manifest.yaml` defines `suites.contractify.max_contracts = 60`, the canonical runtime/MVP attachment wave is reproduced without hidden extra CLI flags.

## Commands run

```bash
PYTHONPATH="$(pwd)/'fy'-suites" python -m postmanify.tools generate
PYTHONPATH="$(pwd)/'fy'-suites" python -m contractify.tools audit --json --out "'fy'-suites/contractify/reports/contract_audit.json" --quiet
PYTHONPATH="$(pwd)/'fy'-suites" python -m contractify.tools discover --json --out "'fy'-suites/contractify/reports/contract_discovery.json" --quiet
PYTHONPATH="$(pwd)/'fy'-suites" python -m pytest "'fy'-suites/contractify/tools/tests" -q
PYTHONPATH="$(pwd)/'fy'-suites" python -m pytest "'fy'-suites/fy_platform/tests" -q
PYTHONPATH="$(pwd)/'fy'-suites" python -m pytest "'fy'-suites/postmanify/tools/tests" -q
```

## Results

- Canonical audit stats: `54 contracts`, `25 projections`, `314 relations`, `0 drifts`, `4 conflicts`, `3 manual unresolved areas`
- Legacy fallback deprecation: not emitted on canonical repo-root Contractify audit run
- OpenAPI/Postman SHA drift: closed
- Audience projection backref drifts: closed

## Intentionally unresolved

- Backend transitional session retirement timeline remains unresolved.
- Clone reproducibility vs machine-local evidence paths remains explicitly reviewable.
- Writers’ Room vs RAG overlap remains explicitly reviewable.
- ADR vocabulary overlap remains a bounded review item rather than a proof of contradiction.
