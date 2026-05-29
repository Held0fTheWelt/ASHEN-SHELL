---
adr: "0069"
title: "W5 Player View Replaces Public current_room Compatibility Aliases"
status: Proposed
date: 2026-05-29
replaces: []
superseded_by: []
---

# ADR-0069: W5 Player View Replaces Public current_room Compatibility Aliases

## Status

Proposed

## Context

Phase 6B-1 (ADR-0063 shadow mode) wired W5 actor-tracking projections into the
player-shell HTTP payload and set `W5_AST_FRONTEND_PLAYER_VIEW_ENABLED` default-on.
Backend static UI (`backend/app/web/static/app.js`) and the live-WS client
(`frontend/static/play_live_ws.js`) already resolve room location via
`w5_player_view.where_summary` with a fallback to `snapshot.current_room`.

Three surfaces had not yet been migrated at the start of Phase 6B-9:

1. **`world-engine/app/web/static/app.js`** — standalone world-engine UI still read
   `state.snapshot.current_room` directly without consulting `w5_player_view`.
2. **WebSocket `RuntimeSnapshot` payload** — `RuntimeSnapshot` (Pydantic, both
   `backend/app/runtime/models.py` and `world-engine/app/runtime/models.py`) carries
   `viewer_room_id: str` and `current_room: dict | None` but does NOT yet carry
   `w5_player_view`. The WS path is therefore on the legacy surface exclusively.
3. **Compatibility alias comments** — `RuntimeSnapshot.viewer_room_id` and
   `RuntimeSnapshot.current_room` had no annotation marking them as compatibility
   aliases pending W5 migration.

This ADR defines the target state, the client compatibility policy, and the
step-by-step migration path for retiring the `current_room`/`viewer_room_id` aliases.

## Problem

`current_room`, `current_room_id`, and `viewer_room_id` were the original
authoritative location fields for the player runtime. Since Phase 6B-1, the
authoritative source is `w5_player_view.where_summary` (built by
`build_w5_projection_for_player_shell` in `ai_stack/actor_tracking/projection.py`).

The legacy fields remain as compatibility aliases in:

- HTTP player-shell state payload (`current_room_id`, `current_room_source`,
  `current_room_fallback_value`, `current_room_w5_value`, `current_room_mismatch`)
- WebSocket `RuntimeSnapshot` (`viewer_room_id`, `current_room`)
- world-engine standalone UI (`currentRoom()` reading `snapshot.current_room`)

Without a documented migration contract and preparatory implementation, consumer
code cannot safely switch to W5-first reads and cannot validate when the legacy
aliases become redundant.

## Decision

### Phase 6B-9 (this ADR — Proposed): Safe Preparatory Implementation

Phase 6B-9 performs safe preparatory steps only. No public aliases are removed.

**Implemented:**

1. Added compatibility-alias doc comments to `RuntimeSnapshot.viewer_room_id` and
   `RuntimeSnapshot.current_room` in both `backend/app/runtime/models.py` and
   `world-engine/app/runtime/models.py`.
2. Upgraded `world-engine/app/web/static/app.js` `currentRoom()` to W5-first with
   legacy fallback, matching the pattern already in `backend/app/web/static/app.js`.
3. Added `viewer_room_id` and `w5_player_view` to the inventory scanner surface list
   so Phase 6B-10 can track their prevalence.
4. Added tests proving the world-engine UI is W5-first, that the WS payload gap is
   explicitly documented, and that the inventory scanner covers the new surfaces.

### Planned Phase 6B-10 (future ADR): Wire W5 into RuntimeSnapshot

Wire `w5_player_view` into `RuntimeSnapshot` as an optional field. Requires:
- Adding `w5_player_view: dict[str, Any] | None = None` and
  `feature_flags: dict[str, Any] | None = None` to `RuntimeSnapshot`.
- Populating these fields in `RuntimeEngine.build_snapshot()` from the story
  session state (calling `_maybe_build_w5_player_view_for_session()`).
- Adding WS-side tests and frontend WS integration tests.
- Removing the gap-doc test added in Phase 6B-9.

Phase 6B-10 will have its own ADR and dedicated compatibility tests.

### Planned Phase 6B-11 (future ADR): Deprecate Legacy WS Fields

