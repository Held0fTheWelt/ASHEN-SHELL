---
id: ADR-0068
title: "Remove Narrator Strict-Off Transition Rollback Surface"
status: Accepted
date: 2026-05-23
phase: 6B-8
supersedes: []
related:
  - ADR-0063  # W5 actor tracking
  - ADR-0065  # W5 narrator strict mode default
  - ADR-0066  # Retire narrator legacy-compat diagnostics flag
  - ADR-0067  # Deprecate narrator strict-off transition rollback surface
---

# ADR-0068: Remove Narrator Strict-Off Transition Rollback Surface

## Status

**Accepted** — Phase 6B-8 (2026-05-23).

---

## Operator Waiver

**Waiver granted by authorized operator decision (2026-05-23).**

ADR-0067 Criteria 1 and 2 were not fully satisfied from repository evidence alone:

| Criterion | Status | Waiver Rationale |
|---|---|---|
| 1. No active operator usage in prod/staging/cloud | **Partially met** — repo-local config is clean; live/cloud config is not verifiable from the repository | Operator waives the live-config audit requirement. Repo-local audit (no `.env`, `docker-compose`, GitHub workflows, `settings*.py` sets `W5_AST_NARRATOR_STRICT_ENABLED=false`) is accepted as sufficient evidence. |
| 2. NarratorStrictOffDeprecationWarning observed for one full release cycle | **Not met** — the warning was introduced the same day as ADR-0067 (2026-05-23) | Operator waives the release-cycle observation period. The rollback window has effectively closed: strict-on has been the permanent default since Phase 6B-5C; no production rollback has been triggered; the payload produced under strict-off (`source_facts["transition_from_previous"]`) has not been narrator-authoritative since ADR-0065/ADR-0066. |
| 3. Parity test suite updated | **Met by this phase (6B-8)** | — |
| 4. Inventory updated | **Met by this phase (6B-8)** | — |
| 5. This ADR written and Accepted | **Met by this document** | — |

**Waiver scope:** This waiver covers the removal of the strict-off rollback path in `ai_stack/actor_tracking/diagnostics.py` and `ai_stack/story_runtime/narrator/god_of_carnage_narrator_path.py` as specified in this ADR. It does not waive any other ADR criterion or constraint.

**Repo-local config evidence (Phase 6B-7.5 audit, 2026-05-23):**

No file in the repository sets `W5_AST_NARRATOR_STRICT_ENABLED` to a false value. Files audited:

- `.env`, `.env.*`, `*.env` (none found)
- `docker-compose*.yml` / `docker-compose*.yaml` — no false assignment
- `.github/workflows/**/*.yml` — no false assignment
- `settings*.py`, `config*.py` — no false assignment
- Shell scripts (`scripts/**/*.sh`, `*.sh`) — no false assignment
- Documentation (`docs/**/*.md`) — mentions only as historical/deprecated reference

---

## Context

### State entering this phase

Phase 6B-7 (ADR-0067, Accepted, 2026-05-23) deprecated the narrator strict-off
rollback surface. Entering Phase 6B-8, the runtime state was:

| Posture | Trigger | `source_facts["transition_from_previous"]` | Warning |
|---|---|---|---|
| **Strict-on** (default) | unset / empty / `1/true/yes/on` | **absent** | none |
| **Strict-off** (deprecated rollback) | explicit `0/false/no/off` | **present, first-class** | `NarratorStrictOffDeprecationWarning` once per process |

### Why removal was authorized

1. **W5 projection is the sole actor-situation authority.** Since Phase 6B-5C
   (default-on) and Phase 6B-5D (prompt paragraph removal), the narrator prompt
   no longer instructs the LLM to use `transition_from_previous` as authoritative
   guidance under any posture. The strict-off path produced this payload but the
   prompt labeled it "legacy compatibility information only and not authoritative."
   The payload was computationally wasted.

2. **The rollback window has closed.** `W5_AST_NARRATOR_STRICT_ENABLED` was
   introduced as an emergency rollback in Phase 6B-3B. Strict-on has been the
   permanent default since Phase 6B-5C. No operator rollback was triggered.

3. **`_transition_facts()` was dead code under the default path.** Under strict-on
   (the only production posture since Phase 6B-5C), `_transition_facts()` was
   never called.

4. **`NarratorStrictOffDeprecationWarning` made removal safe.** Any operator
   process that still set `W5_AST_NARRATOR_STRICT_ENABLED=false` would have seen
   the warning immediately upon Phase 6B-7 deployment.

5. **Test suite carried dead strict-off coverage.** Fifteen-plus test functions
   asserted strict-off behavior that became permanently unreachable after removal.

---

## Decision

Remove the narrator strict-off transition rollback surface:

1. **`w5_ast_narrator_strict_enabled()`** is unconditionally `True`. The function
   body is now `return True`. The env-var `W5_AST_NARRATOR_STRICT_ENABLED` no
   longer affects narrator behavior.

2. **`_transition_facts()`** is removed from
   `ai_stack/story_runtime/narrator/god_of_carnage_narrator_path.py`.

