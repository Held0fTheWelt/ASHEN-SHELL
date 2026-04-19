# World of Shadows MVP v24 — Lean but Finishable

This package is a curated continuation MVP.

It is intentionally **not** a full archive of every surrounding artifact from earlier bundles.
It is also intentionally **not** a tiny throwaway skeleton.

The packaging goal is:

- keep the surfaces that are ultimately needed for the real runtime and platform,
- keep the materials that make completion easier, cleaner, and less drift-prone,
- remove archive, promo, export, and side-workflow ballast that does not help implementation.

## What is included on purpose

- core service surfaces: `backend/`, `world-engine/`, `frontend/`, `administration-tool/`, `writers-room/`
- AI/runtime logic surfaces: `ai_stack/`, `story_runtime_core/`, `content/`, `tools/`
- the canonical MVP planning and reference scaffold under `mvp/`
- a curated root `docs/` set with architecture, runtime, integration, governance, operations, testing, and start-here material
- FY governance suites: `contractify`, `despaghettify`, `docify`
- validation artifacts and wrapper scripts that support controlled continuation

## What was intentionally removed

Examples of removed ballast:

- `promo/`
- `outgoing/`
- `postman/`
- broad docs archive/history areas
- presentation-only and legacy side-material
- loose extra resources not required for implementation continuation

## Where to start

1. Read `MVP_V24_PACKAGE_NOTE.md`
2. Read `docs/72_V24_LEAN_SCOPE_AND_KEEP_RULES.md`
3. Read `mvp/START_HERE.md`
4. Read `mvp/docs/48_CANONICAL_IMPLEMENTATION_PROTOCOL.md`
5. Read `mvp/docs/49_CANONICAL_TARGET_SURFACES.md`
6. Read `mvp/docs/50_IMPLEMENTATION_WORKSTREAMS.md`
7. Read `docs/dev/contracts/normative-contracts-index.md`
8. Read `governance/V24_SOURCE_PRESERVATION_LEDGER.md`
9. Use the audit prompt in `docs/73_V24_AUDIT_MASTERPROMPT.md`
10. Let the auditor choose the next implementation field and generate the concrete handoff for the implementation AI

## Validation entry points

- `python scripts/run_fy_governance_cycle.py`
- `pytest mvp/reference_scaffold/tests -q`
- `pytest ai_stack/tests/test_capabilities.py ai_stack/tests/test_mcp_canonical_surface.py -q`

## Packaging intent in one sentence

This is a **lean but finishable MVP**: trimmed of ballast, but still carrying the real runtime/service/governance surfaces that a completion-oriented implementation cycle will need.
