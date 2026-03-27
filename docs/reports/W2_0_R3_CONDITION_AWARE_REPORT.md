# Enhancement Report: W2.0-R3 Condition-Aware Next Situation Derivation

**Version**: 0.1.0
**Date**: 2026-03-27
**Status**: ✅ COMPLETE — Condition-aware derivation implemented and tested

---

## Executive Summary

W2.0-R3 extends next-situation derivation to evaluate module-defined transition and ending conditions instead of only handling unconditional cases.

**Previous limitation**: Only transitions/endings with empty `trigger_conditions` could fire.
**New capability**: Conditional transitions and endings now evaluate against detected triggers.

**Design**: Optional `detected_triggers` parameter maintains backward compatibility while enabling condition evaluation.

**Tests**: 4 new focused tests verify conditional transitions, conditional endings, multi-condition logic, and backward compatibility.
**Result**: 139/139 tests passing (135 existing + 4 new).

---

## Problem Statement

The W2.0.5 implementation only supported unconditional transitions and endings:

```python
# Old: Only handled empty trigger_conditions
if not ending.trigger_conditions:
    return True  # Always fires
return False     # Never fires (conditions present)
```

This meant:
- ❌ Real God of Carnage transitions (with conditions) couldn't fire
- ❌ Conditional endings were inaccessible
- ❌ Complex narrative rules couldn't be expressed
- ❌ System collapses to "continue" when conditions aren't met

---

## Solution

### 1. Extended Function Signatures

Added optional `detected_triggers: list[str] | None = None` parameter to:
- `derive_next_situation()` — Main entry point
- `_check_ending_condition()` — Ending evaluation
- `_check_transition_condition()` — Transition evaluation

This maintains backward compatibility while enabling condition evaluation.

### 2. Condition Evaluation Logic

**For unconditional rules** (empty `trigger_conditions`):
- Always fire (same as before)
- No `detected_triggers` needed

**For conditional rules** (non-empty `trigger_conditions`):
- Require ALL conditions to be detected
- Evaluate: `all(cond_id in detected_triggers for cond_id in trigger_conditions)`
- Fire only if all conditions match

**When `detected_triggers` not provided**:
- Unconditional rules work normally
- Conditional rules cannot fire (backward compatible)

### 3. Updated next_situation.py

**File**: `backend/app/runtime/next_situation.py:40-180`

**Key changes**:

```python
# Updated signatures
def derive_next_situation(
    session: SessionState,
    module: ContentModule,
    detected_triggers: list[str] | None = None,  # NEW
) -> NextSituation:
    ...
    if _check_ending_condition(ending, session, detected_triggers):
        ...
    if _check_transition_condition(transition, session, module, detected_triggers):
        ...

# Updated evaluation
def _check_ending_condition(ending, session, detected_triggers=None) -> bool:
    # Unconditional: always fire
    if not ending.trigger_conditions:
        return True

    # Conditional: all must be detected
    if detected_triggers is not None:
        return all(c in detected_triggers for c in ending.trigger_conditions)

    # Conditions present but no triggers provided: cannot fire
    return False

def _check_transition_condition(transition, session, module, detected_triggers=None) -> bool:
    if transition.to_phase not in module.scene_phases:
        return False

    if not transition.trigger_conditions:
        return True

    if detected_triggers is not None:
        return all(c in detected_triggers for c in transition.trigger_conditions)

    return False
```

---

## Test Coverage

### New Tests Added

**File**: `backend/tests/runtime/test_next_situation.py` (new class: `TestConditionAwareNextSituation`)

| Test | Purpose | Validates |
|------|---------|-----------|
| `test_conditional_transition_triggered_with_conditions_satisfied` | Conditional transition | Fires when all trigger conditions detected |
| `test_conditional_ending_triggered_with_conditions_satisfied` | Conditional ending | Terminal state when all conditions detected |
| `test_multiple_condition_transition_requires_all_conditions` | Multi-condition logic | ALL conditions required, not ANY |
| `test_backward_compatibility_unconditional_still_works` | Backward compatibility | God of Carnage unconditional cases still work |

**Test Results**: 4/4 PASSED

### Examples from Tests

**Conditional Transition**:
```
Module: scene_a →[escalation]→ scene_b
Detected triggers: []          → Continue in scene_a ✓
Detected triggers: [escalation] → Transition to scene_b ✓
```

**Conditional Ending**:
```
Module: total_breakdown → catastrophic_end
Detected triggers: []                 → Continue ✓
Detected triggers: [total_breakdown]  → Ending reached ✓
```

**Multi-Condition Transition**:
```
Module: scene_1 →[anger, betrayal]→ scene_2
Detected: [anger]           → Continue (betrayal missing)
Detected: [anger, betrayal] → Transition (all present) ✓
```

### Regression Testing

All existing tests pass unchanged (135/135):
- 27 W2.0.1 runtime model tests
- 22 W2.0.2 session start tests
- 48 W2.0.3 turn executor tests
- 19 W2.0.4 event logging tests
- 10 W2.0.5 next situation tests
- 4 W2.0-R1 failure path tests
- 5 W2.0-R2 scene validation tests

**Total**: 139/139 PASSED (135 existing + 4 new)

---

