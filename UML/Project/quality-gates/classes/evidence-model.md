# Quality Gates - Evidence Model

**Viewpoint:** `class`
**Concern:** Suite definitions, exact executions and actionable findings

[PlantUML source](evidence-model.puml)

## Modeled elements

| Element | Responsibility | Contract | Source |
| --- | --- | --- | --- |
| Suite Definition | Declare scope, prerequisites and owner | Stable suite id | [`tests/run_tests.py`](../../../../tests/run_tests.py) |
| Test Execution | Record exact selected and observed result | Command and environment evidence | [`tests/reports/RUNNER_CI_TRUTH_MATRIX.md`](../../../../tests/reports/RUNNER_CI_TRUTH_MATRIX.md) |
| Quality Finding | Explain failure or coverage omission | Actionable source location | [`tests/reports/WEAK_TESTS_AND_STUBS_AUDIT.md`](../../../../tests/reports/WEAK_TESTS_AND_STUBS_AUDIT.md) |

## Modeled relationships

| From | To | Semantics | Contract | Source |
| --- | --- | --- | --- | --- |
| Suite Definition | Test Execution | produces | exact environment and command | [`tests/run_tests.py`](../../../../tests/run_tests.py) |
| Test Execution | Quality Finding | may emit | source-located evidence | [`tests/reports/WEAK_TESTS_AND_STUBS_AUDIT.md`](../../../../tests/reports/WEAK_TESTS_AND_STUBS_AUDIT.md) |

Generated deterministically from Better Tomorrow's semantic model catalog; edit the catalog, not this projection.