Mark `viewer_room_id` and `current_room` as deprecated in `RuntimeSnapshot` once
W5 player view is proven on WS payloads. Document removal timeline. Coordinate
client upgrade. Requires confirmed Phase 6B-10 adoption.

### Planned Phase 6B-12 (future ADR): Remove Legacy WS Fields

Remove `viewer_room_id` and `current_room` from `RuntimeSnapshot`. Requires all
known WS clients to have migrated to W5-first reads.

## Current Public Payload Shape

### HTTP Player-Shell State (`/api/v1/game/sessions/{id}/state`)

```json
{
  "run_id": "...",
  "template_id": "...",
  "environment_state": { "current_room_id": "salon" },
  "current_room_id": "salon_w5",
  "current_room_source": "w5_player_view",
  "current_room_fallback_value": "salon",
  "current_room_w5_value": "salon_w5",
  "current_room_mismatch": true,
  "feature_flags": { "W5_AST_FRONTEND_PLAYER_VIEW_ENABLED": true },
  "w5_player_view": {
    "target_consumer": "player_shell",
    "actor_id": "annette",
    "where_summary": {
      "current_visible_location": "salon_w5",
      "current_location": "salon_w5",
      "scene_location": { "value": "salon_w5", "confidence": 1.0 }
    },
    "how_summary": { "facts": { "tone": "strained" } },
    "what_summary": { "facts": { "current_action": "listens" } },
    "why_summary": { "facts": { "motive": "keep_the_peace" } },
    "truth_attribution": { "why_summary.facts.motive": "inferred" }
  },
  "w5_player_view_diagnostics": {
    "w5_player_view_used": true,
    "current_room_source": "w5_player_view",
    "current_room_fallback_value": "salon",
    "current_room_w5_value": "salon_w5",
    "current_room_mismatch": true
  }
}
```

### WebSocket `RuntimeSnapshot` (current — Phase 6B-9 gap)

```json
{
  "run_id": "...",
  "viewer_room_id": "salon",
  "current_room": {
    "id": "salon",
    "name": "The Salon",
    "description": "..."
  }
}
```

**Gap:** `w5_player_view` and `feature_flags` are absent from the WS snapshot.
WS clients (`world-engine/app/web/static/app.js`) fall through to
`snapshot.current_room` until Phase 6B-10 wires W5 into `RuntimeSnapshot`.

## Target Public Payload Shape (after Phase 6B-10)

### WebSocket `RuntimeSnapshot`

```json
{
  "run_id": "...",
  "viewer_room_id": "salon",
  "current_room": { "id": "salon", "name": "The Salon", "description": "..." },
  "feature_flags": { "W5_AST_FRONTEND_PLAYER_VIEW_ENABLED": true },
  "w5_player_view": {
    "target_consumer": "player_shell",
    "actor_id": "annette",
    "where_summary": {
      "current_visible_location": "salon_w5",
      "scene_location": { "value": "salon_w5", "confidence": 1.0 }
    }
  }
}
```

`viewer_room_id` and `current_room` are retained as compatibility aliases until
Phase 6B-11 coordinates client upgrades.

## W5 Player View Contract

**Builder:** `build_w5_projection_for_player_shell()` in
`ai_stack/actor_tracking/projection.py`

**Consumer scope:** `target_consumer: "player_shell"` — identifies this projection as
player-facing. NPC and Director projections use separate consumer identifiers and are
never emitted on the player-facing surface.

**Key output fields and resolution order:**

| Priority | Field | Path |
|----------|-------|------|
| 1 | current_visible_location | `where_summary.current_visible_location` (string) |
| 2 | current_location | `where_summary.current_location` (string) |
| 3 | scene_location.value | `where_summary.scene_location.value` (fact dict) |
| 4 | facts.scene_location | `where_summary.facts.scene_location` (raw fact string) |

**Dimension policy:**

- **How** (`how_summary.facts`) — first-class; always included when available.
- **What** (`what_summary.facts`) — included; observable actions.
- **Why** (`why_summary.facts`) — soft truth; included but `truth_attribution` marks
  inferred keys as `"inferred"`. Frontend SHOULD display with appropriate hedging.
