# OpenAPI and API explorer strategy

Plan for how HTTP APIs are documented and discovered in the **lean v24 MVP package**.

## Classification

- `docs/api/openapi.yaml` → **`canonical_api_schema`** for the bounded Flask backend `/api/v1` route inventory shipped in this package
- `docs/api/README.md` → **`projection_doc`**
- `docs/api/REFERENCE.md` → **`convenience_reference`**
- `docs/api/POSTMAN_COLLECTION.md` → **`operational_projection`**
- `postman/README.md` and generated collections → **`operational_projection`**
- this file → **`planned_projection`**

## Upstream authority

The higher-order authority for overlapping runtime/API semantics remains:

1. `docs/technical/architecture/canonical_runtime_contract.md`
2. `docs/technical/runtime/runtime-authority-and-state-flow.md`
3. `docs/ADR/adr-0001-runtime-authority-in-world-engine.md`
4. validated producer/consumer code (`world-engine/app/api/http.py`, `backend/app/services/game_service.py`)

This strategy doc must never be treated as a stronger truth source than those anchors.

## Current package state

- The package ships a generated `docs/api/openapi.yaml` artifact for the backend API surface.
- The package ships generated Postman collections plus `postman/postmanify-manifest.json` whose OpenAPI sha must match the packaged `openapi.yaml`.
- The package does **not** currently ship the backend-side OpenAPI generator script or a full in-package API explorer runtime.
- Therefore this MVP can govern the **artifacts and their lineage**, but it does **not** prove that in-package regeneration is available.

## What remains partial

- OpenAPI schema depth is still partial: many operations are route-inventory stubs with generic responses.
- Human-readable payload examples still live heavily in `docs/api/REFERENCE.md`.
- World-engine FastAPI/OpenAPI is not merged into this backend OpenAPI artifact.
- WebSocket/live runtime contracts remain outside the Postman/OpenAPI HTTP projection layer.

## Re-audit checks

A future re-audit should verify all of the following before calling this projection layer stable:

- `postman/postmanify-manifest.json` still points to `docs/api/openapi.yaml`
- manifest sha still matches the packaged OpenAPI artifact
- generated Postman collections remain present and importable
- `docs/api/README.md`, `REFERENCE.md`, and `POSTMAN_COLLECTION.md` still describe themselves as projections rather than primary truth
- no convenience doc starts reading like a stronger authority than the canonical runtime contract family

## Related

- `docs/api/README.md`
- `docs/api/REFERENCE.md`
- `docs/api/POSTMAN_COLLECTION.md`
- `postman/README.md`
- `governance/V24_API_PROJECTION_GOVERNANCE_LEDGER.md`
