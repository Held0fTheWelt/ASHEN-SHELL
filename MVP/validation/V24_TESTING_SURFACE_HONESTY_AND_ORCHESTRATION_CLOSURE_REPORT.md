# V24 Testing-Surface Honesty and Orchestration Closure Report

## Scope

Small closure wave focused on:
- aligning `tests/TESTING.md` with the real package runner surface,
- making the package-level status of `story_runtime_core` explicit,
- removing stale `database` runner exposure that no longer matches the package contents.

## Targeted gap

Before this pass:
- `tests/run_tests.py` exposed suites beyond what `tests/TESTING.md` documented,
- `tests/TESTING.md` still described a four-tree model and a `database` surface that no longer existed in the package,
- `story_runtime_core` had useful validation but no explicit package-level orchestration status.

## Decision

`story_runtime_core` is now treated as a **first-class runner suite**.

Why:
- it is a lightweight shared-core validation surface,
- its tests are stable and package-relevant,
- keeping it manual would understate the actual package validation surface.

This does **not** create a separate runtime authority. It only clarifies package-level validation orchestration.

## Changes made

### `tests/run_tests.py`
- removed stale `database` suite exposure,
- added `story_runtime_core` as a first-class suite,
- ensured repo-root `PYTHONPATH` handling for `story_runtime_core`,
- updated help/description/examples to match the real suite surface.

### `tests/TESTING.md`
- rewritten to document the actual orchestrated suites,
- explicitly states that no `database` suite exists in the current package,
- documents `story_runtime_core` as first-class runner coverage,
- updates operator examples and coverage notes to match current runner behavior.

## Validation executed

### Runner help reflects current suite surface
```bash
cd tests
python run_tests.py --help
```

### Story runtime core now runs through the package runner
```bash
cd tests
python run_tests.py --suite story_runtime_core --quick
```

### Stale database suite is no longer exposed
```bash
cd tests
python run_tests.py --suite database --quick
```
Expected result: argparse rejects `database` as an invalid suite choice.

## Validation result

- runner help updated successfully,
- `story_runtime_core` runner path passed,
- stale `database` suite is no longer accepted,
- testing-surface honesty gap reduced to bounded operator-environment dependency expectations only.

## Residue

The package runner still assumes the operator has installed the dependencies needed for the selected suites. That is expected environment residue, not runner-surface dishonesty.
