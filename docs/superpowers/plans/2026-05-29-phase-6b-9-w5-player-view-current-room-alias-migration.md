# Phase 6B-9: W5 Player View Replaces Public current_room Compatibility Aliases — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create ADR-0069, a public payload inventory, safe preparatory implementation, and a complete test suite proving the W5 player view is the authoritative player-facing actor-situation surface while `current_room`/`current_room_id`/`viewer_room_id` remain compatibility aliases.

**Architecture:** Phase 6B-1 already wired W5 player view into HTTP player-shell payloads and upgraded `backend/app/web/static/app.js` and `frontend/static/play_live_ws.js` to W5-first. Phase 6B-9 documents the migration contract in ADR-0069, upgrades the world-engine standalone UI to W5-first, adds compatibility alias doc comments to `RuntimeSnapshot`, extends the inventory scanner with Phase 6B-9 surfaces, and adds tests for every gap that the spec mandates.

**Tech Stack:** Python 3.12, Pydantic v2, pytest, vanilla JavaScript (no bundler), ADR markdown

---

## Technical Verification (pre-plan)

All findings confirmed by reading actual source files.

| File | Symbol | Lines | Status |
|------|--------|-------|--------|
| `backend/app/runtime/models.py` | `RuntimeSnapshot.viewer_room_id` | 146 | PUBLIC — WS payload, no compat comment yet |
| `backend/app/runtime/models.py` | `RuntimeSnapshot.current_room` | 149 | PUBLIC — WS payload, no compat comment yet |
| `world-engine/app/runtime/models.py` | `RuntimeSnapshot.viewer_room_id` | 139 | PUBLIC — WS payload, no compat comment yet |
| `world-engine/app/runtime/models.py` | `RuntimeSnapshot.current_room` | 142 | PUBLIC — WS payload, no compat comment yet |
| `world-engine/app/web/static/app.js` | `currentRoom()` | 85–88 | LEGACY ONLY — reads `snapshot.current_room` directly, no W5 logic |
| `backend/app/web/static/app.js` | `currentRoom()` | 131–133 | W5-FIRST — calls `currentRoomFromSnapshot()`, DONE |
| `frontend/static/play_live_ws.js` | `roomFromSnapshot()` | 25–36 | W5-FIRST — DONE |
| `backend/app/api/v1/game/player_shell_state_projection.py` | `w5_player_view` + `current_room_id` | 44–81 | DONE — dual-surface payload with diagnostics |
| `world-engine/app/story_runtime/manager/actor_tracking/session_state_w5_view.py` | `_maybe_build_w5_player_view_for_session()` | 101–145 | DONE |
| `world-engine/app/runtime/engine.py` | `build_snapshot()` | 30–59 | WS snapshot — no `w5_player_view` yet (gap to document in ADR) |
| `scripts/inventory_w5_legacy_consumers.py` | `LEGACY_SURFACES` | 35–72 | missing `viewer_room_id`, `w5_player_view` surfaces |
| `docs/architecture/components/world-engine/architecture*` | — | — | DOES NOT EXIST — primary deliverable |

**ADR number:** 0069 (0068 was the highest numbered ADR before SAD-only retirement; see `docs/archive/adr-retired-2026/`).

**Existing test files that are complete and must not be broken:**
- `world-engine/tests/test_story_runtime_w5_player_view.py`
- `world-engine/tests/test_story_runtime_w5_admin_diagnostics.py`
- `backend/tests/test_w5_player_shell_payload.py`
- `tests/test_inventory_w5_legacy_consumers.py`

---

## File Map

**Create:**
- `docs/architecture/components/world-engine/architecture.md#d6-w5-actor-tracking-and-player-view` — primary ADR

**Modify:**
- `backend/app/runtime/models.py:146,149` — add compat alias comments to `RuntimeSnapshot`
- `world-engine/app/runtime/models.py:139,142` — same
- `world-engine/app/web/static/app.js:85–88` — upgrade `currentRoom()` to W5-first
- `scripts/inventory_w5_legacy_consumers.py` — add `viewer_room_id`, `w5_player_view`, Phase 6B-9 section
- `backend/tests/test_w5_player_shell_payload.py` — add world-engine/app.js test + WS gap doc test
- `tests/test_inventory_w5_legacy_consumers.py` — add tests for new surfaces

---

## Task 1: Create ADR-0069

**Files:**
- Create: `docs/architecture/components/world-engine/architecture.md#d6-w5-actor-tracking-and-player-view`

- [ ] **Step 1: Write the ADR**

