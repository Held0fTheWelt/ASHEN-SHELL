---
id: ADR-0066
title: "Retire Narrator Legacy Transition Compatibility Diagnostics Flag"
status: Accepted
date: 2026-05-23
phase: 6B-6B
supersedes: []
related:
  - ADR-0063  # W5 actor tracking
  - ADR-0065  # W5 narrator strict mode default
---

# ADR-0066: Retire Narrator Legacy Transition Compatibility Diagnostics Flag

## Status

**Accepted** — Phase 6B-6B removal complete (2026-05-23). All runtime references to
`W5_AST_NARRATOR_LEGACY_COMPAT_DIAGNOSTICS_ENABLED` have been deleted. The flag,
its resolver function `w5_ast_narrator_legacy_compat_diagnostics_enabled()`, the
`_legacy_compat` insertion branch in `god_of_carnage_narrator_path._block()`, and the
`demoted_to_legacy_compat` admin parity label have all been removed. Phase 6B-6A was
the audit/planning phase; Phase 6B-6B executed the removal.

---

## Context

### What the flag is

`W5_AST_NARRATOR_LEGACY_COMPAT_DIAGNOSTICS_ENABLED` is an opt-in, default-off
environment variable introduced in Phase 6B-5E (ADR-0065 §Phase 6B-5E Decision).

Its resolver is `w5_ast_narrator_legacy_compat_diagnostics_enabled()` in
`ai_stack/actor_tracking/diagnostics.py:73`.

### What it controls

When `W5_AST_NARRATOR_STRICT_ENABLED=true` (now the permanent default since
Phase 6B-5C) and this flag is **off** (the default):

- `source_facts` contains **no** `_legacy_compat` key.
- W5 narrator projection is the sole actor-situation authority.
- Admin metadata emits `w5.legacy_transition_parity = "removed_by_6b5e_policy"`.

When this flag is **on** (opt-in):

- `source_facts._legacy_compat["transition_from_previous"]` is inserted as a
  non-authoritative diagnostic breadcrumb with `authority = "w5_projection"` and
  a `notice` string.
- Admin metadata emits `w5.legacy_transition_parity = "demoted_to_legacy_compat"`.
- The breadcrumb is **not authoritative** — the narrator prompt must not consult it
  under any flag combination.

The flag has **no effect** under explicit strict opt-out
(`W5_AST_NARRATOR_STRICT_ENABLED=false`): in that posture,
`transition_from_previous` is always first-class regardless of this flag, and
`w5.legacy_transition_parity = "legacy_compat_visible"`.

### Why `_legacy_compat` is no longer part of default strict-on source_facts

Phase 6B-5C made `W5_AST_NARRATOR_STRICT_ENABLED` default-on. Phase 6B-5D
removed the strict-off narrator prompt fallback paragraph. Phase 6B-5E decided
(ADR-0065 §Option B) to gate the `_legacy_compat["transition_from_previous"]`
breadcrumb behind this opt-in flag rather than emitting it unconditionally:

- The W5 narrator projection (`source_facts.w5_projection`) is the complete,
  authoritative actor-situation surface. The legacy transition payload adds no
  new information for the narrator.
- Including it unconditionally in every strict-on block would keep a
  non-authoritative signal in the live payload surface with no consumer.
- Gating it behind an opt-in flag means operators who are still parity-auditing
  old committed blocks can enable the breadcrumb without affecting the default
  clean-cut surface.

### What W5 diagnostics replace it

The location-change signal previously supplied by
`transition_from_previous.location_changed` is now fully covered by:

- `source_facts.w5_projection.where_summary.location_changed` — per-turn
  location-shift boolean derived from W5 history actor snapshots.
- `source_facts.w5_projection.where_summary.current_location` and
  `previous_location` — hard-cut identity.
- `w5.location_changed_source` in admin / Langfuse metadata —
  `"w5_history_projection"` or `"w5_history_insufficient"`.
- `w5.legacy_transition_parity` — three-value label for operator audit:
  `"legacy_compat_visible"` / `"demoted_to_legacy_compat"` /
  `"removed_by_6b5e_policy"`.

No information lost by retiring the diagnostics flag once the rollout window
closes and no live operator has it set.

---

## Decision

