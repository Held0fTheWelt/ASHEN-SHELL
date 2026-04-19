# Contributing and repository layout (lean v24)

Orientation for developers working inside the curated v24 bundle.

## Repository language

**Canonical policy (single source of truth):** change **only this section** when repository-language rules change.

**Policy:** use **English** for committed developer-facing and operator-facing material in this package, including:

- documentation under `docs/`,
- governance and validation outputs,
- FY-suite maintained Markdown,
- code comments and docstrings,
- and implementation-facing reports.

Player-facing narrative content may follow its authored tone, but tooling, schemas, keys, and governance prose stay English.

## Top-level layout (lean carry-forward)

| Path | Responsibility |
|------|----------------|
| `backend/` | API, auth, content compilation, governance-facing integration |
| `world-engine/` | Authoritative play-service runtime |
| `frontend/` | Player/public web UI |
| `administration-tool/` | Admin UI |
| `writers-room/` | Writers-room UI and tests |
| `ai_stack/` | AI orchestration, retrieval, GoC seams, MCP-facing surfaces |
| `story_runtime_core/` | Shared interpretation and runtime models |
| `content/modules/` | Canonical authored modules |
| `tools/mcp_server/` | MCP tooling |
| `schemas/` | Shared JSON schemas |
| `tests/` | Cross-cutting reports and smoke helpers |
| `docs/` | Active documentation, lean redirects, governance anchors |

## Related

- [Start here](../start-here/README.md)
- [Normative contracts index](contracts/normative-contracts-index.md)
- [Technical documentation](../technical/README.md)
- [Source-preservation ledger](../../governance/V24_SOURCE_PRESERVATION_LEDGER.md)