3. **The strict-off branch** in `god_of_carnage_narrator_path._block()` that
   emitted `source_facts["transition_from_previous"]` is removed.

4. **`_strict_off_deprecation_warned`** and **`_emit_strict_off_deprecation_warning()`**
   are removed from `ai_stack/actor_tracking/diagnostics.py`.

5. **`NarratorStrictOffDeprecationWarning`** is retained as an empty tombstone
   class in `ai_stack/actor_tracking/diagnostics.py` for import compatibility.
   It is never emitted.

6. **`_location_ref_id()`** and **`_scene_anchor_scene()`** are removed as they
   were only used by the removed `_transition_facts()`.

7. **`_scene_transition()`** is retained — it feeds `_beat_source_facts()` and
   `build_goc_narrator_path_opening()`.

8. **Inventory** reclassifies `transition_from_previous` as `removed_by_adr_0068`.

9. **All strict-off tests** are rewritten to assert strict-on-only behavior.

---

## Consequences

### Accepted

- `W5_AST_NARRATOR_STRICT_ENABLED=false` no longer changes narrator behavior.
  Operators who set this variable will see no runtime effect (no error, no warning).
- `source_facts["transition_from_previous"]` is permanently absent from narrator
  blocks under all environment configurations.
- `NarratorStrictOffDeprecationWarning` can still be imported but is never emitted.
- `W5 where_summary.location_changed` is the sole location-shift signal.
- Test suite no longer covers the strict-off path (it is gone).
- All prior strict-off rollback tests have been rewritten to the strict-on contract.

### Non-consequences (invariants preserved)

- **ADR-0033**: Live runtime commit semantics unchanged.
- **ADR-0061**: Director/Gathering pause semantics unchanged.
- **ADR-0063**: W5 actor-situation authority unchanged. How is first-class.
  Inferred Why is soft truth. OBSERVED facts only from committed substrate.
- **ADR-0065**: W5 narrator strict mode is the permanent default.
- **ADR-0066**: `_legacy_compat["transition_from_previous"]` remains absent.
- **ADR-0067**: Deprecation fulfilled by this removal.
- **Actor Lane / Commit / Readiness / `validation_outcome` / Canonical Path**:
  unchanged.
- **How remains first-class.** `how_summary` is never folded into `what_summary`.
- **Inferred Why remains soft truth.** `why_summary.facts` with
  `truth_attribution = "inferred"` are never narrated as observed fact.
- **Malformed-W5 safety fallback**: unchanged.
- **Public compatibility aliases**: unchanged.
- **Substrate writers/readers**: unchanged.
- **W5 validation (ADR-0065, ADR-0066)**: unchanged.

---

## Rollback Plan

There is no rollback. The strict-off path was the rollback mechanism itself.

If narrator regressions emerge after this removal, the fix is to extend
`build_w5_projection_for_narrator()` or the narrator prompt — not to reinstate
`transition_from_previous` as authoritative.

---

## Test Evidence

Gate tests passed at Phase 6B-8 execution:

- `python -m py_compile` on all changed Python files: clean.
- `python scripts/inventory_w5_legacy_consumers.py`: exits 0; `transition_from_previous` classified as `removed_by_adr_0068`.
- `pytest -q tests/test_inventory_w5_legacy_consumers.py`: 0 failed.
- `pytest -q ai_stack/tests/test_w5_actor_tracking_phase_6b7_strict_off_deprecation.py`: 0 failed (rewritten).
- `pytest -q ai_stack/tests/test_w5_actor_tracking_phase_6b5b_parity.py`: 0 failed (updated).
- `pytest -q ai_stack/tests/test_w5_actor_tracking_phase_6b3b_narrator_strict_migration.py`: 0 failed (updated).
- `pytest -q ai_stack/tests/test_w5_actor_tracking_projection.py ai_stack/tests/test_w5_actor_tracking_validation.py`: 0 failed.
- `pytest -q ai_stack/tests/test_god_of_carnage_narrator_path.py`: 0 failed (updated).
- `PYTHONPATH=world-engine:. pytest -q world-engine/tests/test_story_runtime_w5_narrator_strict_phase_6b5b_parity.py`: 0 failed.
- `PYTHONPATH=world-engine:. pytest -q world-engine/tests/test_story_runtime_w5_narrator_strict_migration.py world-engine/tests/test_story_runtime_w5_narrator_projection.py`: 0 failed.
- `PYTHONPATH=world-engine:. pytest -q world-engine/tests/test_story_runtime_w5_admin_diagnostics.py`: 0 failed.
- `PYTHONPATH=world-engine:. pytest -q world-engine/tests/test_goc_narrator_path_opening.py`: 0 failed (updated).
- `pytest -q tests/gates/test_goc_mvp03_live_dramatic_scene_simulator_gate.py`: 0 failed.
- `pytest -q tests/gates/test_goc_mvp04_observability_diagnostics_gate.py tests/test_local_langfuse_docker_config.py`: 0 failed.