```markdown
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

Three surfaces have not yet been migrated:

1. **`world-engine/app/web/static/app.js`** — standalone world-engine UI still reads
   `state.snapshot.current_room` directly without consulting `w5_player_view`.
2. **WebSocket `RuntimeSnapshot` payload** — `RuntimeSnapshot` (Pydantic, both
   `backend/app/runtime/models.py` and `world-engine/app/runtime/models.py`) carries
   `viewer_room_id: str` and `current_room: dict | None` but does NOT yet carry
   `w5_player_view`. The WS path is therefore on the legacy surface exclusively.
3. **Compatibility alias comments** — `RuntimeSnapshot.viewer_room_id` and
   `RuntimeSnapshot.current_room` have no annotation marking them as compatibility
   aliases pending W5 migration.

This ADR defines the target state, the client compatibility policy, and the
step-by-step migration path.

## Problem

`current_room`, `current_room_id`, and `viewer_room_id` were the original
authoritative location fields for the player runtime. Since Phase 6B-1, the
authoritative source is `w5_player_view.where_summary` (built by
`build_w5_projection_for_player_shell` from `ai_stack/actor_tracking/projection.py`).

The legacy fields remain as compatibility aliases in:
- HTTP player-shell state payload (`current_room_id`, `current_room_source`,
  `current_room_fallback_value`, `current_room_w5_value`, `current_room_mismatch`)
- WebSocket `RuntimeSnapshot` (`viewer_room_id`, `current_room`)
- world-engine standalone UI (`currentRoom()` reading `snapshot.current_room`)

Without a documented migration contract and preparatory implementation, consumer
code cannot safely switch to W5-first reads and cannot validate when the legacy
aliases become redundant.

## Decision

### Phase 6B-9 (this ADR — Proposed)

Implement safe preparatory steps only. No public aliases are removed.

1. Add compatibility-alias doc comments to `RuntimeSnapshot.viewer_room_id` and
   `RuntimeSnapshot.current_room` in both `backend/app/runtime/models.py` and
   `world-engine/app/runtime/models.py`.
2. Upgrade `world-engine/app/web/static/app.js` `currentRoom()` to W5-first with
   legacy fallback, matching the pattern already in `backend/app/web/static/app.js`.
3. Add `viewer_room_id` and `w5_player_view` to the inventory scanner surface list
   so Phase 6B-10 can track their prevalence.
4. Add tests proving the world-engine UI is W5-first, that the WS payload gap is
   explicitly documented, and that the inventory script covers the new surfaces.

### Planned Phase 6B-10 (future ADR)

Wire `w5_player_view` into `RuntimeSnapshot` as an optional field. This requires:
- Adding `w5_player_view: dict[str, Any] | None = None` and
  `feature_flags: dict[str, Any] | None = None` to `RuntimeSnapshot`.
- Populating these fields in `RuntimeEngine.build_snapshot()` from the story
  session state.
- Adding WS-side tests and frontend WS integration tests.

Phase 6B-10 will have its own ADR and dedicated compatibility tests.

### Planned Phase 6B-11 (future ADR, after 6B-10)

Mark `viewer_room_id` and `current_room` as deprecated in `RuntimeSnapshot` once
W5 player view is proven on WS payloads. Document removal timeline. Coordinate
client upgrade.

## Current Public Payload Shape

### HTTP player-shell state (returned by `/api/v1/game/sessions/{id}/state`)

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

### WebSocket `RuntimeSnapshot` (current — gap identified)

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

**Gap:** `w5_player_view` and `feature_flags` are absent from WS snapshot. WS
clients (`world-engine/app/web/static/app.js`) fall through to `snapshot.current_room`
until Phase 6B-10 wires W5 into `RuntimeSnapshot`.

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
Phase 6B-11.

## W5 Player View Contract

**Builder:** `build_w5_projection_for_player_shell()` in
`ai_stack/actor_tracking/projection.py`

**Key output fields:**
- `target_consumer: "player_shell"` — identifies consumer scope; never NPC or Director
- `where_summary.current_visible_location` — primary room identifier string (string)
- `where_summary.current_location` — secondary fallback string
- `where_summary.scene_location.value` — tertiary fallback (fact dict)
- `where_summary.facts.scene_location` — quaternary fallback (raw fact)
- `how_summary.facts` — How dimension is first-class (not gated by flag)
- `why_summary.facts` — present but soft truth; `truth_attribution` marks inferred keys
- `truth_attribution` — keys listing `"inferred"` for any Why facts not directly observed

**What is NOT in player-shell W5 view:**
- Private NPC `why_summary` facts from actors with `visibility: "private_to_actor"`
  — filtered at projection boundary in `_player_shell_why_summary()`
- Internal director/narrator Why reasoning

## Client Compatibility Policy

1. **Never remove `current_room` or `viewer_room_id` without a dedicated ADR and
   proven client upgrade.** These are public WebSocket payload fields.
2. **Never remove the malformed-W5 fallback** in `session_state_w5_view.py`.
   The `try/except` in `_maybe_build_w5_player_view_for_session()` is safety, not dead code.
3. **`W5_AST_FRONTEND_PLAYER_VIEW_ENABLED=0`** remains a supported opt-out. Any code
   that gates on this flag must keep the legacy `current_room` path alive.
4. Frontend code MUST follow W5-first with legacy fallback:
   ```js
   if (w5FrontendPlayerViewEnabled(snapshot)) {
     const w5Room = roomFromW5PlayerView(snapshot);
     if (w5Room) return w5Room;
   }
   return snapshot.current_room || null;
   ```

## Deprecation Timeline

| Phase | Action | ADR |
|-------|--------|-----|
| 6B-9 (now) | Preparatory: doc comments, world-engine UI W5-first, inventory scanner, tests | 0069 |
| 6B-10 (next) | Wire `w5_player_view` into `RuntimeSnapshot` + WS tests | future |
| 6B-11 (after) | Deprecate `viewer_room_id` + `current_room` in `RuntimeSnapshot` | future |
| 6B-12 (after clients upgrade) | Remove `viewer_room_id` + `current_room` from `RuntimeSnapshot` | future |

## Feature Flag / Rollback

`W5_AST_FRONTEND_PLAYER_VIEW_ENABLED` (env var, default on):
- `1/true/yes/on` or unset → W5 player view enabled; frontend reads W5 first
- `0/false/no/off` → legacy fallback only; `w5_player_view` not built

Rollback: set `W5_AST_FRONTEND_PLAYER_VIEW_ENABLED=0` in environment. No code
change required. The legacy surface (`runtime_world.current_room_id`,
`environment_state.current_room_id`) is always populated independently of the flag.

## WebSocket Migration Strategy

Phase 6B-10 will extend `RuntimeSnapshot` with optional fields:
```python
w5_player_view: dict[str, Any] | None = None
feature_flags: dict[str, Any] | None = None
```

`RuntimeEngine.build_snapshot()` will populate these from the session W5 view
when available. WS clients must adopt the same W5-first + fallback pattern as
HTTP clients before Phase 6B-11 removes the legacy fields.

## Frontend Migration Strategy

All three frontend files follow (or will follow) the same pattern:

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

`backend/app/web/static/app.js` — DONE (Phase 6B-1).
`frontend/static/play_live_ws.js` — DONE (Phase 6B-1).
`world-engine/app/web/static/app.js` — Phase 6B-9 (this ADR).

## Backend Payload Migration Strategy

`backend/app/api/v1/game/player_shell_state_projection.py` already emits the dual
surface. No change needed in Phase 6B-9. Phase 6B-10 will wire the same view into
`RuntimeEngine.build_snapshot()` for the WS path.

## Observability Diagnostics

`w5_player_view_diagnostics` in the HTTP player-shell payload carries:
- `current_room_source`: `"w5_player_view"` or `"fallback_current_room"`
- `current_room_fallback_value`: raw legacy value
- `current_room_w5_value`: W5-derived value
- `current_room_mismatch`: boolean, true when both are present and differ

These diagnostics let engineers confirm W5 is active and detect divergence.

## Acceptance Criteria

- [ ] ADR-0069 exists as `docs/architecture/components/world-engine/architecture.md#d6-w5-actor-tracking-and-player-view`
- [ ] `RuntimeSnapshot.viewer_room_id` and `.current_room` carry compatibility alias comments in both model files
- [ ] `world-engine/app/web/static/app.js` `currentRoom()` is W5-first with legacy fallback
- [ ] Inventory scanner declares `viewer_room_id` and `w5_player_view` surfaces with Phase 6B-9 classification
- [ ] `python -m py_compile` passes on all modified Python files
- [ ] `python scripts/inventory_w5_legacy_consumers.py` runs without error
- [ ] `pytest -q tests/test_inventory_w5_legacy_consumers.py` passes
- [ ] `pytest -q backend/tests/test_w5_player_shell_payload.py` passes (including new tests)
- [ ] `PYTHONPATH=world-engine:. pytest -q world-engine/tests/test_story_runtime_w5_player_view.py` passes
- [ ] `PYTHONPATH=world-engine:. pytest -q world-engine/tests/test_story_runtime_w5_admin_diagnostics.py` passes
- [ ] `PYTHONPATH=backend:. pytest -q backend/tests/test_w5_player_shell_payload.py` passes
- [ ] No public aliases removed

