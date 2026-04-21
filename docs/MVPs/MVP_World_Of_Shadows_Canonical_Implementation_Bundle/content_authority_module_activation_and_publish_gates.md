# Content Authority, Module Activation, and Publish Gates

## Canonical Content Authority

The YAML module tree at `content/modules/god_of_carnage/` is the **canonical source for all God of Carnage content**. All other artifacts (builtins, writers-room, fallbacks) are secondary and must not silently override YAML truth.

### Content Hierarchy

1. **YAML Module Definition** (primary authority)
   - Location: `content/modules/god_of_carnage/goc_module.yaml`
   - Defines: Character roster, scene structure, dramatic rules, pressure vectors
   - Status: This is the truth; runtime code must respect these definitions

2. **Builtin Artifacts** (secondary)
   - Location: `content/builtins/god_of_carnage/`
   - Purpose: Fallback content for proposals, character voice templates
   - Governance: May only be used if YAML content is missing; must not override YAML

3. **Writers-Room Artifacts** (secondary)
   - Location: `backend/writers_room/god_of_carnage/`
   - Purpose: Review/staging content; not activated unless explicitly published
   - Governance: Writers-room changes do not affect runtime until published

4. **Published Artifacts** (activation boundary)
   - Location: `backend/published_content/god_of_carnage/`
   - Status: These are the only artifacts runtime may consume
   - Governance: Non-published content is invisible to running sessions

### Authority Precedence Rule

When multiple sources define the same entity:

```
YAML > Published snapshots > Writers-room staging > Builtins
```

Code path: `content/backend_loader.py` implements this precedence by:
1. Loading YAML module as base truth
2. Checking `backend/published_content/` for activated overrides
3. Falling back to builtins only if neither YAML nor published content exists
4. Never silently accepting writers-room content into runtime

---

## Module Discovery and Loading Flow

### Load-Time Authority Verification

When a session starts:

1. **Module Request** → `backend/api/session_api.py`
2. **Publish Check** → Query published content registry
   - Location: `backend/db/published_modules.py`
   - Enforces: Only modules with explicit published record may be used
3. **Content Load** → `content/backend_loader.py`
   - Reads YAML from `content/modules/god_of_carnage/`
   - Applies published override snapshots if available
   - Injects builtins only for missing entities
4. **Runtime Injection** → `world-engine/app/story_runtime_shell.py`
   - Session receives loaded module
   - Runtime never re-loads; content is locked for session lifetime

### Content Mutation Prevention

Once a session is running:

- **No live content reloading** — Session holds a snapshot; mid-session changes to YAML are invisible
- **No writer-room injection** — Even if writers room updates, session ignores them
- **No silent fallback switches** — If published content becomes unavailable mid-session, error is explicit; fallback is not automatic

This prevents drift between authored intent and player-visible truth.

---

## Activation Boundary Contract

Content may only be used at runtime if it has an explicit published record.

### Publish State Diagram

```
Writers Room (draft)
     ↓
   [Review]
     ↓
Published Record (activated)
     ↓
Runtime Session (locked snapshot)
```

### Publish Record Schema

Every published piece of content has:

```json
{
  "publish_id": "uuid",
  "module_id": "god_of_carnage",
  "content_type": "character|scene|rule|dialogue_template",
  "content_ref": "path/in/yaml",
  "timestamp": "ISO-8601",
  "published_by": "user_id",
  "snapshot": {
    "yaml_source": "...",
    "builtins_version": "...",
    "override_overrides": {...}
  },
  "status": "active|archived|rollback",
  "gate_compliance": {
    "passed_gates": ["consistency_check", "rule_validation"],
    "failed_gates": [],
    "gate_evidence": [...]
  }
}
```

### Publish Validation Gates (P0 Must Pass)

Before content can be published, these gates must pass:

#### Gate 1: Consistency Check
- **What it checks:** Content does not contradict published scene/character definitions
- **Implementation:** `backend/publish_gates/consistency_gate.py`
- **Failure:** Publish is blocked; evidence is returned to author
- **Evidence:** Side-by-side comparison of new vs. existing published content

