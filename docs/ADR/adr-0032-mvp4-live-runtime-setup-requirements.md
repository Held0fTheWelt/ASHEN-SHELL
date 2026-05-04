# ADR-0032: MVP4 Live Runtime Setup Requirements — 5 Core Contracts

**Status:** Accepted

**Date:** 2026-05-04

**Author:** Claude Code (with user validation)

**MVP:** 4 — End-to-End Live Story Execution

## Context

The live runtime (frontend → backend → world-engine) currently violates fundamental contracts that prevent end-to-end story execution. An audit (`live_runtime_empty_session_audit.md`) identified 12 specific defects:

- **D-001:** Actor lanes missing from backend→world-engine handoff
- **D-002:** Opening bypasses LangGraph/model (deterministic LDSS only)
- **D-003:** Empty openings pass validation without checking visible output
- **D-004:** State-only test paths mask broken create_session
- **D-005:** Frontend ignores create-session opening, renders resumed state only
- **D-006:** Empty shell marked `can_execute=true` (no degradation signal)
- **D-007:** Backend sends content-only projection, loses actor ownership
- **D-008:** Narrator streaming not forwarded in HTTP response
- **D-009:** Provider/model route blocked; fallback silent
- **D-010:** Tests false-green: mocks prove nothing about live path
- **D-011:** Visitor actor appears in legacy local UI
- **D-012:** Test docstrings claim "real runtime" for mocked paths

Rather than fixing defects sequentially, this ADR defines **5 runtime contracts** that, when fulfilled, prevent all 12 defects from being reintroduced. The contracts are:

1. Backend → World-Engine story session handoff
2. Story session opening truthfulness
3. Frontend playability and empty-state handling
4. Diagnostics and observability truthfulness
5. Narrative streaming integration

---

## Decision

### Principle: Contracts Over Repairs

MVP4 acceptance is not "we fixed defects D-001 through D-012" but "the runtime satisfies these 5 contracts, making those defects impossible."

Each contract specifies:
- **What must be true** (contract definition)
- **How we verify it** (acceptance gate + tests)
- **What happens when it breaks** (error handling, audit trail)
- **How we degrade gracefully** (fallback with visibility)

### Contract 1: Backend → World-Engine Story Session Handoff

**Definition:**

When backend calls `POST /api/story/sessions` to create a story session, it MUST include a complete `runtime_projection` with all fields required by world-engine to enforce actor lanes and runtime provenance:

```python
{
  "module_id": str,              # Content module ID (e.g. "god_of_carnage")
  "start_scene_id": str,         # Starting scene
  "scenes": dict,                # Scene definitions
  "characters": dict,            # Character definitions
  # ===== REQUIRED by MVP4 =====
  "selected_player_role": str,   # Human player's chosen role (e.g. "annette")
  "human_actor_id": str,         # Must equal selected_player_role
  "npc_actor_ids": list[str],    # All other canonical actors (non-human)
  "actor_lanes": dict,           # {actor_id: "human"|"npc"} mapping
  "runtime_profile_id": str,     # Profile ID (e.g. "god_of_carnage_solo")
  "runtime_module_id": str,      # Runtime module ID
  "content_module_id": str,      # Canonical content module
}
```

**Acceptance Gate:**

```bash
# After create_story_session, verify via GET /api/story/sessions/{session_id}/state:
curl -s http://localhost:8001/api/story/sessions/{session_id}/state \
  -H "X-Play-Service-Key: $API_KEY" \
  | jq '.runtime_projection | {selected_player_role, human_actor_id, npc_actor_ids, actor_lanes, runtime_profile_id, runtime_module_id, content_module_id}' \
  | grep -E 'selected_player_role|human_actor_id|npc_actor_ids|actor_lanes'
```

All 7 fields present, non-null, non-empty. `actor_lanes` keys do not include `visitor`.

**Test Coverage:**

- `backend/tests/test_story_session_contract_backend_handoff.py::test_create_story_session_includes_actor_ownership`
- `backend/tests/test_story_session_contract_backend_handoff.py::test_human_actor_id_matches_selected_role`
- `backend/tests/test_story_session_contract_backend_handoff.py::test_actor_lanes_excludes_visitor`
- `world-engine/tests/test_story_session_contract_backend_handoff.py::test_stored_projection_has_all_required_fields`