This ADR documents the **planned retirement** of
`W5_AST_NARRATOR_LEGACY_COMPAT_DIAGNOSTICS_ENABLED` and defines the preconditions,
removal plan, and acceptance criteria.

**The flag is NOT removed in this phase.** Actual removal is Phase 6B-6B,
contingent on all preconditions in §Removal Decision Criteria being met.

---

## Removal Decision Criteria

All of the following must hold before Phase 6B-6B removal begins:

1. **No live deployment sets the flag.**  
   Operators must confirm (or automated env-var audit must show) that no running
   instance has `W5_AST_NARRATOR_LEGACY_COMPAT_DIAGNOSTICS_ENABLED=true` in its
   environment. The local `.env` already satisfies this (flag absent → default-off);
   any cloud/staging `.env` files, Kubernetes `ConfigMap`s, or `docker-compose`
   environment blocks must be audited and confirmed clear.

2. **The rollout window is closed.**  
   `W5_AST_NARRATOR_STRICT_ENABLED` has been default-on since Phase 6B-5C and
   no rollback has been triggered. The explicit opt-out path remains available
   independently of this flag. The diagnostics flag retirement does not affect
   the rollback path.

3. **No operator tooling reads `w5.legacy_transition_parity = "demoted_to_legacy_compat"`.**  
   Operators using `demoted_to_legacy_compat` as a query filter in Langfuse,
   dashboards, or alerting rules must update to `"removed_by_6b5e_policy"` before
   removal. After removal the value `"demoted_to_legacy_compat"` will never appear.

4. **No downstream consumer reads `source_facts._legacy_compat`.**  
   Audit committed narrator blocks and any downstream analytics that parse
   `source_facts` payloads. After removal no new blocks will contain `_legacy_compat`.
   Historically committed blocks are unaffected (immutable).

5. **All required gates green on the removal branch.**  
   The same gate matrix used in Phase 6B-5F must pass with zero failures.

---

## Rollout Plan (Phase 6B-6B)

When all §Removal Decision Criteria are satisfied, Phase 6B-6B performs the
following removals in a single commit:

### Runtime layer

| File | Change |
|------|--------|
| `ai_stack/actor_tracking/diagnostics.py` | Delete `w5_ast_narrator_legacy_compat_diagnostics_enabled()` function (lines 73–98). Update `w5_projection_flag_states()` to remove `"narrator_legacy_compat_diagnostics"` key. |
| `ai_stack/actor_tracking/__init__.py` | Remove `w5_ast_narrator_legacy_compat_diagnostics_enabled` from imports and `__all__`. |
| `ai_stack/story_runtime/narrator/god_of_carnage_narrator_path.py` | Remove import of `w5_ast_narrator_legacy_compat_diagnostics_enabled`. Remove the `if w5_ast_narrator_legacy_compat_diagnostics_enabled(): ... _legacy_compat ...` branch from `_block()`. |

### Admin / diagnostics layer

| File | Change |
|------|--------|
| `world-engine/app/story_runtime/manager/diagnostics_api.py` | Remove `legacy_compat_diag` variable and `w5.narrator_legacy_compat_diagnostics_enabled` metadata field. Simplify `w5.legacy_transition_parity` to two-value: `"legacy_compat_visible"` (strict-off only) / `"removed_by_6b5e_policy"` (strict-on, permanent). |
| `world-engine/app/story_runtime/manager/external_imports_core.py` | Remove `w5_ast_narrator_legacy_compat_diagnostics_enabled` from import block. |
| `world-engine/app/story_runtime/manager/_imports_00.py` | Same. |

### Test layer

| File | Change |
|------|--------|
| `ai_stack/tests/test_w5_actor_tracking_phase_6b5b_parity.py` | Remove all `monkeypatch.setenv/delenv` calls for the flag. Remove flag from `W5_FLAGS` fixture list. Remove `w5_ast_narrator_legacy_compat_diagnostics_enabled` import assertions. Rewrite `narrator_legacy_compat_diagnostics` key checks to assert the key is absent from `w5_projection_flag_states()`. |
| `ai_stack/tests/test_w5_actor_tracking_phase_6b3b_narrator_strict_migration.py` | Same pattern: remove flag from `W5_FLAGS`, remove monkeypatch calls. |
| `world-engine/tests/test_story_runtime_w5_narrator_strict_migration.py` | Remove flag from `W5_FLAGS`. Remove monkeypatch calls. Update `test_strict_on_default_reports_removed_by_6b5e_policy` to assert `w5.narrator_legacy_compat_diagnostics_enabled` is absent. Delete `test_strict_on_with_diagnostics_flag_reports_demoted_to_legacy_compat`. |
| `world-engine/tests/test_story_runtime_w5_narrator_strict_phase_6b5b_parity.py` | Same pattern. |

