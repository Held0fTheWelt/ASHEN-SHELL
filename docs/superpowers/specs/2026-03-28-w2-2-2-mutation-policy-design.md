# W2.2.2: Field-Level Mutation Whitelist & Protected-State Rules

**Goal:** Harden AI mutation validation by enforcing an explicit deny-by-default whitelist of mutable state fields, protecting runtime/engine/session identity from AI proposals.

**Architecture:** Separate mutation policy concerns from validation plumbing. New `mutation_policy.py` defines semantic domains and path-pattern rules; `validators.py` orchestrates validation and calls policy enforcement.

**Scope:** W2.2.2 subsection only — mutation permission validation. Does not redesign state model, add UI, or introduce module-specific hacks.

---

## Problem Statement

W2.2.1 established a canonical action taxonomy (6 action types). However, **path validity does not imply mutation permission**:
- Current validation checks path syntax and entity existence only
- No protection against mutating session_id, execution_mode, event logs, or engine-owned state
- "Valid path" ≠ "allowed mutation" — the gap this work closes

W2.2.2 closes this gap by:
1. Defining which canonical state fields AI is *allowed* to mutate (whitelist)
2. Defining which fields are *protected* (deny-by-default)
3. Enforcing mutation permission in the validation pipeline, before state application

---

## Design

### Semantic Field Catalog

**Allowed Domains** — AI may mutate these areas:
- `characters` — character emotional state, stance, tension
- `relationships` — relationship axis values
- `scene_state` — scene-level conflict/pressure markers
- `conflict_state` — escalation/intensity trackers

**Protected Domains** — AI may never mutate these areas:
- `metadata` — internal metadata fields
- `runtime` — execution state, mode, adapter configuration
- `system` — engine bookkeeping
- `logs` — event logs, decision logs (immutable audit trail)
- `decision` — AI decision artifacts
- `session` — session_id, created_at, module_id, module_version
- `turn` — turn_number, session_id
- `cache` — derived/computed fields
- Technical patterns: `*._*`, `*.__*`, `*_internal`, `*_derived`

### Path-Pattern Rules

**Whitelist Rules** (patterns AI may mutate, within allowed domains):
```
characters.*.emotional_state
characters.*.stance
characters.*.tension
relationships.*.value
scene_state.*.pressure
scene_state.*.conflict
conflict_state.*.escalation
conflict_state.*.intensity
```

**Blocked Rules** (patterns always protected, global):
```
*.metadata
*._*
*.__*
runtime.*
system.*
logs.*
decision.*
session.*
turn.*
cache.*
*_internal
*_derived
```

### Core Enforcement Functions

**File:** `backend/app/runtime/mutation_policy.py`

```python
class MutationPolicy:
    """Defines canonical AI mutation permission rules."""

    ALLOWED_DOMAINS = {"characters", "relationships", "scene_state", "conflict_state"}
    PROTECTED_DOMAINS = {"metadata", "runtime", "system", "logs", "decision", "session", "turn", "cache"}

    WHITELIST_PATTERNS = [
        "characters.*.emotional_state",
        "characters.*.stance",
        "characters.*.tension",
        "relationships.*.value",
        "scene_state.*.pressure",
        "scene_state.*.conflict",
        "conflict_state.*.escalation",
        "conflict_state.*.intensity",
    ]

    BLOCKED_PATTERNS = [
        "*.metadata",
        "*._*",
        "*.__*",
        "runtime.*",
        "system.*",
        "logs.*",
        "decision.*",
        "session.*",
        "turn.*",
        "cache.*",
        "*_internal",
        "*_derived",
    ]

    @staticmethod
    def is_mutation_allowed(target_path: str) -> tuple[bool, str | None]:
        """Check if a target path is allowed to be mutated by AI.

        Returns (allowed, reason) where reason is None if allowed, or error message if blocked.
        Deny-by-default: only whitelisted patterns are allowed.
        """
        ...

    @staticmethod
    def get_protection_reason(target_path: str) -> str | None:
        """Get the protection reason if a path is blocked, else None."""
        ...
```

### Integration into Validation Pipeline

**File:** `backend/app/runtime/validators.py`