**Error Handling:**

If backend compiles a projection without actor ownership:
1. **Readable Error:** Log to Langfuse: `"backend_handoff_contract_violation: missing human_actor_id in runtime_projection"`
2. **Failure Mode:** `create_story_session` returns 400 with body: `{"error": "runtime_projection missing required actor fields: human_actor_id, npc_actor_ids, actor_lanes"}`
3. **Mandatory Fix:** Caller must enrich projection before retry. Error is not recoverable.

**Fallback Behavior:**

None. This is a hard precondition. If backend cannot produce a valid projection, session creation fails (no silent mock fallback).

**Audit Logging:**

Every call to `create_story_session` must log to Langfuse:
```json
{
  "span": "backend.story_session_create",
  "backend_session_id": "...",
  "world_engine_story_session_id": "...",
  "runtime_projection_fields_present": ["module_id", "selected_player_role", "human_actor_id", ...],
  "actor_lanes_keys": ["annette", "veronique", "michel", "alain"],
  "actor_lanes_visitor_present": false,
  "status": "ok" | "error"
}
```

---

### Contract 2: Story Session Opening Truthfulness

**Definition:**

When a new story session is created (`create_session` in world-engine), an opening turn (Turn 0) MUST be generated, persisted, and MUST contain:

1. **Non-empty visible output:** At least one NPC has spoken, acted, or decided (not GM narration alone)
2. **Live provider/model:** Opening uses real LangGraph execution OR is explicitly marked `kind: deterministic_ldss_bootstrap` with a scheduled follow-up live turn
3. **Validation pass:** Opening's NPC agency plan and proposed output pass actor-lane validation (human actor not controlled)

**Acceptance Gate:**

```bash
# After create_story_session, verify opening in story window:
RUNTIME_SESSION_ID=$(jq -r '.runtime_session_id' /tmp/player-session-create.json)
curl -s "http://localhost:8001/api/story/sessions/$RUNTIME_SESSION_ID/state" \
  -H "X-Play-Service-Key: $API_KEY" \
  | jq '.story_window.entries[0] | {turn_number, kind, visible_output_bundle, npc_agency_plan}'
```

Gate conditions:
- `entries[0].turn_number == 0`
- `entries[0].kind == "opening"`
- `entries[0].visible_output_bundle.gm_narration` non-empty
- `entries[0].visible_output_bundle.actor_response` non-empty OR `npc_agency_plan.primary_responder_id` set
- `entries[0].diagnostics_envelope.generation.provider != "mock"` (unless explicitly `deterministic_ldss_bootstrap`)
- `entries[0].diagnostics_envelope.validation_outcome == "approved"`

**Test Coverage:**

- `world-engine/tests/test_story_session_contract_opening_truthfulness.py::test_opening_turn_exists_after_create_session`
- `world-engine/tests/test_story_session_contract_opening_truthfulness.py::test_opening_has_npc_agency`
- `world-engine/tests/test_story_session_contract_opening_truthfulness.py::test_opening_uses_live_provider_not_mock`
- `world-engine/tests/test_story_session_contract_opening_truthfulness.py::test_opening_passes_actor_lane_validation`

**Error Handling:**

If opening generation fails:
1. **Readable Error:** Log to Langfuse: `"opening_generation_failed: {reason}"`
   - Reasons: `"no_visible_npc_output"`, `"validation_rejected"`, `"provider_error"`, `"graph_execution_error"`
2. **Failure Mode:** `create_session` raises `StorySessionOpeningFailure` with context:
   ```python
   {
       "session_id": "...",
       "reason_code": "no_visible_npc_output",
       "diagnostics": {...},
       "remediation": "Check LDSS output; verify actor lanes are set; verify provider is configured"
   }
   ```
3. **Mandatory Fix:** Session is rolled back; caller receives actionable diagnostics.

**Fallback Behavior:**

If live provider is unavailable (D-009):
1. **Visible Fallback:** Mark opening `kind: deterministic_ldss_bootstrap` (not silent mock)
2. **Audit Trail:** Log to Langfuse:
   ```json
   {
     "span": "opening.fallback_to_ldss",
     "reason": "provider_unavailable",
     "provider_requested": "claude",
     "diagnostics_hint": "Check LANGFUSE_ENABLED, provider config, API keys"
   }
   ```