## Rejected Alternatives

**Remove `current_room` immediately.** Rejected — WebSocket clients consume this field.
No advance notice has been given; removal would break live clients without migration path.

**Wire W5 into `RuntimeSnapshot` in Phase 6B-9.** Rejected — scope is too large for
one phase. Phase 6B-10 owns the WS wiring with its own tests and ADR.

**Make `viewer_room_id` a property derived from W5.** Rejected — `RuntimeSnapshot` is
Pydantic; adding a validator that reads W5 would introduce a complex dependency in the
model layer. Compatibility alias removal is cleaner via Phase 6B-11 direct field removal.

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| world-engine UI W5-first breaks when `w5_player_view` absent from WS snapshot | Explicit feature-flag check + legacy fallback; `roomFromW5PlayerView()` returns null when `feature_flags` absent |
| NPC private Why leaks into player view via W5 | `_player_shell_why_summary()` already filters `private_to_actor` facts; tests assert `why_summary` not in player view |
| Inferred Why presented as fact | `truth_attribution` dict marks inferred keys; frontend SHOULD gate display; no change to spec in this ADR |
| Inventory scanner misses `viewer_room_id` occurrences | Phase 6B-9 adds the surface to `LEGACY_SURFACES` |

## Explicit Non-Goals

- No substrate consolidation: `environment_state.current_room_id`, `actor_locations`,
  `runtime_world.current_room_id` are substrate reads, not addressed here.
