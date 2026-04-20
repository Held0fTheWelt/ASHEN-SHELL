# Postman — World of Shadows

> **Projection governance status:** `operational_projection`
>
> The Postman assets in this package are **generated convenience projections** of `docs/api/openapi.yaml`.
> They are useful for manual API exercise and review, but they are **not** allowed to outrank the bounded OpenAPI schema or the higher-order canonical runtime/API contracts.

## Upstream authority

1. `docs/technical/architecture/canonical_runtime_contract.md` for overlapping run lifecycle payload semantics
2. `docs/api/openapi.yaml` for the bounded backend `/api/v1` machine schema shipped here
3. `postman/postmanify-manifest.json` as lineage evidence tying collections to one OpenAPI fingerprint
4. generated collections in `postman/` and `postman/suites/`

## Packaged files

| File / directory | Role | Coverage |
|---|---|---|
| `WorldOfShadows_Complete_OpenAPI.postman_collection.json` | generated master collection | backend HTTP `/api/v1` projection only |
| `suites/WorldOfShadows_Suite_*.postman_collection.json` | tag-scoped generated sub-suites | backend HTTP subset by tag |
| `postmanify-manifest.json` | generation lineage record | records OpenAPI sha and output list |
| `WEBSOCKET_MANUAL.md` | manual note | live runtime/WebSocket checks not covered by OpenAPI-generated collections |
| `generated/README.md` | location note | auxiliary only |

## What these collections are allowed to represent

- request URLs/methods grouped from the packaged OpenAPI inventory
- a practical import surface for developers/operators
- tag-scoped review passes for backend HTTP work

## What they must not be treated as

- the canonical runtime contract
- proof of full payload-shape correctness for overlapping play-service semantics
- proof that the whole platform API surface is covered
- authority over WebSocket or runtime committed truth

## Coverage note

These collections cover the packaged backend HTTP OpenAPI inventory.
They do **not** become authoritative for world-engine live runtime state, WebSocket event contracts, or any unpublished/admin convenience note.

## Environment note

This lean MVP package does **not** ship environment JSON files.
When importing collections, set `backendBaseUrl` and `backendApiPrefix` manually in your Postman environment.

## Re-audit checks

- manifest OpenAPI sha matches `docs/api/openapi.yaml`
- master and suite collections still exist
- no Postman doc or collection claims to be a stronger authority than OpenAPI or canonical runtime contracts
- WebSocket/manual checks remain explicitly separate from generated HTTP collections
