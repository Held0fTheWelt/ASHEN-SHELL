# API and MCP Integration Surfaces

## Backend API Surface Family

The backend exposes four API families:

### Family 1: Publish and Content Activation
**Owner:** `backend/api/publish.py`

**Endpoints:**

```
POST /api/v1/content/publish
  Input: {module_id, content_ref, snapshot}
  Output: {publish_id, status, gate_results}
  Gate checks: consistency, rule validation, continuity binding
  Auth: publisher role only

GET /api/v1/content/published
  Input: {module_id, version}
  Output: {published_artifacts, snapshots}
  Auth: session creation only

POST /api/v1/content/activate
  Input: {publish_id}
  Output: {status, previous_active_version}
  Auth: publisher role only

POST /api/v1/content/rollback
  Input: {module_id, target_version}
  Output: {status, new_active_version}
  Auth: publisher + supervisor approval

GET /api/v1/content/gates/{publish_id}
  Input: {publish_id}
  Output: {gate_results, evidence}
  Auth: publisher role only
```

**Data flow:** Writers room → publish request → gate checks → published record → sessions use published content

**Authority:** Only content with passing gates may be published. Non-published content is invisible to sessions.

### Family 2: Session Management
**Owner:** `backend/api/session_api.py`

**Endpoints:**

```
POST /api/v1/sessions/create
  Input: {player_id, module_id}
  Output: {session_id, content_snapshot, initial_state}
  Precondition: module_id has published content
  Auth: authenticated player

GET /api/v1/sessions/{session_id}
  Input: {session_id}
  Output: {session_metadata, status, current_world_state}
  Auth: session owner or operator

POST /api/v1/sessions/{session_id}/turn
  Input: {session_id, player_action}
  Output: {turn_id, visible_output, new_state}
  Precondition: session is active
  Auth: session owner

POST /api/v1/sessions/{session_id}/pause
  Input: {session_id, reason}
  Output: {status}
  Auth: session owner or operator

GET /api/v1/sessions/{session_id}/archive
  Input: {session_id}
  Output: {turn_log, governance_log, final_state}
  Auth: session owner or operator
```

**Data flow:** Session create locks content snapshot → Turn input → Turn execution → Visible output returned → Session state updated

**Authority:** Session content is immutable for the session's lifetime. Sessions cannot see non-published content.

### Family 3: Governance and Operator Actions
**Owner:** `backend/api/governance_api.py`

**Endpoints:**

```
POST /api/v1/governance/override
  Input: {session_id, turn_id, override_type, justification}
  Overrides: validation, state_correction
  Output: {override_id, status}
  Auth: operator role, with supervisor approval

POST /api/v1/governance/rollback
  Input: {session_id, target_turn}
  Output: {status, new_session_state}
  Auth: operator + supervisor approval

POST /api/v1/governance/diagnostics
  Input: {session_id, turn_id}
  Output: {full_diagnostics_payload}
  Auth: operator role only

POST /api/v1/governance/consistency_check
  Input: {session_id}
  Output: {check_results, flags, recommendations}
  Auth: operator role only

POST /api/v1/governance/intervention_log
  Input: {session_id}
  Output: {all_operator_interventions, evidence}
  Auth: operator role only
```

**Data flow:** Operator detects issue → requests diagnostics → makes intervention decision → intervention is recorded with audit trail

**Authority:** Operators can override validation or correct state, but all actions are recorded and auditable.

### Family 4: Diagnostics and Queries
**Owner:** `backend/api/diagnostics_api.py`

**Endpoints:**

```
GET /api/v1/diagnostics/sessions/active
  Input: {filter_module, limit}
  Output: [{session_id, status, pressure_state, last_activity}]
  Auth: operator role only

GET /api/v1/diagnostics/turn/{turn_id}
  Input: {turn_id}
  Output: {full_turn_diagnostics}
  Auth: session owner or operator

GET /api/v1/diagnostics/character/{session_id}/{actor_id}
  Input: {session_id, actor_id}
  Output: {character_state, turn_history, relationships}
  Auth: session owner or operator

GET /api/v1/diagnostics/pressure
  Input: {session_id}
  Output: {pressure_timeline, dominant_pressure_per_turn}
  Auth: session owner or operator

GET /api/v1/diagnostics/consistency
  Input: {session_id}
  Output: {consistency_check_results}
  Auth: session owner or operator
```

**Data flow:** Operator/player queries → backend retrieves diagnostic data → formatted response returned

**Authority:** Diagnostics are read-only. They inform but do not change state directly (except via explicit override endpoints).

---

## MCP Control-Plane Surface

The Model Context Protocol (MCP) surfaces control-plane operations for orchestrated AI support.

