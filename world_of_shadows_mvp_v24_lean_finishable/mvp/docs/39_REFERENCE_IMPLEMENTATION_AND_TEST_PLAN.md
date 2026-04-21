# 39 — Reference Implementation and Test Plan

This MVP contains two coordinated implementation layers.

## Layer 1 — Real repository implementation

Production-facing implementation work belongs in the real repository components:
- `backend/`
- `frontend/`
- `administration-tool/`
- `world-engine/`
- `writers-room/`
- `ai_stack/`
- `tools/mcp_server/`
- `tests/`

These are the true ownership surfaces for code changes.

## Layer 2 — Runnable reference scaffold

`reference_scaffold/` is the executable minimum slice inside the MVP.
It proves:
- publish-bound session birth,
- ordinary-player versus operator separation,
- incident-visible persistence,
- MCP-safe session access,
- memory slotting and lineage basics,
- threshold/effect/transformation behavior,
- and non-graph testability.

## How to use both layers correctly

1. Understand the target behavior from the MVP chapters.
2. Inspect the scaffold to see the minimum runtime behavior in code.
3. Patch the real repository component that owns the responsibility.
4. Run the real component tests.
5. Re-run the scaffold when the seam should still match the MVP proof.

## Validation rule

The scaffold can prove the minimum behavior shape.
It cannot stand in for repository integration when the task is to implement World of Shadows itself.
