# Operational Settings & AI Runtime Governance

This repository now includes an operational governance control plane for bootstrap,
provider/model/route settings, runtime mode selection, and cost governance.

## Canonical behavior

- Bootstrap/trust-anchor state is persisted in backend tables and surfaced via:
  - `GET /api/v1/bootstrap/public-status`
  - `GET /api/v1/admin/bootstrap/status`
  - `POST /api/v1/admin/bootstrap/initialize`
  - `POST /api/v1/admin/bootstrap/reopen`
- Runtime truth is resolved server-side and surfaced via:
  - `GET /api/v1/admin/runtime/resolved-config`
  - `POST /api/v1/admin/runtime/reload-resolved-config`
  - `GET /api/v1/internal/runtime-config` (token-protected)

## Secret handling

- Provider credentials are write-only.
- Raw secrets are never returned by normal APIs.
- Envelope encryption uses per-secret DEK and environment KEK (`SECRETS_KEK`).

## Integration guardrail

Legacy env/default paths may remain only as documented bootstrap or emergency fallback seams and must never silently override resolved governance values during normal operation.

## Operator UI

Administration tool surfaces:

- `/manage/operational-governance`
- `/manage/operational-governance/bootstrap`
- `/manage/operational-governance/providers`
- `/manage/operational-governance/models`
- `/manage/operational-governance/routes`
- `/manage/operational-governance/runtime`
- `/manage/operational-governance/costs`

## docker-up bootstrap guidance

`python docker-up.py up` now checks bootstrap readiness through
`/api/v1/bootstrap/public-status` and prints the setup path when initialization is
still required.
