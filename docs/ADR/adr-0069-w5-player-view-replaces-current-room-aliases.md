---
adr: "0069"
title: "W5 Player View Replaces Public current_room Compatibility Aliases"
status: Accepted
date: 2026-05-29
replaces: []
superseded_by: []
---

# ADR-0069: W5 Player View Replaces Public current_room Compatibility Aliases

## Status

Accepted

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

### Phase 6B-9 (this ADR — Accepted): Safe Preparatory Implementation

Phase 6B-9 performs safe preparatory steps only. No public aliases are removed.

**Implemented:**

1. Added compatibility-alias doc comments to `RuntimeSnapshot.viewer_room_id` and
   `RuntimeSnapshot.current_room` in both `backend/app/runtime/models.py` and
   `world-engine/app/runtime/models.py`.
2. Upgraded `world-engine/app/web/static/app.js` `currentRoom()` to W5-first with
   legacy fallback, matching the pattern already in `backend/app/web/static/app.js`.
3. Added `viewer_room_id` and `w5_player_view` to the inventory scanner surface list
   so later phases can track their prevalence.
4. Added tests proving the world-engine UI is W5-first, that the initial WS payload
   gap was explicitly documented, and that the inventory scanner covers the new
   surfaces.

### Phase 6B-10 (this ADR — Accepted): Wire W5 into RuntimeSnapshot

**Implemented in Phase 6B-10:**

1. Added `w5_player_view: dict[str, Any] | None = None` and
   `feature_flags: dict[str, Any] | None = None` to `RuntimeSnapshot` in both
   `backend/app/runtime/models.py` and `world-engine/app/runtime/models.py`.
2. Updated `RuntimeEngine.build_snapshot()` (both engines) to accept optional
   `w5_player_view` and `feature_flags` kwargs. `feature_flags` is always
   populated from the `W5_AST_FRONTEND_PLAYER_VIEW_ENABLED` env var via
   `_default_feature_flags()`. `w5_player_view` is populated when provided
   or from `instance.metadata.get("_w5_player_view")` as a cache channel.
3. Updated `RuntimeManager.build_snapshot()` to expose these kwargs so callers
   can thread pre-built W5 views without coupling `RuntimeManager` to
   `StoryRuntimeManager`.
4. WS `broadcast_snapshot()` passes no explicit W5 kwargs; `feature_flags` is
   always emitted via the default; `w5_player_view` is `None` until a caller
   populates `instance.metadata["_w5_player_view"]` or passes it explicitly.
5. Removed the gap-doc test (`test_ws_runtime_snapshot_w5_player_view_gap_is_documented`)
   and replaced it with 4 positive WS payload assertion tests.

No separate ADR-0070 was created: Phase 6B-10 wires the WS contract that this
ADR already defined as its target state. The decision and risks were fully
scoped in ADR-0069; the implementation closes the gap without a new
architectural decision.

### Phase 6B-11 (this ADR — Accepted): Populate W5 in Production WS Snapshots

**Implemented in Phase 6B-11:**

1. `RuntimeManager` now attaches to `StoryRuntimeManager` in the world-engine
   application bootstrap.
2. Story-session creation binds `content_provenance.run_id` to the corresponding
   runtime run by writing `world_engine_story_session_id` / `runtime_session_id`
   into `RuntimeInstance.metadata`.
3. `RuntimeManager.build_snapshot()` and `broadcast_snapshot()` resolve the bound
   `StorySession`, build a per-viewer W5 player view with the existing
   `build_w5_projection_for_player_shell()` path, and pass the result directly
   into `RuntimeEngine.build_snapshot()`.
4. The direct per-viewer argument is the production bridge. The
   `instance.metadata["_w5_player_view"]` cache remains a base-engine/test hook,
   but it is not the production bridge because one run can have multiple viewers.
5. Missing, disabled, or malformed W5 data fails safely to `w5_player_view: null`
   while preserving `viewer_room_id` and `current_room`.
6. Compact WS diagnostics are emitted under
   `RuntimeSnapshot.metadata.w5_player_view_diagnostics`.

Phase 6B-11 starts the public compatibility window: `viewer_room_id`,
`current_room`, and HTTP/player-shell `current_room_id` are deprecated aliases,
but they remain present and are not removed in this phase.

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

### WebSocket `RuntimeSnapshot` (Phase 6B-10 baseline)