3. **Remediation:** Frontend shows explicit UI: "Opening generated with deterministic narrative (live AI unavailable; check system status)"

**Audit Logging:**

Every opening execution must log:
```json
{
  "span": "story.opening.execute",
  "session_id": "...",
  "turn_number": 0,
  "opening_kind": "live_graph" | "deterministic_ldss_bootstrap",
  "provider": "claude" | "ldss" | "fallback",
  "visible_output_present": true | false,
  "npc_agency_plan_set": true | false,
  "validation_status": "approved" | "rejected",
  "quality_class": "live" | "degraded" | "blocked",
  "diagnostics_envelope": {...}
}
```

---

### Contract 3: Frontend Playability and Empty-State Handling

**Definition:**

The frontend play shell MUST NOT display a session as interactive (`can_execute=true`) if `story_entries` is empty. If empty, the shell MUST:

1. Show the empty state explicitly (placeholder text)
2. Include a degradation reason from backend
3. NOT be clickable for player input

Backend MUST compute `can_execute` based on actual story window state, not independently.

**Acceptance Gate:**

```javascript
// In frontend test or browser console:
const sessionState = await fetch('/api/v1/game/player-sessions/{run_id}').then(r => r.json());
console.assert(sessionState.story_entries.length > 0 || sessionState.can_execute === false,
  `Empty story_entries but can_execute=true: GATE FAIL`);

// Empty state MUST have degradation_signals
if (sessionState.story_entries.length === 0) {
  console.assert(sessionState.degradation_signals && sessionState.degradation_signals.length > 0,
    `Empty but no degradation_signals: GATE FAIL`);
}
```

**Test Coverage:**

- `backend/tests/test_story_session_contract_playability.py::test_can_execute_false_when_story_entries_empty`
- `backend/tests/test_story_session_contract_playability.py::test_empty_state_includes_degradation_reason`
- `frontend/tests/test_play_shell_contract_playability.py::test_empty_shell_not_interactive`
- `frontend/tests/test_play_shell_contract_playability.py::test_degradation_reason_displayed`

**Error Handling:**

If backend marks `can_execute=true` but `story_entries` is empty:
1. **Readable Error:** Log to Langfuse: `"frontend_contract_violation: can_execute=true with empty story_entries"`
2. **Failure Mode:** Backend returns 400 with validation error before response is sent
3. **Mandatory Fix:** Backend logic must recompute `can_execute` based on `story_window.entry_count`

**Fallback Behavior:**

If opening failed to generate:
1. **Visible Degradation:** `can_execute=false`, placeholder shows "No opening available"
2. **Reason Code:** `degradation_signals` contains `"opening_generation_failed"`
3. **Audit Trail:** Log to Langfuse with reason code and remediation hint

**Audit Logging:**

Every session state bundle to frontend must log:
```json
{
  "span": "backend.player_session_bundle",
  "session_id": "...",
  "story_entries_count": 0,
  "can_execute": false,
  "degradation_signals": ["opening_generation_failed", "..."],
  "status": "empty" | "playable"
}
```

---

### Contract 4: Diagnostics and Observability Truthfulness

**Definition:**

Every turn (including Turn 0 opening) MUST include complete diagnostics that explain:
- **Why** the response was generated (route decision, provider, model)
- **How** it was validated (validation status, rejection reasons if any)
- **What** was committed (commit reason, visible output)
- **Where** it might have degraded (fallback markers, quality class)

Diagnostics construction errors MUST NOT be swallowed. Missing diagnostics is a turn failure.

**Acceptance Gate:**

```bash
# For any turn, verify diagnostics envelope:
curl -s "http://localhost:8001/api/story/sessions/$RUNTIME_SESSION_ID/diagnostics" \
  -H "X-Play-Service-Key: $API_KEY" \
  | jq '.diagnostics[-1] | {
      turn_number,
      visible_response_source,
      generation.provider,
      generation.model,
      validation_outcome,
      quality_class,
      degradation_signals,
      fallback_used
    }'
```