New function:
```python
def validate_mutation_permission(target_path: str) -> tuple[bool, str | None]:
    """Validate that AI is permitted to mutate the target path.

    Called after path-existence validation, before state mutation.
    Checks against MutationPolicy whitelist/blocked patterns.
    """
    from app.runtime.mutation_policy import MutationPolicy
    return MutationPolicy.is_mutation_allowed(target_path)
```

Updated validation flow in `_validate_delta()`:
```
1. Check target field exists and is string
2. Check path format (dot-notation)
3. Check path exists in canonical_state  ← existing
4. Check mutation permission           ← NEW: validate_mutation_permission()
5. If blocked: add to rejected_deltas
6. If allowed: proceed to state application
```

### Error Handling

Rejected mutations:
- Visible in `TurnExecutionResult.rejected_deltas`
- Error message: `"Mutation blocked: target_path '<path>' is protected (reason: <protection_reason>)"`
- Logged in validation outcome with explicit reason
- Audit trail preserved in `AIDecisionLog`

Example rejection:
```
target_path: "session.status"
error: "Mutation blocked: target_path 'session.status' is protected (protected domain: session)"
result: rejected_delta with explicit reason
```

### Testing Strategy

**File:** `backend/tests/runtime/test_mutation_policy.py`

Test classes:
1. **TestMutationPolicyWhitelist** — verify allowed patterns are accepted
2. **TestMutationPolicyBlocked** — verify blocked patterns are rejected
3. **TestProtectedDomains** — verify protected domains cannot be mutated
4. **TestPermissionVsPathValidity** — verify path can exist but mutation still blocked
5. **TestIntegration** — mutations flow through full validation pipeline

Key test cases:
- ✅ `characters.veronique.emotional_state` — allowed
- ❌ `session.status` — protected domain
- ❌ `characters.veronique._internal_flag` — internal field
- ❌ `canonical_state.metadata.created_at` — protected metadata
- ✅ Path exists but mutation blocked (valid path ≠ allowed mutation)
- ✅ Rejected mutations visible in `TurnExecutionResult`

---

## Implementation Plan

### Phase 1: Define Policy
1. Create `mutation_policy.py` with semantic domains and pattern rules
2. Implement pattern-matching logic (whitelist, blocked rules)
3. Add policy enforcement functions

### Phase 2: Integrate Validation
1. Add `validate_mutation_permission()` to `validators.py`
2. Call policy in `_validate_delta()` validation chain
3. Reject mutations before state application

### Phase 3: Testing
1. Write comprehensive test suite (`test_mutation_policy.py`)
2. Verify whitelist/blocked patterns work correctly
3. Verify integration with full validation pipeline
4. Ensure no regressions in existing tests

### Phase 4: Integration Verification
1. Run full test suite to ensure no regressions
2. Verify `TurnExecutionResult` captures rejected mutations
3. Verify error messages are clear and actionable

---

## Acceptance Criteria

- ✅ New `mutation_policy.py` defines canonical semantic domains
- ✅ Deny-by-default whitelist enforces mutation permission
- ✅ Protected domains cannot be mutated (session, turn, logs, engine metadata)
- ✅ Path validity is checked separately from mutation permission
- ✅ Rejected mutations are visible in validation outcomes
- ✅ Integration tests verify full pipeline works
- ✅ No regressions in existing test suite
- ✅ Implementation stays within W2.2.2 scope

---

## What's Deferred to W2.2.3+

- Role-based mutation permissions (admin vs AI)
- Module-specific mutation policies (God of Carnage custom rules)
- Dynamic policy loading/validation
- Audit logging of rejected mutations to persistent store
- UI for policy visualization
- Mutation audit trail analytics

---

## Files to Create/Modify

**Create:**
- `backend/app/runtime/mutation_policy.py` — Policy definition and enforcement
- `backend/tests/runtime/test_mutation_policy.py` — Comprehensive test suite

**Modify:**
- `backend/app/runtime/validators.py` — Integrate policy validation

---

## Commit Message

```
feat(w2): enforce field-level mutation whitelist and protected state rules

Define canonical semantic domains (characters, relationships, scene_state, conflict_state)
and enforce deny-by-default mutation permission in validation pipeline.

Protected domains (session, turn, logs, runtime, system, metadata) cannot be mutated
by AI proposals. Path validity is checked separately from mutation permission.

Rejected mutations remain visible in validation outcomes for audit trail.
```