- No `environment_state` removal.
- No `actor_locations` substrate removal.
- No `complete_actor_locations_for_gathering` removal.
- No WS `RuntimeSnapshot` field additions (deferred to Phase 6B-10).
- No removal of any public alias in Phase 6B-9.
```

- [ ] **Step 2: Verify file was created**

```bash
ls -la docs/architecture/components/world-engine/architecture.md#d6-w5-actor-tracking-and-player-view
```
Expected: file exists, >4000 bytes

- [ ] **Step 3: Compile check (trivially passes since it's markdown)**

```bash
echo "ADR created"
```

- [ ] **Step 4: Commit**

```bash
git add docs/architecture/components/world-engine/architecture.md#d6-w5-actor-tracking-and-player-view
git commit -m "doc(adr): ADR-0069 W5 player view replaces current_room aliases — Proposed"
```

---

## Task 2: Add Compatibility Alias Doc Comments to RuntimeSnapshot

**Files:**
- Modify: `backend/app/runtime/models.py:146,149`
- Modify: `world-engine/app/runtime/models.py:139,142`

- [ ] **Step 1: Write failing test**

Add to `backend/tests/test_w5_player_shell_payload.py`:

```python
def test_runtime_snapshot_viewer_room_id_has_compatibility_alias_comment() -> None:
    from pathlib import Path
    src = (Path(__file__).resolve().parents[1] / "app/runtime/models.py").read_text(encoding="utf-8")
    assert "viewer_room_id" in src
    assert "compatibility alias" in src.lower() or "compat" in src.lower()
    assert "w5_player_view" in src


def test_runtime_snapshot_current_room_has_compatibility_alias_comment() -> None:
    from pathlib import Path
    src = (Path(__file__).resolve().parents[1] / "app/runtime/models.py").read_text(encoding="utf-8")
    assert "current_room" in src
    assert "compatibility alias" in src.lower() or "compat" in src.lower()
```

- [ ] **Step 2: Run tests to confirm they fail**

```bash
cd /mnt/d/WorldOfShadows && PYTHONPATH=backend:. pytest -q backend/tests/test_w5_player_shell_payload.py::test_runtime_snapshot_viewer_room_id_has_compatibility_alias_comment backend/tests/test_w5_player_shell_payload.py::test_runtime_snapshot_current_room_has_compatibility_alias_comment -v
```
Expected: FAIL (no compat comment yet in models.py)

- [ ] **Step 3: Add compatibility alias comments to `backend/app/runtime/models.py`**

In `backend/app/runtime/models.py`, change lines 146–149 from:
```python
    viewer_room_id: str
    viewer_role_id: str
    viewer_display_name: str
    current_room: dict[str, Any] | None = None
```
to:
```python
    viewer_room_id: str  # compat alias — W5 replacement: w5_player_view.where_summary.current_visible_location
    viewer_role_id: str
    viewer_display_name: str
    current_room: dict[str, Any] | None = None  # compat alias — W5 replacement: w5_player_view.where_summary
```

- [ ] **Step 4: Add compatibility alias comments to `world-engine/app/runtime/models.py`**

In `world-engine/app/runtime/models.py`, change lines 139–142 from:
```python
    viewer_room_id: str
    viewer_role_id: str
    viewer_display_name: str
    current_room: dict[str, Any] | None = None
```
to:
```python
    viewer_room_id: str  # compat alias — W5 replacement: w5_player_view.where_summary.current_visible_location
    viewer_role_id: str
    viewer_display_name: str
    current_room: dict[str, Any] | None = None  # compat alias — W5 replacement: w5_player_view.where_summary