- **Private NPC Why** — filtered at the projection boundary in
  `_player_shell_why_summary()`. Facts with `visibility: "private_to_actor"` for
  non-player actors are excluded from the player-shell projection.

## Client Compatibility Policy

1. **Never remove `current_room` or `viewer_room_id` without a dedicated ADR and
   proven client upgrade.** These are public WebSocket payload fields consumed by
   unknown clients.
2. **Never remove the malformed-W5 fallback** in `session_state_w5_view.py`.
   The `try/except` in `_maybe_build_w5_player_view_for_session()` is a safety net
   for missing/malformed W5 snapshots, not dead code.
3. **`W5_AST_FRONTEND_PLAYER_VIEW_ENABLED=0`** remains a supported opt-out. Any code
   gating on this flag must keep the legacy `current_room` path alive.
4. All frontend code consuming room location MUST follow W5-first with legacy fallback:

   ```js
   function currentRoomFromSnapshot(snapshot) {
     if (!snapshot) return null;
     if (w5FrontendPlayerViewEnabled(snapshot)) {
       const w5Room = roomFromW5PlayerView(snapshot);
       if (w5Room) return w5Room;
     }
     return snapshot.current_room || null;
   }
   ```

## Deprecation Timeline

| Phase | Action | ADR |
|-------|--------|-----|
| 6B-9 (this) | Preparatory: compat comments, WE UI W5-first, inventory scanner, tests | 0069 |
| 6B-10 (next) | Wire `w5_player_view` into `RuntimeSnapshot` + WS tests | future |
| 6B-11 | Deprecate `viewer_room_id` + `current_room` in `RuntimeSnapshot` | future |
| 6B-12 | Remove `viewer_room_id` + `current_room` from `RuntimeSnapshot` | future |

## Feature Flag / Rollback Behavior

`W5_AST_FRONTEND_PLAYER_VIEW_ENABLED` (env var, default on):

- Unset or `1/true/yes/on` → W5 player view built and emitted; frontend reads W5 first
- `0/false/no/off` → legacy fallback only; `w5_player_view` key absent from payload

**Rollback procedure:** Set `W5_AST_FRONTEND_PLAYER_VIEW_ENABLED=0` in the server
environment. No code change or deployment required. The legacy surface
(`runtime_world.current_room_id`, `environment_state.current_room_id`) is always
populated independently of the flag.

## WebSocket Migration Strategy

Phase 6B-10 will extend `RuntimeSnapshot` with optional fields:

```python
# world-engine/app/runtime/models.py + backend/app/runtime/models.py
w5_player_view: dict[str, Any] | None = None
feature_flags: dict[str, Any] | None = None
```

`RuntimeEngine.build_snapshot()` will call `_maybe_build_w5_player_view_for_session()`
(from `world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py`)
to populate these fields when the session has W5 state available.

WS clients must adopt the same W5-first + legacy fallback pattern as HTTP clients
before Phase 6B-11 marks the legacy fields deprecated.

## Frontend Migration Strategy

All three frontend files follow (or will follow after Phase 6B-9) the same W5-first
pattern using four shared helpers: `w5FrontendPlayerViewEnabled()`,
`w5PlayerViewLocation()`, `roomFromW5PlayerView()`, `currentRoomFromSnapshot()`.

| File | Status after Phase 6B-9 |
|------|------------------------|
| `backend/app/web/static/app.js` | W5-first (Phase 6B-1 — complete) |
| `frontend/static/play_live_ws.js` | W5-first (Phase 6B-1 — complete) |
| `world-engine/app/web/static/app.js` | W5-first (Phase 6B-9 — this ADR) |

## Backend Payload Migration Strategy

`backend/app/api/v1/game/player_shell_state_projection.py` already emits the dual
surface (W5 + legacy) with full diagnostics. No change needed in Phase 6B-9.
Phase 6B-10 will wire the same W5 view into `RuntimeEngine.build_snapshot()` for
the WS path.

## Observability Diagnostics

`w5_player_view_diagnostics` in the HTTP player-shell payload carries:

