# V24 Engine Story-Runtime Validation Reproducibility and Preflight Closure

## Summary

This micro-wave closes the remaining operator-facing engine validation entry gap by replacing an opaque import-time pytest collection failure with a package-contained, explicit preflight that stops early and points the operator to the correct bootstrap path.

## Targeted blocker

`cd tests && python run_tests.py --suite engine --quick` previously failed only after pytest collection/import had already started, with an opaque error like:

- `ImportError: cannot import name 'RuntimeTurnGraphExecutor' from 'ai_stack'`

That error was caused by missing heavy story-runtime dependencies (`langchain`, `langchain_core`, `langgraph`, `fastembed`) plus local editable package setup for `story_runtime_core` / `ai_stack[test]`.

## Changes

- Added an engine-suite preflight in `tests/run_tests.py`.
- The preflight checks the heavy story-runtime dependency path before pytest collection starts.
- If the stack is unavailable, the runner now fails early with a precise setup message pointing to:
  - `./setup-test-environment.sh`
  - `setup-test-environment.bat`
  - manual fallback commands for `story_runtime_core` and `ai_stack[test]`
- Updated `tests/TESTING.md` with an explicit engine bootstrap note.

## Validation

Executed:

- `python -m py_compile tests/run_tests.py`
- `cd tests && python run_tests.py --suite engine --quick`
- `cd world-engine && python -m pytest -q tests/test_http_runs.py -q`

Observed:

- The runner now fails early and clearly with a preflight message instead of surfacing the opaque import-time failure.
- Direct test execution still shows the underlying import failure when bypassing the runner, confirming that the proof path itself was not weakened or silently skipped away.

## Closure judgment

Closed for this micro-wave.

The engine validation entry path is now operator-honest and strict-audit-safe:

- either use the package-contained bootstrap path,
- or receive a precise actionable preflight failure.
