# V24 API projection governance clarification report

## Scope

This report records the tightly scoped **API projection / OpenAPI / Postman governance clarification** pass applied to the current MVP package.
The goal of this cycle was not API redesign and not route expansion.
The goal was to make the **API projection family explicit, layered, and anti-drift reviewable**.

## Classified artifact inventory

| Artifact | Role | Normative / projection status | Allowed to represent | Must not be treated as |
|---|---|---|---|---|
| `docs/api/openapi.yaml` | `canonical_api_schema` | bounded canonical | packaged backend `/api/v1` route inventory and tag grouping | full platform/runtime truth layer |
| `docs/api/README.md` | `projection_doc` | projection-only | navigation, base-url orientation, artifact lineage | a stronger contract than OpenAPI or canonical runtime docs |
| `docs/api/REFERENCE.md` | `convenience_reference` | projection-only | human-readable endpoint examples and quick lookup | proof of full payload correctness or freshness |
| `docs/api/POSTMAN_COLLECTION.md` | `operational_projection` | projection-only | Postman workflow/status explanation and historical checklist residue | canonical schema or full sync proof |
| `docs/dev/api/openapi-and-api-explorer-strategy.md` | `planned_projection` | projection-only | strategy, limits, re-audit checks | evidence that explorer/sync is fully solved |
| `postman/README.md` | `operational_projection` | projection-only | generated collection usage guidance | primary API truth |
| `postman/*.postman_collection.json` | `operational_projection` | generated convenience | backend HTTP request import surface | runtime/WebSocket/canonical payload authority |
| `postman/postmanify-manifest.json` | `operational_projection` | lineage evidence | OpenAPI sha + output lineage | behavioral contract |

## Authority clarification

Higher-order runtime/API authority still clearly outranks the projection layer:

1. `docs/technical/architecture/canonical_runtime_contract.md`
2. `docs/technical/runtime/runtime-authority-and-state-flow.md`
3. `docs/ADR/adr-0001-runtime-authority-in-world-engine.md`
4. validated producer/consumer code at `world-engine/app/api/http.py` and `backend/app/services/game_service.py`

`docs/api/openapi.yaml` is now made explicit as a **bounded canonical API schema** for the packaged backend `/api/v1` inventory only.
It is not claimed to be the sole truth source for overlapping play-service runtime semantics.

## What changed in touched docs

- `docs/api/openapi.yaml` now carries explicit governance metadata and bounded authority wording.
- `docs/api/README.md` now states the API projection authority order and includes a projection-boundary matrix.
- `docs/api/REFERENCE.md` now declares itself a convenience projection and forbids treating examples as primary truth.
- `docs/api/POSTMAN_COLLECTION.md` now states that Postman is an operational projection layer and that historical residue remains historical.
- `docs/dev/api/openapi-and-api-explorer-strategy.md` now exists in-package and records current lean-package limits honestly.
- `postman/README.md` now exists in-package and classifies collections as generated convenience projections.
- `governance/V24_API_PROJECTION_GOVERNANCE_LEDGER.md` now records the layered model, matrix, residue, and re-audit checks.

## Contractify / governance attachment

The API projection family is now more explicitly attached in Contractify:

- `CTR-API-OPENAPI-001` now carries clearer bounded-authority wording and projection/doc attachments.
- New projection records were added for:
  - `PRJ-API-README`
  - `PRJ-API-REFERENCE`
  - `PRJ-API-POSTMAN-GUIDE`
  - `PRJ-API-EXPLORER-STRATEGY`
  - `PRJ-POSTMAN-README`
- The contract graph now records that the bounded OpenAPI schema depends on the higher-order canonical runtime contract for overlapping run-lifecycle semantics.
- A new manual unresolved area keeps the API projection layer visible as **bounded but not fully closed**.

## Before vs after (focused governance view)

| Metric | Before | After | Delta |
|---|---:|---:|---:|
| Contracts | 40 | 40 | 0 |
| Projections | 10 | 17 | 7 |
| Relations | 287 | 299 | 12 |
| Manual unresolved areas | 2 | 3 | 1 |

## Remaining visible projection residue

The projection weakness is **not hidden**. It remains visible in narrower form:

- OpenAPI remains bounded to the backend `/api/v1` schema surface.
- Schema depth remains partial for many operations.
- Markdown API docs remain lower-order convenience projections.
- Postman remains generated convenience, not canonical truth.
- The package ships generated artifacts, not the full in-package generation pipeline.

## Focused validation evidence

- updated Contractify audit: `validation/fy_reports/contractify_audit.json`
- touched API projection link check: `validation/V24_API_PROJECTION_LINK_CHECK.md` (PASS)
- YAML + manifest consistency check: PASS
- Contractify focused tests: PASS
- Postmanify focused unit tests: PASS
- API projection smoke test: PASS

## What future re-audits must verify

- that `postman/postmanify-manifest.json` still points to `docs/api/openapi.yaml`
- that the manifest sha still matches the packaged OpenAPI artifact
- that `docs/api/README.md`, `REFERENCE.md`, and `POSTMAN_COLLECTION.md` still describe themselves as projections rather than primary truth
- that no API convenience artifact starts reading like a stronger authority than the canonical runtime contract family
- that any future generator/explorer work is attached explicitly instead of implied into authority