| Field | Meaning |
|-------|---------|
| `current_room_source` | `"w5_player_view"` or `"fallback_current_room"` |
| `current_room_fallback_value` | Raw legacy value from `runtime_world.current_room_id` |
| `current_room_w5_value` | W5-derived location string |
| `current_room_mismatch` | Boolean — true when both present and different |
| `w5_player_view_used` | Boolean — whether W5 projection is the active source |
| `w5_player_view_failed` | Error string when W5 projection failed |
| `w5_player_view_fallback_reason` | Reason fallback was used |
| `w5_player_view_has_how` | Boolean — How dimension present in projection |
| `w5_player_view_has_inferred_why` | Boolean — any Why facts are inferred |

These diagnostics let engineers confirm W5 is active and detect `current_room_source`
divergence without needing to read internal state.

## Acceptance Criteria

- [ ] ADR-0069 exists as `docs/ADR/adr-0069-w5-player-view-replaces-current-room-aliases.md`
- [ ] `RuntimeSnapshot.viewer_room_id` and `.current_room` carry compat alias comments in both model files
- [ ] `world-engine/app/web/static/app.js` `currentRoom()` is W5-first with legacy fallback
- [ ] Inventory scanner declares `viewer_room_id` and `w5_player_view` with Phase 6B-9 labels
- [ ] `python -m py_compile` passes on all modified Python files
- [ ] `python scripts/inventory_w5_legacy_consumers.py` runs without error
- [ ] `pytest -q tests/test_inventory_w5_legacy_consumers.py` passes
- [ ] `PYTHONPATH=backend:. pytest -q backend/tests/test_w5_player_shell_payload.py` passes
- [ ] `PYTHONPATH=world-engine:. pytest -q world-engine/tests/test_story_runtime_w5_player_view.py` passes
- [ ] `PYTHONPATH=world-engine:. pytest -q world-engine/tests/test_story_runtime_w5_admin_diagnostics.py` passes
- [ ] No public aliases removed

## Rejected Alternatives

**Remove `current_room` immediately.** Rejected — WebSocket clients consume this field.
No advance notice has been given; removal would break live clients without a migration path.

**Wire W5 into `RuntimeSnapshot` in Phase 6B-9.** Rejected — scope too large. The WS
wiring requires changes to `RuntimeEngine`, session state threading, WS-side tests, and
frontend WS integration tests. Phase 6B-10 owns this work under its own ADR.

**Make `viewer_room_id` a computed property on `RuntimeSnapshot`.** Rejected —
`RuntimeSnapshot` is a Pydantic model; adding a validator that derives `viewer_room_id`
from `w5_player_view` would introduce a complex bidirectional dependency in the model
layer. Direct field removal in Phase 6B-12 is cleaner.

**Use a single shared JS module for W5 helpers.** Rejected — the three static JS files
are served from different endpoints with no shared module system. Code duplication is
intentional and keeps each file self-contained.

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| world-engine UI W5-first breaks when `w5_player_view` absent from WS snapshot | Explicit feature-flag check returns false when `feature_flags` absent; falls through to `snapshot.current_room || null` |
| NPC private Why leaks into player view | `_player_shell_why_summary()` already filters `private_to_actor` facts; tests assert `why_summary` absent for private actors |
| Inferred Why presented as certainty | `truth_attribution` dict marks inferred keys; frontend guidance added to this ADR |
| Inventory scanner misses `viewer_room_id` occurrences | Phase 6B-9 adds the surface to `LEGACY_SURFACES`; scan count test added |
| WS gap tracker test becomes stale after Phase 6B-10 | Test includes inline comment directing engineer to replace it; assertion error message names the responsible phase |
| How dimension omitted from player view | `w5_player_view_has_how` diagnostic; tests assert `how_summary.facts` present when How facts exist |

## Explicit Non-Goals

This ADR intentionally does NOT address:

- Substrate consolidation: `environment_state.current_room_id`, `actor_locations`,
  `runtime_world.current_room_id` remain as substrate reads.
- `environment_state` removal.
- `actor_locations` substrate removal.
- `complete_actor_locations_for_gathering` removal.
- Adding `w5_player_view` to `RuntimeSnapshot` (deferred to Phase 6B-10).
- Removing any public alias (deferred to Phase 6B-11 and 6B-12).
- `current_area` or `previous_room_id` substrate migration (separate ADR).