```

- [ ] **Step 5: Compile check**

```bash
cd /mnt/d/WorldOfShadows && python -m py_compile backend/app/runtime/models.py && echo "OK" && PYTHONPATH=world-engine python -m py_compile world-engine/app/runtime/models.py && echo "OK"
```
Expected: two `OK` lines, no errors

- [ ] **Step 6: Run tests — expect pass**

```bash
cd /mnt/d/WorldOfShadows && PYTHONPATH=backend:. pytest -q backend/tests/test_w5_player_shell_payload.py::test_runtime_snapshot_viewer_room_id_has_compatibility_alias_comment backend/tests/test_w5_player_shell_payload.py::test_runtime_snapshot_current_room_has_compatibility_alias_comment -v
```
Expected: 2 passed

- [ ] **Step 7: Commit**

```bash
cd /mnt/d/WorldOfShadows
git add backend/app/runtime/models.py world-engine/app/runtime/models.py backend/tests/test_w5_player_shell_payload.py
git commit -m "doc(runtime): mark viewer_room_id + current_room as W5 compat aliases in RuntimeSnapshot"
```

---

## Task 3: Write Tests for world-engine/app.js W5-First and WS Gap

**Files:**
- Modify: `backend/tests/test_w5_player_shell_payload.py`

These tests must fail BEFORE Task 4 changes `world-engine/app/web/static/app.js`.

- [ ] **Step 1: Add failing tests to `backend/tests/test_w5_player_shell_payload.py`**

Append to end of file:

```python
def test_world_engine_static_currentroom_is_w5_first_with_fallback() -> None:
    """Phase 6B-9: world-engine standalone UI must follow the same W5-first pattern
    as backend/app/web/static/app.js and frontend/static/play_live_ws.js."""
    source = (
        Path(__file__).resolve().parents[2]
        / "world-engine/app/web/static/app.js"
    ).read_text(encoding="utf-8")
    assert "function w5FrontendPlayerViewEnabled(snapshot)" in source, (
        "world-engine/app/web/static/app.js must declare w5FrontendPlayerViewEnabled()"
    )
    assert "function w5PlayerViewLocation(snapshot)" in source, (
        "world-engine/app/web/static/app.js must declare w5PlayerViewLocation()"
    )
    assert "function currentRoomFromSnapshot(snapshot)" in source, (
        "world-engine/app/web/static/app.js must declare currentRoomFromSnapshot()"
    )
    assert "if (w5FrontendPlayerViewEnabled(snapshot))" in source, (
        "currentRoomFromSnapshot must gate on the feature flag"
    )
    assert "return snapshot.current_room || null;" in source, (
        "legacy fallback must remain present"
    )
    assert "if (!where) return null;" in source, (
        "w5PlayerViewLocation must guard against missing where_summary"
    )
    assert "where.scene_location && where.scene_location.value" in source, (
        "w5PlayerViewLocation must cascade through scene_location.value"
    )
    assert "why_summary" not in source, (
        "world-engine static UI must not render why_summary"
    )


def test_ws_runtime_snapshot_w5_player_view_gap_is_documented() -> None:
    """Phase 6B-9 gap tracker: the WS RuntimeSnapshot does NOT yet carry
    w5_player_view. This test documents the gap explicitly so Phase 6B-10
    can remove it once the field is wired in.

    When Phase 6B-10 wires w5_player_view into RuntimeSnapshot, replace this
    test with one that asserts the field IS present and is correctly populated.
    """
    from pathlib import Path
    we_models = (
        Path(__file__).resolve().parents[2]
        / "world-engine/app/runtime/models.py"
    ).read_text(encoding="utf-8")
    # RuntimeSnapshot does NOT carry w5_player_view in Phase 6B-9.
    # If this assertion fails, Phase 6B-10 has landed and this test should be replaced.
    assert "w5_player_view" not in we_models.split("class RuntimeSnapshot")[1].split("class ")[0], (
        "RuntimeSnapshot now carries w5_player_view — this test is stale. "
        "Replace it with a test asserting w5_player_view is correctly populated (Phase 6B-10 landed)."
    )
    be_models = (
        Path(__file__).resolve().parents[1]
        / "app/runtime/models.py"
    ).read_text(encoding="utf-8")
    assert "w5_player_view" not in be_models.split("class RuntimeSnapshot")[1].split("class ")[0], (
        "RuntimeSnapshot now carries w5_player_view — this test is stale. "
        "Replace it with a test asserting w5_player_view is correctly populated (Phase 6B-10 landed)."
    )
```

- [ ] **Step 2: Run tests to confirm first one fails**

```bash
cd /mnt/d/WorldOfShadows && PYTHONPATH=backend:. pytest -q backend/tests/test_w5_player_shell_payload.py::test_world_engine_static_currentroom_is_w5_first_with_fallback -v
```
Expected: FAIL — `w5FrontendPlayerViewEnabled` not found in world-engine/app/web/static/app.js

- [ ] **Step 3: Run WS gap test to confirm it passes already**

```bash
cd /mnt/d/WorldOfShadows && PYTHONPATH=backend:. pytest -q backend/tests/test_w5_player_shell_payload.py::test_ws_runtime_snapshot_w5_player_view_gap_is_documented -v
```
Expected: PASS (w5_player_view is not in RuntimeSnapshot yet)

- [ ] **Step 4: Commit tests only (red state preserved for Task 4)**

```bash
cd /mnt/d/WorldOfShadows
git add backend/tests/test_w5_player_shell_payload.py
git commit -m "test(w5-9): add failing test for world-engine/app.js W5-first + WS gap doc test"
```

---

## Task 4: Upgrade world-engine/app/web/static/app.js to W5-first

**Files:**
- Modify: `world-engine/app/web/static/app.js:85–88`

- [ ] **Step 1: Replace `currentRoom()` with W5-first implementation**

In `world-engine/app/web/static/app.js`, replace lines 85–88:

```js
function currentRoom() {
  if (!state.snapshot) return null;
  return state.snapshot.current_room || null;
}
```

with:

```js
function w5FrontendPlayerViewEnabled(snapshot) {
  const flags = snapshot && snapshot.feature_flags;
  if (flags && flags.W5_AST_FRONTEND_PLAYER_VIEW_ENABLED === true) return true;
  return Boolean(window.W5_AST_FRONTEND_PLAYER_VIEW_ENABLED === true);
}