### MCP Tools Available to Model
(During proposal generation only)

**Tool 1: retrieval_search**
```
Input: {query, context_type (character|scene|rule)}
Output: [{result, source_reference}]
Bounds: Searches published content only; cannot access writers room
Purpose: Model retrieves context about characters/scenes/rules
Rate limit: 5 calls per turn
```

**Tool 2: character_voice_guidance**
```
Input: {actor_id}
Output: {voice_patterns, speech_examples, pressure_response_style}
Bounds: Returns public character profiles (no private thoughts)
Purpose: Model gets voice guidance for dialogue generation
Rate limit: 3 calls per turn
```

**Tool 3: rule_query**
```
Input: {scene_id, rule_type}
Output: {applicable_rules, constraints}
Bounds: Returns only rules relevant to current scene/pressure state
Purpose: Model learns what proposals will pass validation
Rate limit: 2 calls per turn
```

**Tool 4: validation_test**
```
Input: {proposed_effects, scene_context}
Output: {would_pass, failing_rules}
Bounds: Dry-run; does not commit; shows what would fail
Purpose: Model can test proposals before committing to one
Rate limit: 1 call per turn (high cost due to rule engine load)
```

### MCP Control-Plane Policies

**Policy 1: Knowledge Cutoff**
- Model does not know about player history (surprise is preserved)
- Model only knows: current scene, character profiles, applicable rules
- Model learns player's move when proposal seam executes

**Policy 2: Authority Boundary**
- Model can propose; cannot commit
- Model output is staging only; validation seam decides
- If proposal is rejected, model does not see why (prevents gaming validation)

**Policy 3: Orchestration Boundary**
- Model cannot call operators or human services
- Model cannot trigger rollbacks or overrides
- Model cannot modify session state directly

All orchestration decisions require explicit seam execution (proposal → validation → commit).

---

## Query Surface Boundary

Players access limited query surface:

**Query 1: "Who is here?"**
```
GET /api/v1/query/scene_state
Output: {present_characters, visible_objects, room_description}
Bounds: Only returns what player would perceive
Auth: session owner
```

**Query 2: "What happened?"**
```
GET /api/v1/query/recent_events
Output: {last_5_turns_summary, key_facts_established}
Bounds: Only returns what player's character would know
Auth: session owner
```

**Query 3: "What can I do?"**
```
GET /api/v1/query/available_actions
Output: {action_suggestions, consequences_of_each}
Bounds: Suggestions based on current scene/pressure state
Auth: session owner
```

All query responses are bounded by what the player's character would know.

---

## Data Flow Through API Boundaries

### New Session Request
```
Player requests session
  ↓
POST /api/v1/sessions/create
  ↓
Backend verifies published content exists
  ↓
world-engine initializes with content snapshot
  ↓
Session created; initial world state returned
  ↓
Player sees opening scene
```

**Authority checkpoint:** Only published content is loaded.

### Turn Execution
```
Player submits action
  ↓
POST /api/v1/sessions/{id}/turn
  ↓
world-engine executes turn (all 4 seams)
  ↓
world-engine calls MCP for retrieval/guidance
  ↓
MCP returns bounded data (published content only)
  ↓
Model generates proposal (staging only)
  ↓
Validation seam checks proposal
  ↓
Commit seam applies approved effects
  ↓
Render seam projects to player-visible output
  ↓
Turn result returned to player
  ↓
Session state updated
```

**Authority checkpoints:**
- Content is published-only
- Proposal is staging-only
- Validation gates must pass
- Commit is sole truth authority
- Render is projection-only

### Operator Override
```
Operator detects issue
  ↓
GET /api/v1/diagnostics/turn/{turn_id}
  ↓
Operator reviews diagnostics
  ↓
Operator decides to override validation
  ↓
POST /api/v1/governance/override with justification
  ↓
Backend logs override with audit trail
  ↓
Proposed effects are committed despite validation rejection
  ↓
All future turns use corrected state
```

**Authority checkpoint:** Override is recorded; future analysis can see why state was changed.

---

## Acceptance Criteria

API surfaces are correct when:

1. **Four API families are complete** (publish, session, governance, diagnostics)
2. **MCP tools are bounded** (model cannot access writers room, cannot commit, cannot modify state)
3. **Query surface is bounded** (player only sees what their character would know)
4. **All data flows have authority checkpoints** (content published, proposals validated, commits recorded)
5. **Authentication is enforced** (operator tools require operator auth; governance tools require approval gates)
6. **Audit trails are complete** (all interventions recorded with reason and evidence)
7. **No silent mutations** (all state changes are explicit and traceable)

All criteria must be met for Phase 4 acceptance.

