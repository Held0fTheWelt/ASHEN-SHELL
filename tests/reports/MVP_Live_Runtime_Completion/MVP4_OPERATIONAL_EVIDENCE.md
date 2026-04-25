# MVP4 Operational Evidence

**MVP**: 04 — Observability, Diagnostics, Langfuse, and Narrative Gov
**Date**: 2026-04-26
**Verdict**: PASS

---

## Commands Executed

### Foundation Preflight

```
python -m pytest tests/gates/test_goc_mvp01_mvp02_foundation_gate.py -q
```
Result: **8 passed**

```
python -m pytest tests/gates/test_goc_mvp03_live_dramatic_scene_simulator_gate.py -q
```
Result: **26 passed**

```
python run-test.py --mvp3 --quick
```
Result: **PASSED**

### MVP4 Gate Tests (root context)

```
python -m pytest tests/gates/test_goc_mvp04_observability_diagnostics_gate.py --no-cov -q
```
Result: **26 passed** (after MVP4_OPERATIONAL_EVIDENCE.md created)

### MVP4 World-Engine Integration Tests

```
cd world-engine && python -m pytest tests/test_mvp4_diagnostics_integration.py --no-cov -q
```
Result: **8 passed**

### Full World-Engine Regression

```
cd world-engine && python -m pytest tests/ --no-cov -q
```
Result: **1136 passed** (1128 prior + 8 new MVP4 integration)

---

## MVP-Specific Test Coverage

```
MVP-specific test coverage:
- unit test files:
    tests/gates/test_goc_mvp04_observability_diagnostics_gate.py (26 tests)
    world-engine/tests/test_mvp4_diagnostics_integration.py (8 tests)
- integration test files:
    world-engine/tests/test_mvp4_diagnostics_integration.py (runs through execute_turn seam)
- e2e/browser test files: none (Narrative Gov UI requires docker-compose, not in scope)
- pytest markers or runner suite names: mvp4
- run-test.py suite entries: --mvp4
- GitHub workflow jobs: .github/workflows/engine-tests.yml (engine-fast-tests job)
- TOML testpaths/markers:
    world-engine/pytest.ini: markers += mvp4
    pytest.ini (root): markers += mvp4
```

---

## Gate Path

```
tests/gates/test_goc_mvp04_observability_diagnostics_gate.py
world-engine/tests/test_mvp4_diagnostics_integration.py
```

## Normal Runner Command

```
python run-test.py --mvp4
```

Equivalent to:
```
python tests/run_tests.py --suite engine   (world-engine MVP4 integration tests)
python -m pytest tests/gates/test_goc_mvp04_observability_diagnostics_gate.py -q --no-cov
```

## Workflow / TOML Registration Evidence

- `run-test.py`: `--mvp4` flag added, runs engine suite + gate file
- `world-engine/pytest.ini`: `mvp4` marker registered
- `pytest.ini` (root): `mvp4` marker registered
- `.github/workflows/engine-tests.yml`: covers world-engine/tests/ which includes MVP4 integration tests

## Langfuse Status

- Disabled in test environment (no credentials)
- `langfuse_status = "disabled"` in all diagnostics_envelope test results
- `langfuse_status = "traced"` behavior tested structurally via `build_local_trace_export()`
- Local trace exports written to `tests/reports/langfuse/` (not static fixtures)

## Coverage Status

- 34 MVP4-specific tests (26 gate + 8 integration)
- 1136 total world-engine tests: all passing
- Gate tests cover all required validation paths per MVP4 guide

## Skipped Suites

- `docker-up.py`: not available in test environment (services not running); Narrative Gov JS rendering requires docker-compose
- Playwright e2e: not in scope for MVP4

## Remaining Blockers

None.

## PASS/FAIL Verdict

**PASS**

26 MVP4 gate tests pass. 8 world-engine integration tests pass. Foundation 8/8. MVP3 26/26.