function w5PlayerViewLocation(snapshot) {
  const view = snapshot && snapshot.w5_player_view;
  const where = view && view.where_summary;
  if (!where) return null;
  if (where.current_visible_location) return String(where.current_visible_location);
  if (where.current_location) return String(where.current_location);
  if (where.scene_location && where.scene_location.value) return String(where.scene_location.value);
  if (where.facts && where.facts.scene_location) return String(where.facts.scene_location);
  return null;
}

function roomFromW5PlayerView(snapshot) {
  const roomId = w5PlayerViewLocation(snapshot);
  if (!roomId) return null;
  const currentRoom = snapshot.current_room || null;
  if (currentRoom && currentRoom.id === roomId) return currentRoom;
  const rooms = snapshot.rooms || null;
  if (Array.isArray(rooms)) {
    const found = rooms.find(room => room && room.id === roomId);
    if (found) return found;
  } else if (rooms && rooms[roomId]) {
    return rooms[roomId];
  }
  return { id: roomId, name: roomId, description: '' };
}

function currentRoomFromSnapshot(snapshot) {
  if (!snapshot) return null;
  if (w5FrontendPlayerViewEnabled(snapshot)) {
    const w5Room = roomFromW5PlayerView(snapshot);
    if (w5Room) return w5Room;
  }
  return snapshot.current_room || null;
}

function currentRoom() {
  return currentRoomFromSnapshot(state.snapshot);
}
```

- [ ] **Step 2: Run the failing test — expect pass now**

```bash
cd /mnt/d/WorldOfShadows && PYTHONPATH=backend:. pytest -q backend/tests/test_w5_player_shell_payload.py::test_world_engine_static_currentroom_is_w5_first_with_fallback -v
```
Expected: PASS

- [ ] **Step 3: Run full player-shell payload test suite**

```bash
cd /mnt/d/WorldOfShadows && PYTHONPATH=backend:. pytest -q backend/tests/test_w5_player_shell_payload.py -v
```
Expected: all tests pass (including original tests for backend/app.js and play_live_ws.js)

- [ ] **Step 4: Commit**

```bash
cd /mnt/d/WorldOfShadows
git add world-engine/app/web/static/app.js
git commit -m "feat(w5-9): upgrade world-engine standalone UI currentRoom() to W5-first with legacy fallback"
```

---

## Task 5: Update Inventory Scanner for Phase 6B-9

**Files:**
- Modify: `scripts/inventory_w5_legacy_consumers.py`
- Modify: `tests/test_inventory_w5_legacy_consumers.py`

- [ ] **Step 1: Write failing inventory test**

Add to `tests/test_inventory_w5_legacy_consumers.py`:

```python
def test_phase_6b9_surfaces_are_declared(inventory_module) -> None:
    """Phase 6B-9: viewer_room_id and w5_player_view must be in the scanner."""
    keys = {key for key, _ in inventory_module.LEGACY_SURFACES}
    assert "viewer_room_id" in keys, "viewer_room_id surface missing from LEGACY_SURFACES"
    assert "w5_player_view" in keys, "w5_player_view surface missing from LEGACY_SURFACES"


def test_phase_6b9_taxonomy_extended(inventory_module) -> None:
    """Phase 6B-9 taxonomy must include w5_first_already_migrated."""
    assert "w5_first_already_migrated" in inventory_module.PHASE_6B4_TAXONOMY, (
        "PHASE_6B4_TAXONOMY must include w5_first_already_migrated for Phase 6B-9"
    )
    assert "still_needed_public_client_compatibility" in inventory_module.PHASE_6B4_TAXONOMY


def test_scan_finds_viewer_room_id(inventory_module) -> None:
    """viewer_room_id appears in both RuntimeSnapshot definitions."""
    report = inventory_module.scan(REPO_ROOT)
    counts = report.by_surface()
    assert counts.get("viewer_room_id", 0) > 0, (
        "viewer_room_id must appear in scan results (present in RuntimeSnapshot)"
    )
```

- [ ] **Step 2: Run to confirm failure**

```bash
cd /mnt/d/WorldOfShadows && pytest -q tests/test_inventory_w5_legacy_consumers.py::test_phase_6b9_surfaces_are_declared tests/test_inventory_w5_legacy_consumers.py::test_phase_6b9_taxonomy_extended tests/test_inventory_w5_legacy_consumers.py::test_scan_finds_viewer_room_id -v
```
Expected: FAIL — `viewer_room_id` and `w5_player_view` not yet in LEGACY_SURFACES

- [ ] **Step 3: Add `viewer_room_id` and `w5_player_view` to LEGACY_SURFACES**

In `scripts/inventory_w5_legacy_consumers.py`, after the line:
```python
    ("transition_from_previous", r"\btransition_from_previous\b"),
```
add before `("location_changed", ...)`:
```python
    # Phase 6B-9 surfaces: public payload aliases targeted for migration
    ("viewer_room_id", r"\bviewer_room_id\b"),
    ("w5_player_view", r"\bw5_player_view\b"),
