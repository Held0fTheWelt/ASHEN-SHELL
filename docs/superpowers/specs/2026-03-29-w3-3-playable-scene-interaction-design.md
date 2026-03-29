# W3.3: Playable Scene View and Interaction Flow

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the session UI genuinely playable by wiring the scene view and interaction controls to the canonical turn executor, with real turn execution using in-memory session state.

**Architecture:** Hybrid session management (Flask session for lightweight linkage, server-side in-memory registry for full runtime state) with direct integration to the canonical W2 turn executor. All turns are real, all state updates are canonical, all execution is routed through the real runtime path.

**Tech Stack:** Flask (routes), Jinja2 (templates), Pydantic (runtime models), in-memory dict (session registry)

---

## Architecture

W3.3 makes the session UI genuinely playable by wiring the scene view and interaction controls to the canonical turn executor.

**Core components:**
- **`app/runtime/session_store.py`** (new): In-memory registry mapping `session_id → RuntimeSession` objects. Handles create/get/update/delete of runtime sessions.
- **`app/web/routes.py`** (modified): Three routes for scene display and turn execution:
  - `GET /play/<session_id>` — loads scene view with scene + state + input form
  - `POST /play/<session_id>/execute` — executes a real turn, updates runtime session, renders result feedback
  - Helper: `_resolve_runtime_session(session_id)` — validates Flask session matches requested session_id
- **`session_shell.html`** (modified): Replace placeholders with actual scene display, interaction form, and result feedback.

**Session data flow:**
1. User at `/play/<session_id>` → Flask session links to runtime session_id
2. Route resolves full RuntimeSession from `session_store.get(session_id)`
3. Template renders scene (title, description, state summary) from RuntimeSession
4. Operator submits free-text input via form
5. POST route extracts input → calls canonical turn executor on current canonical state
6. Turn executor returns TurnExecutionResult
7. Route updates RuntimeSession in-memory store with new canonical state
8. Template re-renders with new scene + result feedback

**In-memory constraints (explicitly documented):**
- Sessions exist only while server is running
- Sessions are lost on server restart
- No persistence across server restarts
- This is intentional MVP scope; persistence is deferred to W3.4+

---

## Component Details

### `app/runtime/session_store.py` (new module)

Responsibilities:
- Create runtime session: `create_session(session_id, initial_session_state) → RuntimeSession`
- Retrieve runtime session: `get_session(session_id) → RuntimeSession | None`
- Update runtime session: `update_session(session_id, updated_state) → RuntimeSession`
- Delete runtime session: `delete_session(session_id)`
- Internal registry: module-level in-memory dict (`_runtime_sessions: dict[str, RuntimeSession]`)

`RuntimeSession` dataclass/model wraps:
- `session_id`: unique identifier
- `current_runtime_state`: the full SessionState from W2 (canonical)
- `updated_at`: timestamp of last update

**Implementation rule:** This is the ONLY server-side runtime session registry for W3.3. No parallel stores.

### `app/web/routes.py` (modifications)

**Helper function:**
```python
def _resolve_runtime_session(session_id: str) -> RuntimeSession | None:
    """Validates Flask session matches requested session_id and loads RuntimeSession."""
    flask_session_id = session.get("active_session", {}).get("session_id")
    if flask_session_id != session_id:
        return None
    return session_store.get_session(session_id)
```

**GET /play/<session_id>:**
- Validate Flask session matches session_id
- Resolve RuntimeSession from store
- Extract: scene_id, scene_description, state_summary from canonical state
- Render `session_shell.html` with scene + state + input form

**POST /play/<session_id>/execute (new route):**
- Validate Flask session matches session_id
- Resolve RuntimeSession from store
- Extract operator input from form
- Call canonical `turn_executor.execute_turn(current_canonical_state, operator_input)`
- Update RuntimeSession in store with new canonical state from TurnExecutionResult
- Build result_feedback from TurnExecutionResult
- Re-render `session_shell.html` with new scene + result feedback
- If execution fails, preserve in-memory session state, flash error, re-render with error feedback

**Implementation rule:** The POST route MUST call the canonical runtime execution path through real W2 session/runtime objects, not a simplified UI-only wrapper. State updates must replace the in-memory runtime session with the new canonical state produced by turn execution.

### `session_shell.html` (template modifications)

**Scene display section:**
- Show `scene.title` (extracted from canonical state)
- Show `scene.description` if available
- Show `state_summary` (situation, conversation_status) derived from canonical state
- Do not fabricate narrative fields not provided by the runtime

**Interaction form section:**
- Free-text textarea for operator input (primary control)
- Optional quick-action helper buttons (observe, interact, move, etc.)
  - These buttons should populate/assist the textarea, not replace free-text input
- Form posts to `/play/<session_id>/execute` with CSRF token
- Implementation rule: Free-text is the primary interaction model; helpers are optional enhancements

**Result feedback section (shown after turn execution):**
- Narrative text from `TurnExecutionResult.narrative_text`
- Guard outcome (accepted, partially_accepted, rejected, structurally_invalid)
- If outcome is degraded/fallback/safe-turn, show visible status using real runtime outcome data
- What changed: list of accepted delta targets
- Next scene: updated scene_id if scene changed
- Implementation rule: Result feedback strictly derived from canonical TurnExecutionResult, not UI-invented fields

---

## Data Flow

**Initial scene load (GET /play/<session_id>):**
```
Browser request
  → Flask session lookup → session_id found
  → session_store.get(session_id) → RuntimeSession retrieved
  → extract: scene_id, scene_description, state_summary from canonical_state
  → render session_shell.html with scene + state + input form
```

