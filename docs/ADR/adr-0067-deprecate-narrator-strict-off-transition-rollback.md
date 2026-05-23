---
id: ADR-0067
title: "Deprecate Narrator Strict-Off Transition Rollback Surface"
status: Accepted
date: 2026-05-23
phase: 6B-7
supersedes: []
related:
  - ADR-0063  # W5 actor tracking
  - ADR-0065  # W5 narrator strict mode default
  - ADR-0066  # Retire narrator legacy-compat diagnostics flag
---

# ADR-0067: Deprecate Narrator Strict-Off Transition Rollback Surface

## Status

**Accepted** — Phase 6B-7 deprecation implemented (2026-05-23). The strict-off
rollback path (`W5_AST_NARRATOR_STRICT_ENABLED=false`) is **not yet removed** —
it is declared deprecated. A `NarratorStrictOffDeprecationWarning` is emitted once
per process when the flag is explicitly set to a false value. The warning identifies
the flag, states that strict-off behavior is deprecated, and points here. No behavior
has been removed. Removal requires a dedicated future phase and the acceptance criteria
in §"Future Removal Criteria" below.

---

## Context

### State after ADR-0066

Phase 6B-6B (ADR-0066) completed the following:

- Removed `W5_AST_NARRATOR_LEGACY_COMPAT_DIAGNOSTICS_ENABLED` and its resolver
  `w5_ast_narrator_legacy_compat_diagnostics_enabled()`.
- Removed the `_legacy_compat["transition_from_previous"]` insertion branch from
  `god_of_carnage_narrator_path._block()` under strict-on.
- Removed the `demoted_to_legacy_compat` admin parity label.
- Simplified `w5.legacy_transition_parity` to a two-value enum:
  `removed_by_6b5e_policy` (strict-on) / `legacy_compat_visible` (strict-off).
- Confirmed `w5_projection` as the sole actor-situation authority under strict-on.
- All 269 tests passed, 0 failed.

After ADR-0066 there remain two distinct runtime postures:

| Posture | Trigger | `source_facts["transition_from_previous"]` | Authority |
|---|---|---|---|
| **Strict-on** (default) | unset / empty / `1/true/yes/on` | **absent** | `w5_projection` |
| **Strict-off** (rollback) | explicit `0/false/no/off` | **present, first-class** | legacy block |

The strict-off posture is the sole remaining surface where `transition_from_previous`
appears as a first-class narrator situation input. This ADR deprecates that posture.

### Why strict-off exists

`W5_AST_NARRATOR_STRICT_ENABLED` was introduced in Phase 6B-3B as an opt-in gate
(default-off), allowing operators to progressively migrate narrator consumers to the W5
projection surface. Phase 6B-5C made strict-on the default. Phase 6B-5D removed the
strict-off narrator prompt fallback paragraph. Phase 6B-6B removed the `_legacy_compat`
diagnostic breadcrumb branch.

The strict-off posture now has a single purpose: **emergency rollback**. If W5 projection
data is absent, malformed, or producing incorrect actor-situation signals in production,
an operator can set `W5_AST_NARRATOR_STRICT_ENABLED=false` to revert narrator context
assembly to the Phase 6B-3A posture where `transition_from_previous` remains first-class.

This rollback path was designed for the migration period. That period is over. Strict-on
has been the default for multiple phases. No operator rollback has been triggered. The
rollback surface is now legacy baggage, not a required escape hatch.

### Why `transition_from_previous` is no longer authoritative

`transition_from_previous` is a substrate-derived diff payload synthesized in
`god_of_carnage_narrator_path._transition_facts()`. It captures location, scene,
and prop changes between consecutive step snapshots.

Under W5 actor tracking (ADR-0063, Phase 6B-1+), these signals are derived from the
W5 ledger and expressed as typed `W5Fact` entries in the W5 snapshot, then projected
into `source_facts.w5_projection` via `build_w5_projection_for_narrator()`. Specifically:

- **location changes** → `w5_projection.where_summary.location_changed`
- **scene state** → `w5_projection.where_summary.scene_label` / `scene_id`
- **actor presence** → `w5_projection.actors[actor_id].where`

The W5 projection is:
- validated by `validate_w5_actor_tracking()` before being committed to source_facts,
- sourced from a typed ledger with fact-level truth levels and conflict resolution, and
- the surface that narrator tests, parity suites, and admin diagnostics are pinned against.