```json
{
  "run_id": "...",
  "viewer_room_id": "salon",
  "current_room": {
    "id": "salon",
    "name": "The Salon",
    "description": "..."
  },
  "feature_flags": { "W5_AST_FRONTEND_PLAYER_VIEW_ENABLED": true },
  "w5_player_view": null
}
```

`feature_flags` is always present (populated from env var). In the Phase 6B-10
base WS path, `w5_player_view` was `null` unless a caller passed it explicitly
or populated the private cache channel. `viewer_room_id` and `current_room`
remained compat aliases.

## Target Public Payload Shape (after Phase 6B-11)

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
  },
  "metadata": {
    "w5_player_view_diagnostics": {
      "w5_player_view_used": true,
      "ws_w5_player_view_source": "w5_projection",
      "current_room_source": "w5_player_view",
      "current_room_legacy_value": "salon",
      "current_room_w5_value": "salon_w5",
      "current_room_mismatch": true,
      "ws_current_room_aliases_deprecated": true
    }
  }
}
```

`viewer_room_id` and `current_room` are retained as compatibility aliases until
Phase 6B-12 or later. They are deprecated in Phase 6B-11 but remain contractually
present throughout the client migration window.

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

| Phase | Action | ADR | Status |
|-------|--------|-----|--------|
| 6B-9 | Preparatory: compat comments, WE UI W5-first, inventory scanner, tests | 0069 | Complete |
| 6B-10 | Wire `w5_player_view` + `feature_flags` into `RuntimeSnapshot` + WS tests | 0069 | Complete |
| 6B-11 | Populate production WS `w5_player_view`; deprecate compat aliases | 0069 | Complete |
| 6B-12 | Remove `viewer_room_id` + `current_room` from `RuntimeSnapshot` | future ADR | Pending |

## Feature Flag / Rollback Behavior

`W5_AST_FRONTEND_PLAYER_VIEW_ENABLED` (env var, default on):

- Unset or `1/true/yes/on` → W5 player view built and emitted when a valid
  player-scoped W5 snapshot exists; frontend reads W5 first
- `0/false/no/off` → legacy fallback only; WS `w5_player_view` remains `null`

**Rollback procedure:** Set `W5_AST_FRONTEND_PLAYER_VIEW_ENABLED=0` in the server
environment. No code change or deployment required. The legacy surface
(`runtime_world.current_room_id`, `environment_state.current_room_id`) is always
populated independently of the flag.

## WebSocket Migration Strategy

Phase 6B-10 extended `RuntimeSnapshot` with optional fields:

```python
# world-engine/app/runtime/models.py + backend/app/runtime/models.py
w5_player_view: dict[str, Any] | None = None  # ADR-0069/6B-10
feature_flags: dict[str, Any] | None = None   # ADR-0069/6B-10
```

`RuntimeEngine.build_snapshot()` accepts `w5_player_view`, `feature_flags`, and
compact `w5_player_view_diagnostics` kwargs. `feature_flags` defaults to
`_default_feature_flags()` (reads env var).

Phase 6B-11 production population is:

1. `POST /story/sessions` records the runtime run binding from
   `StorySession.content_provenance.run_id` onto `RuntimeInstance.metadata`.
2. `RuntimeManager.build_snapshot()` / `broadcast_snapshot()` resolves the bound
   `StorySession`.
3. The manager builds the W5 view with the existing player-shell projection path,
   scoped to the connected viewer's `role_id`.
4. The manager passes the view directly to `RuntimeEngine.build_snapshot()` for
   that viewer.

The private `instance.metadata["_w5_player_view"]` cache remains a base-engine
hook only. It is not the production policy because it is run-scoped rather than
viewer-scoped.

WS clients already follow W5-first + legacy fallback. Phase 6B-11 marks the
legacy aliases deprecated and starts the compatibility window. Clients must read
`w5_player_view.where_summary.current_visible_location`, then
`current_location`, then `scene_location.value`, and use `current_room` only as
fallback during the window.

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
Phase 6B-10 wired the same W5 view into `RuntimeEngine.build_snapshot()` for
the WS path.

## Observability Diagnostics

`w5_player_view_diagnostics` in the HTTP player-shell payload carries:

| Field | Meaning |
|-------|---------|
| `current_room_source` | `"w5_player_view"` or `"fallback_current_room"` |
| `current_room_fallback_value` | Raw legacy value from `runtime_world.current_room_id` |
| `current_room_legacy_value` | Raw legacy value from WS `viewer_room_id` / runtime room state |
| `current_room_w5_value` | W5-derived location string |
| `current_room_mismatch` | Boolean — true when both present and different |
| `w5_player_view_used` | Boolean — whether W5 projection is the active source |
| `w5_player_view_failed` | Error string when W5 projection failed |
| `w5_player_view_fallback_reason` | Reason fallback was used |
| `ws_w5_player_view_source` | `"w5_projection"`, `"missing_w5"`, `"malformed_w5"`, or `"legacy_only"` |
| `w5_player_view_has_how` | Boolean — How dimension present in projection |
| `w5_player_view_has_inferred_why` | Boolean — any Why facts are inferred |
| `ws_current_room_aliases_deprecated` | Boolean — Phase 6B-11 deprecation marker for WS aliases |

These diagnostics let engineers confirm W5 is active and detect `current_room_source`
divergence without needing to read internal state.

## Acceptance Criteria

### Phase 6B-9 (Complete)

- [x] ADR-0069 exists as `docs/ADR/adr-0069-w5-player-view-replaces-current-room-aliases.md`
- [x] `RuntimeSnapshot.viewer_room_id` and `.current_room` carry compat alias comments in both model files
- [x] `world-engine/app/web/static/app.js` `currentRoom()` is W5-first with legacy fallback
- [x] Inventory scanner declares `viewer_room_id` and `w5_player_view` with Phase 6B-9 labels
- [x] All Phase 6B-9 tests pass
- [x] No public aliases removed

### Phase 6B-10 (Complete)

- [x] `RuntimeSnapshot.w5_player_view: dict[str, Any] | None = None` added to both model files
- [x] `RuntimeSnapshot.feature_flags: dict[str, Any] | None = None` added to both model files
- [x] `RuntimeEngine.build_snapshot()` accepts `w5_player_view` and `feature_flags` kwargs (both engines)
- [x] `_default_feature_flags()` populates `W5_AST_FRONTEND_PLAYER_VIEW_ENABLED` from env var
- [x] `RuntimeManager.build_snapshot()` exposes the same kwargs for callers
- [x] WS `broadcast_snapshot()` automatically includes new fields via `model_dump(mode="json")`
- [x] Gap-doc test removed; 4 positive WS payload assertion tests added
- [x] `viewer_room_id` and `current_room` compat aliases preserved — not removed
- [x] `python -m py_compile` passes on all modified Python files
- [x] All test suites pass

### Phase 6B-11 (Complete)

- [x] Production world-engine bootstrap attaches `RuntimeManager` to `StoryRuntimeManager`
- [x] Story-session creation binds `content_provenance.run_id` to the runtime run metadata
- [x] `RuntimeManager.build_snapshot()` and `broadcast_snapshot()` populate `w5_player_view` per connected viewer when W5 is valid
- [x] Missing or malformed W5 falls back to `w5_player_view: null`
- [x] `viewer_room_id` and `current_room` compatibility aliases preserved — not removed
- [x] Compact WS W5 diagnostics added under `RuntimeSnapshot.metadata`
- [x] Private NPC inferred Why is not emitted in WS `w5_player_view`
- [x] How remains first-class; inferred Why remains soft truth
- [x] Raw `w5_history` / `w5_latest_snapshot` is not emitted in WS payloads

## Rejected Alternatives

**Remove `current_room` immediately.** Rejected — WebSocket clients consume this field.
No advance notice has been given; removal would break live clients without a migration path.

**Wire W5 into `RuntimeSnapshot` in Phase 6B-9.** Rejected — scope too large for the
preparatory phase. The WS wiring required changes to `RuntimeEngine`, session state
threading, and WS-side tests. Phase 6B-10 completed that work under ADR-0069.

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
| WS gap tracker test becomes stale after Phase 6B-10 | Gap tracker removed in Phase 6B-10 and replaced by positive WS payload tests |
| How dimension omitted from player view | `w5_player_view_has_how` diagnostic; tests assert `how_summary.facts` present when How facts exist |

## Explicit Non-Goals

This ADR intentionally does NOT address:

- Substrate consolidation: `environment_state.current_room_id`, `actor_locations`,
  `runtime_world.current_room_id` remain as substrate reads.
- `environment_state` removal.
- `actor_locations` substrate removal.
- `complete_actor_locations_for_gathering` removal.
- Removing any public alias (deferred to Phase 6B-11 and 6B-12).
- `current_area` or `previous_room_id` substrate migration (separate ADR).
