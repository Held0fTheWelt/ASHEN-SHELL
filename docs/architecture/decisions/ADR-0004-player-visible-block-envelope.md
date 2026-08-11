# ADR-0004 — Versioned player-visible block envelope

**Decision status:** Accepted
**Implementation state:** Partial
**Owners:** World Engine, Frontend
**Date:** 2026-08-11
**Supersedes:** retired player-shell, typewriter and modular-block decisions
**Violations:** `AR-V004`

## Context

The player surface can flatten responder identity, action, narration, beat and diagnostic quality
that exist upstream. Multiple delivery modes also risk different ordering or reconstruction rules.

## Decision

World Engine emits one versioned immutable player-visible envelope after commit. It contains an
ordered list of typed blocks, speaker identity, committed revision and delivery metadata. Backend
transports it without semantic reconstruction. Frontend rendering is exhaustive by version and
block type; unknown versions fail safely and visibly.

## Considered options

- Free-form strings were rejected because they discard identity and structure.
- Frontend inference was rejected because it creates a second story interpretation.
- Separate REST and WebSocket schemas were rejected because they create delivery-dependent truth.

## Consequences

Compatibility adapters may be required, but must be versioned and observable. Renderer tests cover
every variant, unknown versions, reconnect order and duplicate suppression.

## Implementation correspondence

Current evidence lives in `story_window_entry_parts.py`, `story_ws.py`,
`play_narrative_stream.js` and `play_block_renderer.js`. Closure requires identical contract tests
for REST, WebSocket and replay.

## Git and historical lineage

The block renderer lineage begins in the MVP5 implementation series and retains the intent to
preserve cinematic, role-aware output. This ADR separates that intent from current completeness.