## Condition Model Supported

### Trigger-Based Conditions

The implementation evaluates **trigger-based conditions**:

```
PhaseTransition:
  from_phase: "scene_a"
  to_phase: "scene_b"
  trigger_conditions: ["escalation", "betrayal"]  # Must detect both

EndingCondition:
  trigger_conditions: ["total_breakdown"]          # Must detect this
```

**Evaluation**:
```python
all(trigger_id in detected_triggers for trigger_id in trigger_conditions)
```

### Deferred: State-Based Conditions

Future enhancements (W2.1+) may support:
- Numeric thresholds: `escalation_level >= 5`
- Character states: `veronique.emotional_state > 70`
- Relationship changes: `veronique_michel.tension_delta > 20`
- Scene duration: `turns_in_current_scene >= 3`

These require evaluating the canonical state, not just trigger detection.

---

## Canonical Rule: Condition Evaluation

**The new rule for condition-aware derivation**:

> A transition or ending fires if and only if:
> 1. It has no `trigger_conditions` (unconditional), OR
> 2. ALL conditions in `trigger_conditions` are in `detected_triggers`
>
> If conditions are defined but `detected_triggers` is None, the rule cannot fire (conservative).

This rule is:
- **Module-driven**: Reads conditions from content module
- **Deterministic**: All conditions must match (AND logic, not OR)
- **Trigger-based**: Evaluates against detected events in current turn
- **Generic**: Works with any module (God of Carnage, custom scenarios)

---

## Backward Compatibility

✅ **Fully backward compatible**:

```python
# Old usage: no detected_triggers parameter
result = derive_next_situation(session, module)
# Still works: unconditional cases fire normally

# New usage: with detected_triggers
result = derive_next_situation(session, module, detected_triggers=["escalation"])
# Now: conditional cases can fire
```

---

## Design Decisions

| Decision | Rationale | Consequence |
|----------|-----------|--------------|
| Optional `detected_triggers` parameter | Backward compatibility with existing code | Old callers unaffected; new callers can pass triggers |
| ALL conditions required (AND logic) | Narrative coherence: multiple preconditions all needed | Stricter but more predictable |
| Cannot fire if conditions exist but triggers not provided | Conservative: avoid silent failures | Explicit opt-in for condition evaluation |
| Trigger-based (not state-based) evaluation | W2.0.5 scope: simple, testable | State-based deferred to W2.1+ |

---

## Integration with W2.0 Phases

### W2.0.5 (completed)
- ✅ Unconditional derivation (foundation)
- ✅ Next-situation model and evaluation structure

### W2.0-R1 (completed)
- ✅ Failure path hardening

### W2.0-R2 (completed)
- ✅ Scene transition validation (graph-aware)

### W2.0-R3 (this phase)
- ✅ Condition-aware evaluation
- ✅ Trigger-based conditions
- ✅ Backward compatible

### W2.1 (next)
- ⏱️ Session coordinator (calls derive_next_situation with detected_triggers)
- ⏱️ State-based condition evaluation
- ⏱️ Multi-hop scene pathfinding

---

## Deferred to W2.1+

| Feature | Reason | Phase |
|---------|--------|-------|
| State-based conditions | Requires canonical state evaluation | W2.1+ |
| Numeric thresholds | Complex state inspection | W2.1+ |
| Character vulnerability checks | Part of escalation system | W2.2+ |
| Session manager integration | W2.1 coordinator layer | W2.1 |
| Condition history tracking | Audit trail enhancement | W2.2+ |

---

## Verification

```bash
PYTHONPATH=backend python -m pytest backend/tests/runtime/ -v
# Result: 139 PASSED
```

**Breakdown**:
- 135 existing tests (unchanged)
- 4 new condition-aware tests (all passing)

---

## Files Changed

| File | Change | Lines |
|------|--------|-------|
| `backend/app/runtime/next_situation.py` | Add condition evaluation to derive_next_situation and helpers | +30 (added logic), -8 (refactored), net +22 |
| `backend/tests/runtime/test_next_situation.py` | Add TestConditionAwareNextSituation class (4 tests) | +200 |

**Total**: 2 files modified, 200 new test lines, 22 code lines changed

---

## Acceptance Criteria Met

✅ Next-situation derivation supports real module conditions
✅ Trigger-based conditions fully implemented and tested
✅ Conditional transitions fire when conditions detected
✅ Conditional endings fire when conditions detected
✅ God of Carnage works with generic condition evaluation
✅ Backward compatibility maintained (optional parameter)
✅ All conditions must match (AND logic)
✅ No W2 scope jump occurred
✅ 139/139 tests passing

---

## Next Steps

W2.0-R3 completes condition-aware derivation. The next phases are:

- **W2.1**: Build session manager/coordinator
  - Calls `derive_next_situation(session, module, detected_triggers)`
  - Orchestrates turn execution and situation updates

- **W2.1+**: State-based condition evaluation
  - Extend condition model to support numeric thresholds
  - Evaluate against canonical_state values

- **W2.2+**: Advanced features
  - Multi-hop pathfinding for complex narratives
  - Condition history and reversal detection

---

**Commit**: `feat(w2): support condition-aware next situation derivation`
**Status**: ✅ COMPLETE

