# Testing guide — World of Shadows

This document describes the **current package-level validation entry surface** exposed through `tests/run_tests.py`.

The root `tests/` folder contains:

- the multi-suite orchestrator: `tests/run_tests.py`
- smoke tests: `tests/smoke/`
- reports and validation notes under `tests/reports/`
- this operator-facing guide

It does **not** replace the suite-local `tests/` trees inside the package components.

---

## Current orchestrated suites

`run_tests.py` currently supports these suites:

| Suite | Pytest target | Working directory |
|---|---|---|
| `backend` | `backend/tests` | `backend/` |
| `frontend` | `frontend/tests` | `frontend/` |
| `administration` | `administration-tool/tests` | `administration-tool/` |
| `engine` | `world-engine/tests` | `world-engine/` |
| `writers_room` | `backend/tests/writers_room` | `backend/` |
| `improvement` | `backend/tests/improvement` | `backend/` |
| `ai_stack` | `ai_stack/tests` | repo root |
| `story_runtime_core` | `story_runtime_core/tests` | repo root |

There is **no** `database` suite in the current package runner surface. The package no longer ships a `database/` test tree, so the runner and this guide now reflect the real package surface.

---

## Quick start

From the repository `tests/` directory:

```bash
cd tests
python run_tests.py
```

Cross-platform; use `python3` on Linux/macOS if needed.

---

## `run_tests.py` — options

| Option | Meaning |
|---|---|
| `--suite backend` | Run only the backend suite. |
| `--suite frontend` | Run only the frontend suite. |
| `--suite administration` | Run only the administration-tool suite. |
| `--suite engine` | Run only the world-engine suite. |
| `--suite writers_room` | Run only the Writers' Room backend subset. |
| `--suite improvement` | Run only the improvement backend subset. |
| `--suite ai_stack` | Run only the AI-stack suite from repo root. |
| `--suite story_runtime_core` | Run only the shared story-runtime-core suite from repo root. |
| `--suite backend frontend` | Run those suites in sequence. |
| `--suite all` | Run all currently orchestrated suites (default). |
| `--quick` | No coverage; `-x` (stop on first failure). |
| `--coverage` | Extra HTML coverage report (`term-missing:skip-covered` + `html`). |
| `--verbose` | `-vv`, long tracebacks, `-s`. |
| `--scope …` | **Backend only:** filter by pytest marker (see below). |

### Backend scope (`--scope`)

Applies **only** when the backend suite is included. Other suites always run their full target for that run.

| `--scope` value | Pytest filter |
|---|---|
| `all` (default) | No marker filter |
| `contracts` | `-m contract` |
| `integration` | `-m integration` |
| `e2e` | `-m e2e` |
| `security` | `-m security` |

Examples:

```bash
python run_tests.py --suite backend --scope contracts
python run_tests.py --suite ai_stack story_runtime_core --quick
python run_tests.py --suite all --quick
```

Marker definitions for backend live in `backend/pytest.ini`.

---

### Engine suite bootstrap note

The `engine` suite exercises the **story-runtime** path in addition to the lighter runtime and HTTP surfaces. In a minimal environment, missing heavy dependencies such as `langchain`, `langchain_core`, `langgraph`, or `fastembed` can otherwise cause opaque import-time failures during pytest collection.

Use the package-contained bootstrap path from the repository root before running the engine suite:

```bash
./setup-test-environment.sh
cd tests && python run_tests.py --suite engine --quick
```

On Windows:

```bat
setup-test-environment.bat
cd tests && python run_tests.py --suite engine --quick
```

If preflight still fails, follow the exact actionable message shown by `run_tests.py`. The runner now checks this dependency path **before** pytest collection and stops early with a precise setup instruction instead of surfacing an opaque import failure.

## Coverage thresholds used by the runner

- **Backend:** fail-under `85`
- **Frontend:** fail-under `92`
- **Writers' Room:** fail-under `50`
- **Improvement:** fail-under `50`
- **All other orchestrated suites:** fail-under `80`

These thresholds come from `tests/run_tests.py` and are the current operator truth for the package runner.

---

## JUnit reports

`run_tests.py` writes JUnit XML under `tests/reports/` using filenames like:

```text
pytest_<suite>_YYYYMMDD_HHMMSS.xml
```

---

## Orchestration status of `story_runtime_core`

`story_runtime_core` is now a **first-class package runner suite**.

Why:
- it contains shared interpretation / adapter / delivery contracts used across the MVP package,
- its tests are stable and lightweight,
- and keeping it outside the runner would understate the real package validation surface.

This does **not** make `story_runtime_core` a separate runtime authority. It is a shared-core validation surface only.

---

## Running pytest manually (single suite)

Examples:

```bash
cd backend
python -m pytest tests -v
```

```bash
cd world-engine
python -m pytest tests -v
```

```bash
PYTHONPATH=. python -m pytest -q story_runtime_core/tests -q
```

Use backend markers as needed:

```bash
cd backend
python -m pytest tests -m security -v
```

---

## CI example

```yaml
- run: pip install -r backend/requirements-dev.txt
- run: cd tests && python run_tests.py --suite backend --quick
```

For broader CI validation, install the dependencies required by the selected suites and then run `cd tests && python run_tests.py ...`.

---

## References

- [pytest](https://docs.pytest.org/)
- [Coverage.py](https://coverage.readthedocs.io/)