#### Gate 2: Rule Validation
- **What it checks:** Content complies with dramatic rules (scene function validity, pressure vectors, character role compatibility)
- **Implementation:** `backend/publish_gates/rule_validation_gate.py`
- **Failure:** Publish is blocked; violations are listed
- **Evidence:** Rule engine output showing which rules are violated

#### Gate 3: Continuity Binding
- **What it checks:** If content references scene consequences or character history, those references are resolvable
- **Implementation:** `backend/publish_gates/continuity_gate.py`
- **Failure:** Publish is blocked; missing references are listed
- **Evidence:** Graph of unresolved references

### Rollback and Activation Controls

Published content has explicit versioning:

- **Active version:** Currently used by running sessions
- **Previous version:** Available for rollback if issues are discovered
- **Staged version:** Published but not yet active (for A/B testing or gradual rollout)

#### Activation Commands

```
publish_activate(content_id) 
  → Sets status to "active"
  → New sessions use this content
  → Running sessions keep snapshot (unaffected)
  → Audit: logged with timestamp and user
  
publish_rollback(content_id, previous_version)
  → Sets status to "archived"
  → Restores previous_version to "active"
  → New sessions switch to previous version
  → Running sessions keep snapshot (unaffected)
  → Audit: logged with rollback reason
```

---

## Content Authority Proof

### Why YAML Wins (Code Evidence)

Location: `content/backend_loader.py`

```python
def load_module_content(module_id, session_id):
    # Step 1: Load YAML as base truth
    yaml_content = load_yaml(f"content/modules/{module_id}/")
    
    # Step 2: Check if published overrides exist
    published = get_published_snapshot(module_id, session_id)
    if published:
        # Apply overrides, but only for fields that were explicitly published
        yaml_content = merge_published_overrides(yaml_content, published)
    
    # Step 3: Inject builtins ONLY for missing entities
    for entity_type in ["characters", "scenes", "rules"]:
        for entity_id, entity_data in yaml_content[entity_type].items():
            if not entity_data.get("content"):
                builtin_content = get_builtin(entity_type, entity_id)
                if builtin_content:
                    entity_data["content"] = builtin_content
                    entity_data["_source"] = "builtin"
    
    # Never, ever silently accept writer-room content
    writers_room = get_writers_room_draft(module_id)
    if writers_room.exists() and not is_published(writers_room):
        log_warning(f"Writers-room draft exists but is not published: {writers_room}")
        # Continue with YAML/published; draft is ignored
    
    return yaml_content
```

This code proves that:
1. YAML is always loaded first
2. Published overrides are applied on top
3. Builtins fill gaps only (never override)
4. Writers-room drafts are explicitly ignored at runtime

---

## Acceptance Criteria

Content authority is correct when:

1. **YAML module is loadable** → No syntax errors; all required fields present
2. **Published content is versioned** → Every published piece has a snapshot with timestamp
3. **Publish gates all passed** → Consistency, rules, and continuity checks are recorded
4. **No writers-room leakage** → Runtime code never reads writers-room content directly
5. **Precedence is enforced** → Code audit shows YAML > published > builtins order
6. **Activation is explicit** → All publish/rollback actions are logged with evidence
7. **Session snapshots are locked** → Running sessions ignore content changes; snapshot is frozen

---

## Non-Compliance Degradation

If content authority boundaries are violated:

- **YAML missing required field** → Publish gate fails; admin must fix YAML before publish is allowed
- **Publish gate fails** → Content is not published; sessions cannot use it; error is explicit
- **Writer-room sneaks into runtime** → Bug; code audit finds this and blocks it
- **Session sees mid-session content change** → Session continues with snapshot; new sessions pick up change; old sessions are not affected
- **Rollback needed** → Admin runs `publish_rollback()`, new sessions switch to previous version, running sessions keep snapshot

All boundary violations are audited. No silent content mutation.

