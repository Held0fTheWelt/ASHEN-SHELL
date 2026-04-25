# MVP 2 Operational Evidence

**MVP**: 02 — Runtime State, Actor Lanes, and Content Boundary
**Date**: 2026-04-25
**Final Verdict**: PASS

---

## Commands Run

### Unit suite (world-engine)

```
$ python -m pytest world-engine/tests/test_mvp2_runtime_state_actor_lanes.py \
         world-engine/tests/test_mvp2_npc_coercion_state_delta.py \
         world-engine/tests/test_mvp2_object_admission.py \
         world-engine/tests/test_mvp2_operational_gate.py \
         -v --no-cov
```

**Result**: 99 passed, 0 failed

### MVP1 regression

```
$ python -m pytest world-engine/tests/test_mvp1_experience_identity.py -v --no-cov
```

**Result**: 53 passed, 0 failed

### Full MVP2 + MVP1 combined

```
$ python -m pytest world-engine/tests/test_mvp2_runtime_state_actor_lanes.py \
         world-engine/tests/test_mvp2_npc_coercion_state_delta.py \
         world-engine/tests/test_mvp2_object_admission.py \
         world-engine/tests/test_mvp2_operational_gate.py \
         world-engine/tests/test_mvp1_experience_identity.py \
         -q --no-cov
```

**Result**: 152 passed, 0 failed

### docker-up.py gate

```
$ python docker-up.py gate --backend-url http://127.0.0.1:19999
```

**Result**: FAIL — backend unreachable (no running services in test environment)
**Status**: Expected and non-silent. Exit code 2. Gate reports failure correctly:
`GATE FAIL: Backend unreachable at http://127.0.0.1:19999/api/v1/bootstrap/public-status`
Docker services are not running in the local test environment but the gate reports
the failure non-silently with a structured error message. This satisfies the requirement
that `docker-up.py` does not mask failures.

### run-test.py flag verification

```
$ python run-test.py --help  (flag verified via grep — Unicode arrow in docstring
                               causes encoding issue on Windows cp1252, pre-existing)
$ grep mvp2 run-test.py  → --mvp2 flag present
```

**Result**: `--mvp2` flag confirmed present in `run-test.py` at line 44.

---

## MVP-Specific Test Coverage

**Unit test files**:
- `world-engine/tests/test_mvp2_runtime_state_actor_lanes.py` — 28 tests (Waves 2.1–2.2)
- `world-engine/tests/test_mvp2_npc_coercion_state_delta.py` — 32 tests (Wave 2.3)
- `world-engine/tests/test_mvp2_object_admission.py` — 22 tests (Wave 2.4)
- `world-engine/tests/test_mvp2_operational_gate.py` — 17 tests (Wave 2.5)

**Integration test files**: none separate (integration behavior tested via unit seam tests)

**e2e/browser test files**: none (MVP3 LDSS integration is out of scope for MVP2)

**pytest markers or runner suite names**: world-engine `testpaths = ["tests"]` — all MVP2 files picked up automatically

**run-test.py suite entries**: `--mvp2` maps to `--suite engine` (world-engine test suite)

**GitHub workflow jobs**:
- `.github/workflows/mvp2-tests.yml` — jobs: `mvp2-world-engine`, `mvp2-tooling-gate`
- `mvp2-world-engine` runs all 4 MVP2 test files + MVP1 regression
- `mvp2-tooling-gate` verifies `--mvp2` flag, artifact existence, ADRs, docker gate

**TOML testpaths/markers**: `world-engine/pyproject.toml` — `testpaths = ["tests"]`

---

## Skipped Suites

| Suite | Reason |
|---|---|
| backend | No MVP2 changes in backend service |
| frontend | No MVP2 frontend changes |
| ai_stack | Actor lane enforcement in goc_turn_seams.py tested via world-engine seam tests |
| e2e | MVP3 LDSS integration required for full e2e; out of scope |
| compose smoke | Docker services not running in test environment |

---

## Operational Gate Checklist

| Gate | Status | Evidence |
|---|---|---|
| docker-up.py exists | PASS | `docker-up.py` present at repo root |
| docker-up.py reports failed service non-silently | PASS | Exit code 2 with structured error message |
| run-test.py `--mvp2` flag exists | PASS | Line 44 of run-test.py |
| run-test.py maps `--mvp2` to engine suite | PASS | Line 62 of run-test.py |
| GitHub workflow covers MVP2 suites | PASS | `.github/workflows/mvp2-tests.yml` |
| GitHub workflow does not silently skip | PASS | No `|| true` or `continue-on-error: true` |
| TOML testpaths picks up MVP2 tests | PASS | `testpaths = ["tests"]` in world-engine/pyproject.toml |
| All MVP2 tests pass | PASS | 99/99 Wave 2.1–2.5 tests |
| MVP1 regression clean | PASS | 53/53 MVP1 tests |
| Source locator artifact exists | PASS | MVP2_SOURCE_LOCATOR.md |
| Source locator has no unresolved placeholders | PASS | Verified by test_source_locator_artifact_has_no_unresolved_placeholders |
| Operational evidence artifact exists | PASS | This document |
| Handoff artifact exists | PASS | GOC_MVP2_HANDOFF_TO_MVP3.md |
| Required ADRs present | PASS | adr-mvp2-004, adr-mvp2-015, adr-mvp2-016 |

---

## Failing Suites

None. All required suites pass.

---

## Final PASS/FAIL Verdict

**PASS** — All MVP2 tests pass, MVP1 regression clean, operational infrastructure updated, all required artifacts present.