```

- [ ] **Step 4: Add Phase 6B-9 classification entries**

In `PHASE_6B2_CLASSIFICATION`, add after the `"location_changed"` entry:
```python
    "viewer_room_id": "L — public WS RuntimeSnapshot compat alias; needs_dedicated_adr_before_removal (ADR-0069 plans Phase 6B-11)",
    "w5_player_view": "current — W5 player-shell projection surface; w5_first_already_migrated",
```

In `PHASE_6B4_CLASSIFICATION`, add after the `"location_changed"` entry:
```python
    "viewer_room_id": (
        "still_needed_public_client_compatibility + needs_dedicated_adr_before_removal — "
        "public WS RuntimeSnapshot field read by all WS frontend clients; "
        "removal requires Phase 6B-11 ADR + proven client migration"
    ),
    "w5_player_view": (
        "w5_first_already_migrated — W5 player-shell projection surface; "
        "wired in Phase 6B-1; current authority for player-facing location"
    ),
```

- [ ] **Step 5: Add `w5_first_already_migrated` to PHASE_6B4_TAXONOMY**

In `PHASE_6B4_TAXONOMY`, add `"w5_first_already_migrated"` if not already present.
The current tuple ends with `"removed_by_adr_0068_admin_metadata"`. Add after it:
```python
    "w5_first_already_migrated",
```

- [ ] **Step 6: Add Phase 6B-9 section to `_format_human()`**

In `scripts/inventory_w5_legacy_consumers.py`, before the `return "\n".join(out)` line, add:

```python
    out.append("")
    out.append("Phase 6B-9 — ADR-0069 PROPOSED (2026-05-29):")
    out.append("  viewer_room_id: public WS RuntimeSnapshot compat alias; kept until Phase 6B-11.")
    out.append("  w5_player_view: current W5 player-shell projection surface; migrated in Phase 6B-1.")
    out.append("  world-engine/app/web/static/app.js currentRoom(): upgraded to W5-first in Phase 6B-9.")
    out.append("  WS RuntimeSnapshot w5_player_view gap: tracked; Phase 6B-10 will wire it in.")
    _6b9_keys = ("viewer_room_id", "w5_player_view")
    for key in _6b9_keys:
        count = sum(1 for f in report.findings if f.surface == key)
        label = PHASE_6B4_CLASSIFICATION.get(key, "—")
        out.append(f"  {key:48s} {count:3d}  {label[:70]}")
```

- [ ] **Step 7: Compile check**

```bash
cd /mnt/d/WorldOfShadows && python -m py_compile scripts/inventory_w5_legacy_consumers.py && echo "OK"
```
Expected: `OK`

- [ ] **Step 8: Run inventory script**

```bash
cd /mnt/d/WorldOfShadows && python scripts/inventory_w5_legacy_consumers.py 2>&1 | head -50
```
Expected: runs without error; shows Phase 6B-9 section with counts for `viewer_room_id` and `w5_player_view`

- [ ] **Step 9: Run failing tests — expect pass**

```bash
cd /mnt/d/WorldOfShadows && pytest -q tests/test_inventory_w5_legacy_consumers.py::test_phase_6b9_surfaces_are_declared tests/test_inventory_w5_legacy_consumers.py::test_phase_6b9_taxonomy_extended tests/test_inventory_w5_legacy_consumers.py::test_scan_finds_viewer_room_id -v
```
Expected: 3 passed

- [ ] **Step 10: Run full inventory test suite**

```bash
cd /mnt/d/WorldOfShadows && pytest -q tests/test_inventory_w5_legacy_consumers.py -v
```
Expected: all pass

- [ ] **Step 11: Commit**

```bash
cd /mnt/d/WorldOfShadows
git add scripts/inventory_w5_legacy_consumers.py tests/test_inventory_w5_legacy_consumers.py
git commit -m "feat(w5-9): extend inventory scanner with viewer_room_id + w5_player_view Phase 6B-9 surfaces"
```

---

## Task 6: Run Full Required Test Battery

Run all tests specified in the task spec and confirm exact counts.

- [ ] **Step 1: py_compile all changed Python files**

```bash
cd /mnt/d/WorldOfShadows && python -m py_compile \
  backend/app/runtime/models.py \
  world-engine/app/runtime/models.py \
  scripts/inventory_w5_legacy_consumers.py \
  tests/test_inventory_w5_legacy_consumers.py \
  backend/tests/test_w5_player_shell_payload.py \
  && echo "ALL COMPILE OK"