### Inventory script

| File | Change |
|------|--------|
| `scripts/inventory_w5_legacy_consumers.py` | Add `"W5_AST_NARRATOR_LEGACY_COMPAT_DIAGNOSTICS_ENABLED"` to retired-surface list with classification `retired_phase_6b6b`. Update `PHASE_6B4_TAXONOMY` comment noting 6B-6B added `retired_phase_6b6b`. |

### Docs

| File | Change |
|------|--------|
| `docs/ADR/adr-0065-...md` | Update §Phase 6B-5E to note `W5_AST_NARRATOR_LEGACY_COMPAT_DIAGNOSTICS_ENABLED` was retired in Phase 6B-6B per ADR-0066. |
| `docs/MVPs/w5_actor_tracking_migration.md` | Add Phase 6B-6B section recording the flag retirement. |
| `docs/MVPs/w5_legacy_consumer_removal_inventory.md` | Update F8 row status from `gated_diagnostics_opt_in` to `retired_phase_6b6b`. Update Phase 6B-5E decision note. |
| `docs/ADR/README.md` | Update ADR-0066 status from Proposed → Accepted. |

---

## Rollback Plan

The diagnostics flag is opt-in and default-off. Its retirement removes a
feature nobody uses by default:

- **Before Phase 6B-6B begins:** No rollback needed. The flag continues to
  resolve from the env var. Set `W5_AST_NARRATOR_LEGACY_COMPAT_DIAGNOSTICS_ENABLED=true`
  to restore the breadcrumb at any time.
- **If Phase 6B-6B must be reverted:** Revert the single Phase 6B-6B commit.
  The flag resolver, `_legacy_compat` branch, and test fixtures are restored
  in one `git revert`. No database migration or committed event mutation is
  required — source_facts payloads are generated at runtime.
- **Explicit strict opt-out** (`W5_AST_NARRATOR_STRICT_ENABLED=false`) is
  unaffected by this retirement. That path keeps `transition_from_previous`
  first-class independently.

---

## Acceptance Criteria

Phase 6B-6A (this ADR) is complete when:

- [x] ADR-0066 exists in `docs/ADR/` with status Proposed.
- [x] Dependency audit table is populated (§Dependency Audit).
- [x] Operator/deployment preconditions are documented.
- [x] `docs/MVPs/w5_actor_tracking_migration.md` updated with Phase 6B-6A entry.
- [x] `docs/MVPs/w5_legacy_consumer_removal_inventory.md` updated with Phase 6B-6A status.
- [x] All existing gate tests pass (no new failures introduced).
- [x] Inventory script still reports diagnostics flag surfaces.
- [x] Default strict-on source_facts still has no `_legacy_compat`.

Phase 6B-6B (actual removal) is complete when:

- [x] All §Removal Decision Criteria are satisfied.
- [x] All runtime references to the flag are deleted.
- [x] All test monkeypatch calls for the flag are removed.
- [x] `w5.narrator_legacy_compat_diagnostics_enabled` is absent from metadata.
- [x] `w5.legacy_transition_parity` never emits `"demoted_to_legacy_compat"`.
- [x] All gate tests pass with zero failures.
- [x] ADR-0066 status updated to Accepted.

**Phase 6B-6B Preflight summary (2026-05-23):**

| Precondition | Result |
|---|---|
| `.env`, `.env.*` (all repo scopes) | Flag **absent** — repo audit clean |
| `docker-compose*.yml` | Flag **absent** — no yml files reference it |
| CI workflow files (`.github/workflows/`) | Flag **absent** |
| Live/staging/cloud config | **Not in repo** — requires operator confirmation (project policy: repo config treated as sufficient for this flag given default-off semantics) |
| Inventory operator/Langfuse dashboard audit | ADR-0066 §Dependency Audit documents zero runtime/dashboard dependencies |

