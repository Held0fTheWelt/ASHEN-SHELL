# V24 API projection governance ledger

## Scope

This ledger governs the **API projection family** in the current MVP package so that OpenAPI-, API-doc-, and Postman-facing artifacts remain reviewable projections of higher-order runtime/API authority instead of drifting into a competing truth layer.

## Intentional layering

The API projection family is intentionally layered as follows:

1. **Higher-order runtime/API authority**
   - `docs/technical/architecture/canonical_runtime_contract.md`
   - `docs/technical/runtime/runtime-authority-and-state-flow.md`
   - `docs/ADR/adr-0001-runtime-authority-in-world-engine.md`
   - validated producer/consumer code at `world-engine/app/api/http.py` and `backend/app/services/game_service.py`
2. **Bounded canonical API schema**
   - `docs/api/openapi.yaml` for the packaged backend `/api/v1` route inventory
3. **Projection / convenience surfaces**
   - `docs/api/README.md`
   - `docs/api/REFERENCE.md`
   - `docs/api/POSTMAN_COLLECTION.md`
   - `docs/dev/api/openapi-and-api-explorer-strategy.md`
   - `postman/README.md`
   - `postman/*.postman_collection.json`
   - `postman/postmanify-manifest.json`

## Projection matrix

| Artifact | Role | Authority level | Upstream source-of-truth anchor | Coverage status | Forbidden interpretation |
|---|---|---|---|---|---|
| `docs/api/openapi.yaml` | `canonical_api_schema` | bounded canonical | canonical runtime contract family for overlapping runtime semantics | backend `/api/v1` route inventory present; schema depth still partial | not the full platform/runtime truth layer |
| `docs/api/README.md` | `projection_doc` | projection-only | `docs/api/openapi.yaml` + canonical runtime/API anchors | overview only | not a normative contract |
| `docs/api/REFERENCE.md` | `convenience_reference` | projection-only | OpenAPI + validated route code + canonical runtime contract where applicable | broad examples, uneven freshness risk | not proof of complete payload correctness |
| `docs/api/POSTMAN_COLLECTION.md` | `operational_projection` | projection-only | OpenAPI + Postman manifest lineage | mixed: current generated workflow + historical checklist residue | not a primary schema or sync proof |
| `docs/dev/api/openapi-and-api-explorer-strategy.md` | `planned_projection` | projection-only | same upstream authority anchors | strategy / roadmap only | not evidence that explorer/sync is fully solved |
| `postman/postmanify-manifest.json` | `operational_projection` | lineage evidence | `docs/api/openapi.yaml` | exact to one OpenAPI sha | not a behavioral contract |
| `postman/*.postman_collection.json` | `operational_projection` | generated convenience | OpenAPI + manifest | backend HTTP subset only | not canonical API or runtime truth |
| `postman/WEBSOCKET_MANUAL.md` | `projection_doc` | manual note | runtime/API authority docs | manual spot-check only | not a formal WebSocket protocol contract |

## Intentional residue that remains visible

The projection layer is **not fully closed**. Current residue that must stay visible:

- OpenAPI is authoritative only for the **bounded backend `/api/v1` schema surface** shipped here, not for all higher-order runtime semantics.
- OpenAPI schema depth is still partial: many operations remain inventory/stub level instead of full request/response schema coverage.
- `docs/api/REFERENCE.md` remains useful but may carry example drift risk compared with route code and OpenAPI.
- Postman assets are generated and sha-linked, but they still remain convenience projections rather than primary truth.
- The lean MVP ships generated artifacts, not the full in-package OpenAPI regeneration workflow.

## What drift looks like here

Drift on this surface includes any of the following:

- a Postman or markdown API doc reading like a stronger authority than the canonical runtime contract family
- `docs/api/openapi.yaml` implying coverage of world-engine or WebSocket truth that it does not actually carry
- manifest sha no longer matching the packaged OpenAPI artifact
- collections disappearing while docs still describe them as current
- convenience docs claiming complete or canonical payload semantics without proof

## Future re-audit must verify

Before calling the API projection layer stable, a future re-audit must verify:

1. `postman/postmanify-manifest.json` still points at `docs/api/openapi.yaml`
2. manifest sha still matches the packaged OpenAPI file
3. `docs/api/README.md`, `REFERENCE.md`, and `POSTMAN_COLLECTION.md` still declare their projection status honestly
4. OpenAPI is still described as bounded canonical schema, not as universal runtime authority
5. Postman collections still stay subordinate to OpenAPI and canonical runtime/API contracts
6. any added API explorer or sync helper is explicitly governed rather than implied into authority