```
Expected: `ALL COMPILE OK`

- [ ] **Step 2: Inventory script**

```bash
cd /mnt/d/WorldOfShadows && python scripts/inventory_w5_legacy_consumers.py 2>&1 | tail -20
```
Expected: no error; shows Phase 6B-9 section

- [ ] **Step 3: Inventory tests**

```bash
cd /mnt/d/WorldOfShadows && pytest -q tests/test_inventory_w5_legacy_consumers.py
```
Expected: all pass, 0 failed

- [ ] **Step 4: AI stack actor-tracking tests**

```bash
cd /mnt/d/WorldOfShadows && pytest -q ai_stack/tests/test_w5_actor_tracking_projection.py ai_stack/tests/test_w5_actor_tracking_validation.py
```
Expected: all pass

- [ ] **Step 5: World-engine W5 player view tests**

```bash
cd /mnt/d/WorldOfShadows && PYTHONPATH=world-engine:. pytest -q world-engine/tests/test_story_runtime_w5_player_view.py
```
Expected: all pass

- [ ] **Step 6: World-engine admin diagnostics tests**

```bash
cd /mnt/d/WorldOfShadows && PYTHONPATH=world-engine:. pytest -q world-engine/tests/test_story_runtime_w5_admin_diagnostics.py
```
Expected: all pass

- [ ] **Step 7: Backend player-shell payload tests**

```bash
cd /mnt/d/WorldOfShadows && PYTHONPATH=backend:. pytest -q backend/tests/test_w5_player_shell_payload.py
```
Expected: all pass (including 2 new compat-comment tests, 2 new JS tests)

- [ ] **Step 8: Backend runtime core tests**

```bash
cd /mnt/d/WorldOfShadows && pytest -q backend/tests/runtime/test_runtime_core.py
```
Expected: all pass

- [ ] **Step 9: World-engine runtime commands + WS session loop**

```bash
cd /mnt/d/WorldOfShadows && PYTHONPATH=world-engine:. pytest -q world-engine/tests/test_runtime_commands.py world-engine/tests/test_phase2_ws_session_loop_endpoint.py
```
Expected: all pass

- [ ] **Step 10: Gate tests**

```bash
cd /mnt/d/WorldOfShadows && pytest -q tests/gates/test_goc_mvp03_live_dramatic_scene_simulator_gate.py
```
Expected: all pass

```bash
cd /mnt/d/WorldOfShadows && pytest -q tests/gates/test_goc_mvp04_observability_diagnostics_gate.py tests/test_local_langfuse_docker_config.py
```
Expected: all pass (or known-skip if docker not running)

- [ ] **Step 11: Discover and run additional tests mentioning target symbols**

```bash
cd /mnt/d/WorldOfShadows && grep -rl "currentRoom\|current_room\|current_room_id\|viewer_room_id\|w5_player_view\|runtime_world.current_room_id" \
  backend/tests/ world-engine/tests/ ai_stack/tests/ tests/ \
  --include="*.py" | sort
```
Review output, then run any discovered files not already covered above.

- [ ] **Step 12: Scoped git diff check**

```bash
cd /mnt/d/WorldOfShadows && git diff --check HEAD
```
Expected: no trailing whitespace errors

---

## Self-Review

**Spec coverage check:**

| Spec requirement | Task |
|------------------|------|
| Public payload inventory — classify all surfaces | Pre-plan verification + ADR-0069 payload tables |
| ADR with all required sections | Task 1 |
| `current_room`/`current_room_id`/`viewer_room_id` compat alias doc comments | Task 2 |
| Diagnostics showing W5 vs legacy derivation | Already present in player_shell_state_projection.py; test in test_w5_player_shell_payload.py |
| Tests proving `w5_player_view` present in player-facing payloads | Already in test_story_runtime_w5_player_view.py |
| Tests proving frontend `currentRoom()` prefers W5 | Already in test_w5_player_shell_payload.py; new test for world-engine JS in Task 3 |
| Tests proving frontend `currentRoom()` falls back when W5 missing | Already in test_w5_player_shell_payload.py |
| Tests proving WS payload carries W5 or has migration plan | Task 3 (gap doc test) + ADR-0069 Phase 6B-10 section |
| Tests proving `current_room`/`current_room_id` are compat aliases not upstream authority | Already in test_story_runtime_w5_player_view.py (fallback_value vs w5_value) |
| Mismatch diagnostics W5 vs legacy | Already in test_story_runtime_w5_player_view.py |
| No private NPC Why leaks | Already tested; no change needed |
| How remains first-class | Already tested |
| Inferred Why remains soft truth | Already tested |
| No field-presence-only tests | Guidance applied throughout |
| Upgrade world-engine/app.js | Task 4 |
| Inventory scanner Phase 6B-9 | Task 5 |
| All required test runs | Task 6 |

**Placeholder scan:** No TBD, TODO, placeholder content found.

**Type consistency:** All JS function names consistent between tasks. `currentRoomFromSnapshot`, `w5FrontendPlayerViewEnabled`, `w5PlayerViewLocation`, `roomFromW5PlayerView` are consistent across Task 3 (tests) and Task 4 (implementation).

---

**Plan complete and saved to `docs/superpowers/plans/2026-05-29-phase-6b-9-w5-player-view-current-room-alias-migration.md`.**

**Two execution options:**

1. **Subagent-Driven (recommended)** — Fresh subagent per task, review between tasks, fast iteration. Use superpowers:subagent-driven-development.

2. **Inline Execution** — Execute tasks in this session using executing-plans, batch execution with checkpoints. Use superpowers:executing-plans.

**Which approach?**