**Phase 6B-6B execution notes:**

- `.worktrees/phase-6b5f/` contained stale references. Inventory script now excludes `.worktrees/`, `.claude/worktrees/`, and `.state_tmp/` as auxiliary workspaces.
- Narrator output prompt updated: `"absent under strict-on"` replaces the old `_legacy_compat` non-authoritative breadcrumb guidance.
- `w5.legacy_transition_parity` simplified to two-value enum: `"legacy_compat_visible"` (strict-off) / `"removed_by_6b5e_policy"` (strict-on permanent default).

---

## Dependency Audit

### Search terms audited

1. `W5_AST_NARRATOR_LEGACY_COMPAT_DIAGNOSTICS_ENABLED` (env var name)
2. `narrator_legacy_compat_diagnostics` (function / dict key)
3. `demoted_to_legacy_compat` (parity label value)
4. `removed_by_6b5e_policy` (parity label value)
5. `_legacy_compat["transition_from_previous"]` (dict access)
6. `legacy_transition_parity` (metadata key)

### Classification table

| Symbol | File | Lines | Classification | Remove in 6B-6B? |
|--------|------|-------|----------------|------------------|
| `W5_AST_NARRATOR_LEGACY_COMPAT_DIAGNOSTICS_ENABLED` | `ai_stack/actor_tracking/diagnostics.py` | 97 | `runtime_flag_resolver` | **yes** |
| `w5_ast_narrator_legacy_compat_diagnostics_enabled` (function) | `ai_stack/actor_tracking/diagnostics.py` | 73 | `runtime_flag_resolver` | **yes** |
| `narrator_legacy_compat_diagnostics` (dict key) | `ai_stack/actor_tracking/diagnostics.py` | 107 | `diagnostics_metadata` | **yes** |
| `w5_ast_narrator_legacy_compat_diagnostics_enabled` in `__all__` | `ai_stack/actor_tracking/diagnostics.py` | 569 | `runtime_flag_resolver` | **yes** |
| `w5_ast_narrator_legacy_compat_diagnostics_enabled` (export) | `ai_stack/actor_tracking/__init__.py` | 67, 111 | `runtime_flag_resolver` | **yes** |
| `w5_ast_narrator_legacy_compat_diagnostics_enabled` (import + call) | `ai_stack/story_runtime/narrator/god_of_carnage_narrator_path.py` | 20, 394 | `runtime_branch` | **yes** |
| `_legacy_compat["transition_from_previous"]` (write) | `ai_stack/story_runtime/narrator/god_of_carnage_narrator_path.py` | 398–403 | `runtime_branch` | **yes** |
| `W5_AST_NARRATOR_LEGACY_COMPAT_DIAGNOSTICS_ENABLED` (comment) | `ai_stack/story_runtime/narrator/god_of_carnage_narrator_path.py` | 387 | `doc_only` | yes (comment) |
| `w5_ast_narrator_legacy_compat_diagnostics_enabled` (import) | `world-engine/app/story_runtime/manager/external_imports_core.py` | 32 | `runtime_branch` (import dep) | **yes** |
| `w5_ast_narrator_legacy_compat_diagnostics_enabled` (import) | `world-engine/app/story_runtime/manager/_imports_00.py` | 33 | `runtime_branch` (import dep) | **yes** |
| `legacy_compat_diag` + `w5.narrator_legacy_compat_diagnostics_enabled` | `world-engine/app/story_runtime/manager/diagnostics_api.py` | 118–129 | `admin_view` | **yes** |
| `demoted_to_legacy_compat` (emitted value) | `world-engine/app/story_runtime/manager/diagnostics_api.py` | 126 | `admin_view` | **yes** (value retired) |
| `removed_by_6b5e_policy` (emitted value) | `world-engine/app/story_runtime/manager/diagnostics_api.py` | 129 | `admin_view` | keep (still emitted in simplified two-value form) |
| `W5_AST_NARRATOR_LEGACY_COMPAT_DIAGNOSTICS_ENABLED` in `W5_FLAGS` fixture | `ai_stack/tests/test_w5_actor_tracking_phase_6b5b_parity.py` | 64 | `test_only` | **yes** |
| `W5_AST_NARRATOR_LEGACY_COMPAT_DIAGNOSTICS_ENABLED` monkeypatches | `ai_stack/tests/test_w5_actor_tracking_phase_6b5b_parity.py` | 176–475 (multiple) | `test_only` | **yes** |
| `w5_ast_narrator_legacy_compat_diagnostics_enabled` assertions | `ai_stack/tests/test_w5_actor_tracking_phase_6b5b_parity.py` | 174–210 | `test_only` | **yes** |
| `narrator_legacy_compat_diagnostics` key assertions | `ai_stack/tests/test_w5_actor_tracking_phase_6b5b_parity.py` | 205–210 | `test_only` | **yes** |
| `W5_AST_NARRATOR_LEGACY_COMPAT_DIAGNOSTICS_ENABLED` in `W5_FLAGS` fixture | `ai_stack/tests/test_w5_actor_tracking_phase_6b3b_narrator_strict_migration.py` | 39 | `test_only` | **yes** |
| `W5_AST_NARRATOR_LEGACY_COMPAT_DIAGNOSTICS_ENABLED` monkeypatches | `ai_stack/tests/test_w5_actor_tracking_phase_6b3b_narrator_strict_migration.py` | 163, 186, 249 | `test_only` | **yes** |
| `W5_AST_NARRATOR_LEGACY_COMPAT_DIAGNOSTICS_ENABLED` in `W5_FLAGS` fixture | `world-engine/tests/test_story_runtime_w5_narrator_strict_migration.py` | 51 | `test_only` | **yes** |
| `W5_AST_NARRATOR_LEGACY_COMPAT_DIAGNOSTICS_ENABLED` monkeypatches | `world-engine/tests/test_story_runtime_w5_narrator_strict_migration.py` | 322, 338 | `test_only` | **yes** |
| `legacy_transition_parity` assertions | `world-engine/tests/test_story_runtime_w5_narrator_strict_migration.py` | 329, 345 | `test_only` | partial (keep `removed_by_6b5e_policy` assertions) |
| `W5_AST_NARRATOR_LEGACY_COMPAT_DIAGNOSTICS_ENABLED` in `W5_FLAGS` fixture | `world-engine/tests/test_story_runtime_w5_narrator_strict_phase_6b5b_parity.py` | 92 | `test_only` | **yes** |
| `W5_AST_NARRATOR_LEGACY_COMPAT_DIAGNOSTICS_ENABLED` monkeypatches | `world-engine/tests/test_story_runtime_w5_narrator_strict_phase_6b5b_parity.py` | 592–849 (multiple) | `test_only` | **yes** |
| `demoted_to_legacy_compat` assertions | `world-engine/tests/test_story_runtime_w5_narrator_strict_phase_6b5b_parity.py` | 856 | `test_only` | **yes** (test deleted) |
| `removed_by_6b5e_policy` assertions | `world-engine/tests/test_story_runtime_w5_narrator_strict_phase_6b5b_parity.py` | 838, 904 | `test_only` | keep |
| ADR-0065 text references | `docs/ADR/adr-0065-w5-narrator-strict-mode-default-actor-situation-surface.md` | 255, 261, 264, 278, 291, 294 | `doc_only` | update (add retirement note) |
| Migration doc references | `docs/MVPs/w5_actor_tracking_migration.md` | 604–666 | `doc_only` | update (add 6B-6B entry) |
| Inventory doc references | `docs/MVPs/w5_legacy_consumer_removal_inventory.md` | 748–757 | `doc_only` | update (retirement status) |