All fields present, non-null. No `generation.provider == "unknown"`. No `validation_outcome == null`.

**Test Coverage:**

- `world-engine/tests/test_story_session_contract_diagnostics.py::test_diagnostics_envelope_complete`
- `world-engine/tests/test_story_session_contract_diagnostics.py::test_visible_response_source_set`
- `world-engine/tests/test_story_session_contract_diagnostics.py::test_generation_provider_and_model_set`
- `world-engine/tests/test_story_session_contract_diagnostics.py::test_validation_outcome_set`
- `world-engine/tests/test_story_session_contract_diagnostics.py::test_fallback_markers_when_applicable`

**Error Handling:**

If diagnostics envelope construction throws:
1. **Fail Fast:** Do NOT swallow with `except Exception: pass`
2. **Readable Error:** Log to Langfuse: `"diagnostics_construction_error: {exception}"`
3. **Failure Mode:** Turn execution fails; session returns 500 with diagnostics error
4. **Mandatory Fix:** Diagnostics code must be corrected; retry is not automatic

If `visible_response_source` is missing:
1. **Readable Error:** `"missing_visible_response_source"`
2. **Failure Mode:** Turn marked `quality_class: blocked`; visible output suppressed
3. **Mandatory Fix:** Generation or render node must set `visible_response_source`

**Fallback Behavior:**

If provider fails (D-009):
1. **Fallback to Mock:** Use mock adapter to generate placeholder output
2. **Visibility:** Set `fallback_used: true` and `fallback_reason: "provider_unavailable"`
3. **Audit Trail:** Log provider error, fallback decision, and remediation hint
4. **Degradation:** Mark `quality_class: degraded`; output is shown but flagged

**Audit Logging:**

Every turn diagnostics must include:
```json
{
  "span": "story.turn.execute",
  "session_id": "...",
  "turn_number": N,
  "turn_kind": "opening" | "player_turn",
  "visible_response_source": "live_generation" | "ldss_deterministic" | "fallback_mock",
  "generation": {
    "provider": "claude" | "ldss" | "mock",
    "model": "claude-opus-4-7" | "deterministic" | "mock",
    "adapter_invocation_mode": "live_langchain" | "ldss_direct" | "mock_fallback"
  },
  "validation": {
    "actor_lane_status": "approved" | "rejected",
    "actor_lane_reason": "...",
    "validation_status": "approved" | "rejected",
    "rejection_reason": "..."
  },
  "commit": {
    "commit_reason_code": "...",
    "committed": true | false
  },
  "quality": {
    "quality_class": "live" | "degraded" | "blocked",
    "degradation_signals": ["..."]
  },
  "fallback": {
    "fallback_used": true | false,
    "fallback_reason": "...",
    "remediation_hint": "..."
  }
}
```

---

### Contract 5: Narrative Streaming Integration

**Definition:**

If a turn is marked for narrative streaming (incremental NPC narration delivery), the backend MUST:

1. Include `narrator_streaming: true` in the JSON response
2. Provide the correct SSE endpoint for the frontend to open an EventSource
3. Ensure the endpoint is proxied or publicly accessible from the frontend origin

The frontend MUST:

1. Detect `narrator_streaming: true` in the turn response
2. Open the correct EventSource URL
3. Stream blocks to the player as they arrive

**Acceptance Gate:**

```bash
# 1. Verify Turn Response includes narrator_streaming:
curl -s -H "Authorization: Bearer $TOKEN" \
  "http://localhost:8000/api/v1/game/player-sessions/$RUN_ID/turns" \
  -X POST -d '{"player_input":"..."}' \
  | jq '.narrator_streaming'
# Expected: true (if applicable)

# 2. Verify SSE endpoint is accessible:
curl -i "http://localhost:5002/api/v1/game/player-sessions/$RUN_ID/stream-narrator"
# Expected: HTTP 200 (EventSource open), not 404 or 502
```

**Test Coverage:**

- `backend/tests/test_story_session_contract_streaming.py::test_turn_response_includes_narrator_streaming_flag`
- `backend/tests/test_story_session_contract_streaming.py::test_sse_endpoint_proxied_correctly`
- `frontend/tests/test_play_shell_contract_streaming.py::test_detects_narrator_streaming_flag`
- `frontend/tests/test_play_shell_contract_streaming.py::test_opens_correct_sse_url`