**Turn execution (POST /play/<session_id>/execute):**
```
Browser form submit (operator_input)
  → Flask session lookup → session_id found
  → session_store.get(session_id) → RuntimeSession retrieved
  → call canonical turn_executor.execute_turn(
      current_canonical_state=RuntimeSession.current_runtime_state,
      operator_input=form_input
    )
  → turn_executor returns TurnExecutionResult
  → extract: updated_canonical_state, guard_outcome, narrative_text, what_changed
  → update RuntimeSession.current_runtime_state with TurnExecutionResult.updated_canonical_state
  → session_store.update_session(session_id, updated_RuntimeSession)
  → build result_feedback from TurnExecutionResult (narrative, outcome, what changed, next scene)
  → re-render session_shell.html with new scene + result feedback
```

**Error flow:**
```
If turn_executor raises exception or validation fails:
  → catch exception
  → preserve in-memory RuntimeSession state (no update)
  → flash error message to user
  → re-render current scene (no state change)
  → show error feedback to operator
```

**Session cleanup:**
```
User logs out or session expires:
  → session_store.delete_session(session_id)
  → Flask session cleared
```

**Implementation rules:**
- GET renders current runtime session state
- POST executes a real canonical turn and updates the in-memory session state
- Failed execution does not corrupt the in-memory session
- The UI re-renders from the authoritative runtime session state

---

## Testing Strategy

### Unit Tests: `tests/runtime/test_session_store.py` (new)

- `test_create_session`: can create and retrieve a runtime session
- `test_get_nonexistent_session`: returns None for unknown session_id
- `test_update_session`: updates in-memory session state
- `test_delete_session`: removes session from registry
- `test_multiple_concurrent_sessions`: multiple sessions coexist without state leakage

### Integration Tests: `backend/tests/test_session_ui.py` (new/updated)

**Scene view tests:**
- `test_scene_view_renders_scene_data`: GET /play/<session_id> displays scene title, description, state summary
- `test_scene_view_requires_valid_session`: GET /play/<session_id> with mismatched Flask session → error/redirect
- `test_operator_input_form_present`: GET /play/<session_id> renders textarea + quick-action helpers

**Turn execution tests:**
- `test_turn_execution_calls_canonical_executor`: POST /play/<session_id>/execute calls real turn_executor
- `test_turn_execution_updates_session_store`: after POST, RuntimeSession in store has updated canonical state
- `test_turn_result_displayed_after_execution`: POST response includes narrative, outcome, what changed, next scene
- `test_turn_execution_re_renders_from_updated_session`: POST response renders from updated in-memory session, not temporary route-local data
- `test_degraded_outcome_feedback`: if turn result is degraded/fallback/safe-turn, response renders real outcome feedback correctly
- `test_turn_failure_preserves_session_state`: if execution fails, in-memory session unchanged, error displayed

**Session isolation tests:**
- `test_session_isolation_at_route_level`: two different browser-linked sessions do not leak runtime state into each other
- `test_csrf_token_validation`: form submission requires valid CSRF token (if web layer enforces this in normal tests)

**Interaction model tests:**
- `test_quick_action_buttons_assist_free_text`: quick-action buttons populate/suggest textarea, not replace it

**Scope boundary tests:**
- `test_w3_3_scope_contained`: verify no W3.4 character depth or W3.5 history panels are implemented

---

## Scope Boundaries

**Implemented in W3.3:**
- Scene view (title, description, state summary)
- Free-text operator input (primary)
- Quick-action helpers (optional, non-replacing)
- Real turn execution via canonical executor
- Result feedback (narrative, outcome, what changed, next scene)
- In-memory session state management

**Deferred to W3.4+:**
- Persistence layer (session/turn history storage)
- Rich character detail and relationship panels
- Conflict/escalation panel depth
- Advanced debugging panels

**Deferred to W3.5:**
- Full turn history panel
- Validation/log detail panels
- Advanced diagnostics

---

## Implementation Constraints (Non-Negotiable)

1. **Canonical execution only:** The route MUST call the real turn executor through W2 runtime objects, not a UI-specific shortcut.
2. **Single registry:** `session_store` is the ONLY server-side runtime session registry for W3.3.
3. **Flask session linkage only:** Flask session stores only lightweight metadata (session_id), not the full runtime state.
4. **State fidelity:** `/play/<session_id>/execute` re-renders from the updated runtime session state, not ad hoc temporary objects.
5. **In-memory documentation:** The in-memory-only limitation is documented explicitly in code comments and developer docs.
6. **Real canonical data only:** Scene display, state summary, and result feedback derive strictly from canonical runtime/module/session data. No fabricated UI-invented fields.
7. **Free-text primary:** Interaction model is free-text input with optional helper buttons, not menu-driven or structured-choice-primary.
8. **Error preservation:** Failed turn execution preserves the last valid in-memory session state.
9. **Session isolation:** Multiple concurrent sessions must not leak runtime state into each other.

---

## Success Criteria

- ✓ A user can inspect the current scene (scene_id, description, state summary)
- ✓ A user can submit free-text operator input via the UI
- ✓ Turn execution is wired to the canonical turn executor
- ✓ Turn execution updates in-memory session state
- ✓ Turn result feedback is displayed (narrative, outcome, what changed, next scene)
- ✓ Session isolation prevents state leakage between concurrent sessions
- ✓ Failed execution preserves session state
- ✓ All tests pass (unit + integration)
- ✓ No W3 scope jump occurred (W3.4+ features deferred)
- ✓ In-memory-only constraint is clearly documented