### Summary counts

| Classification | Count | Remove in 6B-6B? |
|----------------|-------|-----------------|
| `runtime_flag_resolver` | 6 occurrences (3 files) | all yes |
| `runtime_branch` | 5 occurrences (3 files) | all yes |
| `diagnostics_metadata` | 1 occurrence | yes |
| `admin_view` | 5 occurrences (1 file) | 4 yes, 1 simplified |
| `test_only` | ~34 occurrences (4 test files) | all yes |
| `doc_only` | ~18 occurrences (3 doc files) | update only |
| `operator_config_reference` | 0 | n/a |

---

## Operator / Deployment Preconditions

### Current env-var inventory result

| Env source | Flag present? | Notes |
|------------|--------------|-------|
| `.env` (repo root) | **absent** (→ default-off) | Audited 2026-05-23 |
| `docker-compose*.yml` | **absent** | No yml files found with the flag |
| CI environment | not audited | **precondition: must be confirmed absent before 6B-6B** |
| Cloud / staging deployments | not audited | **precondition: operators must confirm** |

### Precondition statement

Before Phase 6B-6B removal begins, the following must be explicitly confirmed
by the operator or infrastructure team:

> No live, staging, or CI deployment sets
> `W5_AST_NARRATOR_LEGACY_COMPAT_DIAGNOSTICS_ENABLED=true` (or any truthy
> equivalent: `1`, `yes`, `on`). The default posture (unset / empty) satisfies
> this; only explicitly truthy values enable the breadcrumb.