**Error Handling:**

If narrator streaming is requested but endpoint unavailable:
1. **Readable Error:** Log to Langfuse: `"narrator_streaming_endpoint_unavailable"`
2. **Fallback Mode:** Return `narrator_streaming: false` with full turn response (blocks arrive in JSON, not streamed)
3. **Audit Trail:** Log why streaming failed; suggest remediation

**Fallback Behavior:**

If SSE endpoint is not accessible:
1. **Visible Fallback:** `narrator_streaming: false` in response
2. **Delivery Method:** All blocks in single JSON response
3. **Audit Trail:** Log to Langfuse with reason (proxy misconfiguration, endpoint down, etc.)
4. **Remediation Hint:** "Check PLAY_SERVICE_URL configuration; verify SSE endpoint is accessible from frontend origin"

**Audit Logging:**

Every turn with streaming must log:
```json
{
  "span": "backend.narrator_streaming",
  "session_id": "...",
  "turn_number": N,
  "narrator_streaming_requested": true,
  "narrator_streaming_available": true | false,
  "sse_endpoint": "/api/v1/...",
  "fallback": "none" | "json_blocks",
  "blocks_streamed": 0..N | null,
  "blocks_json": 0..N | null
}
```

---

## Defect Mapping — Which Contract Fixes Each Defect

| Defect | Severity | Contract(s) | How Fixed |
|--------|----------|-------------|-----------|
| **D-001** | BLOCKER | Contract 1 | Backend preserves actor ownership fields in projection |
| **D-002** | HIGH | Contract 2 | Opening explicitly marks live vs deterministic; both are valid |
| **D-003** | HIGH | Contract 2, 4 | Opening validation checks `visible_actor_response_present` before approval |
| **D-004** | HIGH | Contract 2 | State-only test paths removed from production manager path |
| **D-005** | MEDIUM | Contract 3 | Frontend verifies `story_entries` non-empty before rendering shell |
| **D-006** | HIGH | Contract 3 | Backend computes `can_execute` from `story_window.entry_count` |
| **D-007** | BLOCKER | Contract 1 | Same as D-001; backend handoff is unified |
| **D-008** | MEDIUM | Contract 5 | Backend forwards `narrator_streaming` flag; frontend SSE wired |
| **D-009** | HIGH | Contract 2, 4 | Provider route health enforced; fallback to mock is visible |
| **D-010** | HIGH | Contract 4 | False-green tests separated from live gates; new E2E gate added |
| **D-011** | LOW | Contract 1 | Actor lanes exclude `visitor`; legacy demo UI cleaned |
| **D-012** | MEDIUM | Contract 4 | Test docstrings updated to describe actual coverage (unit vs live) |

---

## Consequences

1. **Development:** All new code touching story sessions, openings, or diagnostics MUST satisfy one of the 5 contracts. Code review checklists will include contract checks.

2. **Testing:** Tests are classified as:
   - **Unit/Mocked:** Prove isolated component behavior (valid, but never labeled "live")
   - **Integration:** Prove real frontend→backend→world-engine path (required for MVP4 gate)
   - **E2E:** Prove create→opening→turn→diagnostics end-to-end (gate for MVP4)

3. **Monitoring:** Langfuse traces for every turn MUST include all contract audit logging. Missing traces are gate failures.

4. **Fallback Policy:** Fallbacks to mock are acceptable **only if visibly marked and logged**. Silent fallbacks violate contracts.

5. **Onboarding:** New team members receive this ADR as part of MVP4 onboarding. "How do we know the runtime is live?" → "Check the 5 contracts."

---

## References

- `live_runtime_empty_session_audit.md` — Audit of 12 defects (source truth)
- `backend/app/api/v1/session_routes.py` — Backend story session handoff
- `world-engine/app/story_runtime/manager.py` — Story session create/turn execution
- `world-engine/app/observability/langfuse_adapter.py` — Audit logging
- `ai_stack/live_dramatic_scene_simulator.py` — LDSS and opening
- `frontend/app/routes_play.py` — Frontend shell lifecycle

