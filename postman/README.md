# Postman — World of Shadows

Collections here are **generated from** `docs/api/openapi.yaml` via **Postmanify** (`'fy'-suites/postmanify/`). Re-run after OpenAPI changes so Postman stays aligned with the API inventory.

## Files

| File / directory | Role |
|------------------|------|
| **`WorldOfShadows_Complete_OpenAPI.postman_collection.json`** | **Full suite** — one folder per OpenAPI tag, one request per operation. |
| **`suites/WorldOfShadows_Suite_<Tag>.postman_collection.json`** | **Sub-suites** — same requests, scoped to a single tag (e.g. Forum, Auth). |
| **`postmanify-manifest.json`** | Last generation metadata (OpenAPI path, sha256, output list). |
| `WorldOfShadows_Local.postman_environment.json` | Localhost targets (`backendBaseUrl`, `backendApiPrefix`, …). |
| `WorldOfShadows_Docker.postman_environment.json` | Docker / compose-style targets. |
| `WorldOfShadows_Test.postman_environment.json` | Test-oriented defaults (if used by your workflow). |
| `WEBSOCKET_MANUAL.md` | WebSocket checks (not covered by the OpenAPI HTTP generator). |
| `generated/README.md` | Note: the **master** JSON lives in this directory (`WorldOfShadows_Complete_OpenAPI…`), not under `generated/`. |

## Regenerate everything

From the **repository root** (after `pip install -e .`):

```bash
python -m postmanify.tools generate
```

Equivalent explicit path:

```bash
python -m postmanify.tools generate --out-master postman/WorldOfShadows_Complete_OpenAPI.postman_collection.json
```

This overwrites the **complete** collection, all **`suites/*.json`**, and **`postmanify-manifest.json`**.

## Import order

1. Import **`WorldOfShadows_Local`** or **`WorldOfShadows_Docker`** (environment).
2. Import **`WorldOfShadows_Complete_OpenAPI.postman_collection.json`** for a full run, **or** import one or more files from **`suites/`** for a narrower pass.
3. Set real credentials in the environment where your flows need JWTs. Generated requests use **`{{backendBaseUrl}}{{backendApiPrefix}}/…`**; they do **not** include the old hand-written auth pre-request scripts — add tokens in the environment or extend requests locally as needed.

## Coverage

Route coverage matches **`docs/api/openapi.yaml`** (backend `/api/v1` surface). For human-oriented examples and prose, see **`docs/api/REFERENCE.md`**.

## Suggested use

- **Day-to-day:** import one **`suites/WorldOfShadows_Suite_*.postman_collection.json`** for the area you are changing.
- **Pre-merge / wide sweep:** run the **complete** collection; expect bare **method + URL** requests unless you have added scripts locally.
- **CI:** consider Newman against **`WorldOfShadows_Complete_OpenAPI`** or a subset of **`suites/`** once you pin auth and ordering.

See **`'fy'-suites/postmanify/README.md`** for hub details and the **`postmanify-sync`** Cursor skill.