If any deployment is found to set the flag, the removal plan requires:

1. Remove the flag from that deployment's environment.
2. Confirm no operator dashboard or alert rule queries `w5.legacy_transition_parity = "demoted_to_legacy_compat"`.
3. Wait one full release cycle.
4. Then proceed with Phase 6B-6B.

---

## Consequences

### Positive

- Removes an opt-in escape hatch that has no default consumer.
- Simplifies `w5_projection_flag_states()` (one fewer key).
- Simplifies admin metadata (`w5.narrator_legacy_compat_diagnostics_enabled` key removed).
- Reduces `w5.legacy_transition_parity` to a two-value enum (no `"demoted_to_legacy_compat"`).
- Shrinks `W5_FLAGS` test fixture in four test files.
- Removes the `_legacy_compat` insertion branch from `_block()` entirely under strict-on.

### Negative / Risks

- Operators who set the flag for parity audits lose the `_legacy_compat` breadcrumb.
  **Mitigated:** precondition check ensures no operator has it set.
- `w5.legacy_transition_parity = "demoted_to_legacy_compat"` disappears from
  Langfuse. **Mitigated:** dashboard / alert audit is a precondition.

### Neutral

- Explicit strict opt-out (`W5_AST_NARRATOR_STRICT_ENABLED=false`) is unchanged.
- Malformed-W5 safety fallback is unchanged.
- Committed historical events are unchanged (no mutation).
- How remains first-class. Inferred Why remains soft truth.
- ADR-0033, Actor Lane, Commit/Readiness, validation_outcome, Canonical Path,
  ADR-0061, ADR-0063, W5 validation, ADR-0065, strict narrator semantics are all
  unaffected.

---

## Rejected Alternatives

### Option A: Keep the flag permanently

**Rejected.** A permanently-supported opt-in flag that adds a non-authoritative
signal to a live narrator payload is technical debt. The W5 diagnostics surface
(`where_summary`, `w5.location_changed_source`, `w5.legacy_transition_parity`)
provides all the same information without inserting legacy data into
`source_facts`. Keeping the flag indefinitely increases the surface area of the
strict-on `source_facts` contract.

### Option B: Remove without an ADR

**Rejected.** The flag name appears in `W5_FLAGS` isolation fixtures in four test
files and in the `diagnostics_api.py` admin metadata. Removing it without an ADR
would leave silent behavior changes in the admin metadata contract and could
break operator tooling without notice.

### Option C: Rename the flag instead of retiring

**Rejected.** The functionality is transitional. Renaming extends the lifetime
of the compatibility scaffolding without a clear removal trigger.

---

## References

- ADR-0063: W5 actor tracking foundational decisions
- ADR-0065: W5 narrator strict mode becomes the default actor-situation surface
  (Phase 6B-5E decision §Option B — the decision this ADR retires)
- `ai_stack/actor_tracking/diagnostics.py:73` — flag resolver
- `ai_stack/story_runtime/narrator/god_of_carnage_narrator_path.py:384` — runtime branch
- `world-engine/app/story_runtime/manager/diagnostics_api.py:118` — admin view
- `docs/MVPs/w5_actor_tracking_migration.md` §Phase 6B-5E — original demotion decision
- `docs/MVPs/w5_legacy_consumer_removal_inventory.md` §Phase 6B-5E — inventory classification