`transition_from_previous` was never validated at the W5 level. It is a raw diff payload
with no truth-level tracking, no conflict detection, and no actor-lane governance.
Keeping it as a first-class narrator input under strict-off creates a dual-authority
surface that is harder to reason about and maintain.

### What the deprecation warning does

When `W5_AST_NARRATOR_STRICT_ENABLED` is explicitly set to `0`, `false`, `no`, or `off`
(case-insensitive), the first call to `w5_ast_narrator_strict_enabled()` during the
process lifetime emits a `NarratorStrictOffDeprecationWarning` (a subclass of
`DeprecationWarning`) via Python's `warnings.warn()`. Subsequent calls are silent
(module-level sentinel `_strict_off_deprecation_warned`).

The warning is **not** emitted when the variable is unset or empty — those values
select the strict-on default, which is the correct and non-deprecated posture.

The warning text identifies the flag name, labels the behavior deprecated, names
this ADR, and states that the strict-off branch will be removed in a future phase.

### Operator impact

Operators who do not set `W5_AST_NARRATOR_STRICT_ENABLED=false` are unaffected.
No behavior changes for the default posture.

Operators who set `W5_AST_NARRATOR_STRICT_ENABLED=false` will see a Python
`DeprecationWarning` in their logs at process startup. The rollback behavior
(`transition_from_previous` first-class) remains fully functional. No narrator
output changes in the strict-off posture.

Recommended migration path:
1. Remove `W5_AST_NARRATOR_STRICT_ENABLED=false` from all deployment configs.
2. Verify narrator output under strict-on (the default).
3. If issues are found, open a targeted ADR — do **not** reinstate the strict-off override.

---

## Decision

Phase 6B-7 takes the following actions:

1. **Add `NarratorStrictOffDeprecationWarning`** to `ai_stack/actor_tracking/diagnostics.py`
   as a named `DeprecationWarning` subclass, exported from the package.

2. **Emit the warning once per process** inside `w5_ast_narrator_strict_enabled()` when
   strict-off is detected. The once-per-process sentinel (`_strict_off_deprecation_warned`)
   is a module-level bool that tests reset via `monkeypatch.setattr`.

3. **Do not remove** any of the following:
   - `W5_AST_NARRATOR_STRICT_ENABLED` env-var gate.
   - `w5_ast_narrator_strict_enabled()` function.
   - The strict-off branch in `god_of_carnage_narrator_path._narrator_block()`.
   - `source_facts["transition_from_previous"]` under explicit strict-off.
   - The malformed-W5 safety fallback.
   - Public compatibility aliases (`NarratorStrictOffDeprecationWarning`, etc.).
   - Substrate writers / readers.

4. **Update inventory classifications** in `scripts/inventory_w5_legacy_consumers.py`
   to reflect that `transition_from_previous` is now `strict_off_rollback_deprecated`
   and that a dedicated ADR (this one) covers the removal path.

5. **Update docs** in `docs/MVPs/w5_actor_tracking_migration.md` and
   `docs/MVPs/w5_legacy_consumer_removal_inventory.md` to record the deprecated state.

6. **Add semantic tests** (`ai_stack/tests/test_w5_actor_tracking_phase_6b7_strict_off_deprecation.py`)
   proving all warning and behavioral contracts.

---

## Future Removal Criteria

The strict-off branch (`W5_AST_NARRATOR_STRICT_ENABLED=false`) and its
`transition_from_previous` first-class narrator source_facts entry may be
permanently removed only when ALL of the following acceptance criteria are met:

1. **No active operator usage**: Monitoring confirms `W5_AST_NARRATOR_STRICT_ENABLED=false`
   is not set in any production, staging, or preview deployment.

2. **Warning observable in logs**: The `NarratorStrictOffDeprecationWarning` has been
   in place for at least one release cycle without operator escalation.

3. **Parity test suite updated**: All tests that exercise the strict-off rollback path
   (parametrized `false` cases in `test_w5_actor_tracking_phase_6b3b_narrator_strict_migration.py`,
   `test_w5_actor_tracking_phase_6b5b_parity.py`, and world-engine equivalents) are either
   removed or converted to strict-on-only tests, with full rationale in the removal ADR.

4. **Inventory updated**: `transition_from_previous` and `location_changed` are removed
   from `LEGACY_SURFACES` in the inventory script (or reclassified as doc-only), and the
   `strict_off_rollback_deprecated` classification is replaced with `removed`.

