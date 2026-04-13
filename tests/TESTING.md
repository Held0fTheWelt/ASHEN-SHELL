# Testing guide — World of Shadows

This document describes how to run the **multi-component** test suites using the orchestrator [`run_tests.py`](run_tests.py) in this directory. Pytest trees live in **several repositories** under the monorepo; the runner exposes **eight** named suites (seven distinct pytest cwd/path pairs — `writers_room` and `improvement` share `backend/` as cwd).

The root `tests/` folder holds the **orchestrator** (`run_tests.py`), smoke assets (`tests/smoke/`), reports (`tests/reports/`), and this file. It does **not** replace each component’s own `tests/` root.

---

## Quick start

From the **repository root** (recommended):

```bash
python tests/run_tests.py
```

Or from `tests/`:

```bash
cd tests
python run_tests.py
```

Cross-platform; use `python3` on Linux/macOS if needed.

---

## Canonical `--suite` list

| CLI name | Working directory | Pytest path | Notes |
|----------|-------------------|-------------|--------|
| `backend` | `backend/` | `tests` | Collects entire `backend/tests/`, including `writers_room/` and `improvement/` subtrees. |
| `frontend` | `frontend/` | `tests` | Player/public Flask UI tests. |
| `administration` | `administration-tool/` | `tests` | Admin proxy and UI tests. |
| `engine` | `world-engine/` | `tests` | FastAPI runtime, HTTP/WS. |
| `database` | `database/` | `tests` | Schema/migration tests (often import `backend/app` models). |
| `writers_room` | `backend/` | `tests/writers_room` | **Slice** run: Writers-Room tests only (also collected under full `backend`). |
| `improvement` | `backend/` | `tests/improvement` | **Slice** run: improvement-loop tests only. |
| `ai_stack` | **repo root** | `ai_stack/tests` | Requires `PYTHONPATH` including repo root (runner sets this). |

---

## `--suite all` semantics

`--suite all` (or default `--suite` omitted) runs **six** suites **in order**:

1. `backend`  
2. `frontend`  
3. `administration`  
4. `engine`  
5. `database`  
6. `ai_stack`  

`writers_room` and `improvement` are **not** separate orchestrator steps here: they are already part of `backend`’s `pytest tests` collection. That avoids **double-running** the same tests when you also had explicit slice suites.

To run **only** Writers-Room or improvement tests (e.g. focused coverage):

```bash
python tests/run_tests.py --suite writers_room
python tests/run_tests.py --suite improvement
```

---

## `--scope` (pytest marker filter)

`--scope` maps to `pytest -m <marker>` **only** for suites that define the markers in their `pytest.ini` / `pyproject.toml`.

| Suite | `contracts` | `integration` | `e2e` | `security` |
|-------|-------------|-----------------|-------|-------------|
| `backend` | `-m contract` | `-m integration` | `-m e2e` | `-m security` |
| `writers_room` | same | same | same | same |
| `improvement` | same | same | same | same |
| `administration` | `-m contract` | `-m integration` | **full suite** (no `e2e` marker) | `-m security` |
| `engine` | `-m contract` | `-m integration` | **full suite** (no `e2e` marker) | `-m security` |
| `frontend` | **ignored** — always full suite | | | |
| `database` | **ignored** — always full suite | | | |
| `ai_stack` | **ignored** — always full suite | | | |

When scope is set but not applied, the runner prints an `[INFO]` line (see `run_tests.py`).

---

## `--quick`, `--stats`, `--continue-on-failure`

| Flag | Effect |
|------|--------|
| `--quick` | Each suite: `pytest --no-cov -x` (stop on first **test** failure in that suite). **Skips** the pre-run `pytest --collect-only` stats pass (unless `--stats`). **Stops the orchestrator** after the first **suite** that fails (unless `--continue-on-failure`). |
| `--stats` | With `--quick`, still run the collect-only stats pass first. |
| `--continue-on-failure` | With `--quick`, run all selected suites even if one fails. |

Without `--quick`, the runner always runs collect-only first; a non-zero collection exit code **fails the whole run** before pytest executes.

---

## Coverage (`pytest-cov`) per suite

Behavior is implemented in [`run_tests.py`](run_tests.py) (`_cov_sources_for_suite`, `_cov_fail_under_for_suite`, `build_pytest_argv`).

| Suite | `--cov=` roots (each passed as its own flag) | `--cov-fail-under` |
|-------|-----------------------------------------------|---------------------|
| `backend` | `backend/app` | 85 |
| `frontend` | `frontend/app` | 92 |
| `writers_room` | `backend/app` | 50 |
| `improvement` | `backend/app` | 50 |
| `administration` | `--cov=.` + `administration-tool/.coveragerc` (flat tree; tests omitted) | 80 |
| `engine` | `world-engine/app` (path) | 80 |
| `database` | `backend/app` | *(none — instrumentation only; see semantics doc)* |
| `ai_stack` | `ai_stack/` (repo path) | 80 |

- **Default** (no `--coverage`, no `--verbose`): `-v --tb=short`, term-missing report, fail-under as above.  
- **`--coverage`**: adds HTML report and `term-missing:skip-covered`.  
- **`--verbose`**: `-vv --tb=long -s` plus same cov flags as default.  
- **`--quick`**: **no** coverage flags for pytest (`--no-cov`).

**Semantics:** coverage measures **in-process** Python lines touched by tests. It does **not** measure production realism (real network, browser, DB load, or LLM variability). See [`docs/testing/COVERAGE_SEMANTICS.md`](../docs/testing/COVERAGE_SEMANTICS.md).

---

## `run_tests.py` — option summary

| Option | Meaning |
|--------|---------|
| `--suite …` | One or more suite names, or `all` (see above). |
| `--scope …` | Marker filter where supported (see matrix). |
| `--quick` | Fast fail; see table above. |
| `--stats` | Force collect-only with `--quick`. |
| `--continue-on-failure` | Run all suites with `--quick` even after a failure. |
| `--coverage` | HTML + stricter cov reporting. |
| `--verbose` | Verbose pytest + long tracebacks. |

---

## Makefile (optional)

From `tests/`:

| Target | Command |
|--------|---------|
| `make test` | `python3 run_tests.py` |
| `make test-quick` | `python3 run_tests.py --quick` |
| `make test-coverage` | `python3 run_tests.py --coverage` |
| `make test-contracts` | `python3 run_tests.py --suite backend --scope contracts` |
| `make test-integration` | `python3 run_tests.py --suite backend --scope integration` |

---

## JUnit reports

`run_tests.py` writes JUnit XML under `tests/reports/` (`pytest_<suite>_YYYYMMDD_HHMMSS.xml`).

---

## Running pytest manually (single component)

Always set the working directory to the component that owns the code under test:

```bash
cd backend
python -m pytest tests -v
```

---

## Optional: Compose smoke lane

For a **production-narrow** path (real HTTP/WS, services up), see [`smoke/compose_smoke/README.md`](smoke/compose_smoke/README.md).

---

## Optional: Browser E2E (Playwright)

Critical UI flows (login, play shell) are scaffolded under [`e2e/`](e2e/README.md) (`@playwright/test`). Not part of the default `run_tests.py` Python orchestrator.

---

## CI example

```yaml
- run: pip install -r backend/requirements-dev.txt
- run: python tests/run_tests.py --suite backend --quick
```

Install dependencies per component before `python tests/run_tests.py --suite all`.

---

## References

- [pytest](https://docs.pytest.org/)
- [Coverage.py](https://coverage.readthedocs.io/)