5. **A dedicated removal ADR** (tentatively ADR-0068 or successor) is written, reviewed,
   and Accepted before any code is deleted. The removal ADR must:
   - Reference this ADR and confirm the acceptance criteria above are met.
   - Specify the removal diff at the function and branch level.
   - Include a rollback plan (revert commit or feature flag) for the release window.
   - Confirm that no narrator prompt, parity test, or admin diagnostic reads
     `transition_from_previous` outside a strict-off gate after the removal.

---

## Tests Required Before Final Removal

Before the strict-off branch is removed, the following test changes are required:

- Remove or convert all `monkeypatch.setenv("W5_AST_NARRATOR_STRICT_ENABLED", "false")`
  parametrize cases in the parity suites to strict-on-only.
- Confirm `test_god_of_carnage_narrator_path.py::test_narrator_path_strict_off_*` tests
  are deleted and replaced with strict-on equivalents.
- Confirm `test_goc_narrator_path_opening.py::test_strict_off_*` tests are deleted.
- Confirm `test_w5_actor_tracking_projection.py` line 790 strict-off case is removed.
- Confirm the Phase 6B-7 test file (`test_w5_actor_tracking_phase_6b7_strict_off_deprecation.py`)
  is updated to test the *removed* state (strict-off raises, or env-var is silently ignored).

---

## Rollback Plan

If the deprecation warning causes unexpected operator impact before removal:

1. Set `W5_AST_NARRATOR_STRICT_ENABLED` to `true` (no-op, already the default) to silence
   the warning without reverting the code.
2. If the warning itself needs to be suppressed in test pipelines, use Python's
   `warnings.filterwarnings("ignore", category=NarratorStrictOffDeprecationWarning)`.
3. If the sentinel or warning mechanism is found to cause test isolation issues,
   revert the `_emit_strict_off_deprecation_warning()` function body and re-open
   this ADR as Proposed.

The strict-off behavior itself (transition_from_previous first-class) is untouched
and always available by setting the env var to `false`.

---

## Rejected Alternatives

### A: Remove strict-off immediately in Phase 6B-7

**Rejected.** Phase 6B-7 follows a deprecate-then-remove pattern. Removing without
deprecation warning gives operators no runway. The parity test suite still parametrizes
over `false` values — those tests would need simultaneous removal, increasing the
blast radius. A dedicated removal ADR provides a cleaner audit trail.

### B: Add a log message instead of a Python warning

**Rejected.** Python's `warnings` module is the canonical mechanism for deprecation
signals in library code. It integrates with pytest (`pytest.warns`), logging filters,
and CI warning-as-error configurations. A structured log entry would be invisible to
operators who do not instrument their log aggregation for this specific message.

### C: Update ADR-0065 or ADR-0066 with a Phase 6B-7 section instead of a new ADR

**Rejected.** ADR-0065 covers the default-on flip decision. ADR-0066 covers the
legacy-compat diagnostics flag retirement. This ADR covers a conceptually distinct
decision: deprecating the rollback surface itself. A separate ADR gives future
engineers a clearer audit trail for each decision boundary. Cross-references are
maintained via the `related:` frontmatter.

### D: Keep strict-off indefinitely as a "supported opt-out"

**Rejected.** The migration period is over. Strict-on has been the default for multiple
phases. Keeping a permanently-supported dual-authority surface means indefinitely
maintaining `transition_from_previous` as a narrator input alongside W5 projection,
which contradicts ADR-0063's goal of a single typed actor-situation authority.

---

## Consequences

**Positive:**
- Operators who have left `W5_AST_NARRATOR_STRICT_ENABLED=false` in config receive
  a clear, actionable warning.
- The removal path is codified with explicit acceptance criteria.
- Test suites gain isolation semantics for the deprecation sentinel.
- The `NarratorStrictOffDeprecationWarning` class is importable for use in
  `warnings.filterwarnings` guards.

**Neutral:**
- No narrator output changes for any deployment (warning is not in narrator output).
- No change to committed event structure.
- No change to admin diagnostics format.

**Negative (mitigated):**
- Test files that parametrize `W5_AST_NARRATOR_STRICT_ENABLED=false` will emit
  `DeprecationWarning` unless they use `pytest.warns` or `warnings.catch_warnings`.
  The autouse fixture in the new test file shows the reset pattern.
  Mitigation: existing tests use `monkeypatch` which isolates env; the sentinel
  reset pattern is documented and demonstrated in the Phase 6B-7 test file.
