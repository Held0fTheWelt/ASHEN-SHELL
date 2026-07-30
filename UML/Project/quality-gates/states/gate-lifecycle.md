# Quality Gates - Lifecycle

**Viewpoint:** `state`
**Concern:** Declared and selected suites cannot silently bypass execution

[PlantUML source](gate-lifecycle.puml)

## Modeled elements

| Element | Responsibility | Contract | Source |
| --- | --- | --- | --- |
| Declared | Register suite and purpose | Discoverable by central runner | [`tests/run_tests.py`](../../../../tests/run_tests.py) |
| Selected | Include suite for current scope | Selection reason visible | [`scripts/test_changed.py`](../../../../scripts/test_changed.py) |
| Executed | Run all selected tests | No hidden skip | [`tests/run_tests.py`](../../../../tests/run_tests.py) |
| Accepted | Permit promotion | All required gates pass | [`.github/workflows/quality-gate.yml`](../../../../.github/workflows/quality-gate.yml) |
| Failed | Block promotion with evidence | Actionable finding | [`tests/reports/RUNNER_CI_TRUTH_MATRIX.md`](../../../../tests/reports/RUNNER_CI_TRUTH_MATRIX.md) |

## Modeled relationships

| From | To | Semantics | Contract | Source |
| --- | --- | --- | --- | --- |
| Initial | Declared | suite registered | owner and purpose | catalog contract |
| Declared | Selected | profile requires suite | selection visible | catalog contract |
| Selected | Executed | runner invokes suite | command recorded | [`tests/run_tests.py`](../../../../tests/run_tests.py) |
| Executed | Accepted | all assertions pass | required evidence | catalog contract |
| Executed | Failed | assertion or discovery fails | blocking finding | catalog contract |

Generated deterministically from Better Tomorrow's semantic model catalog; edit the catalog, not this projection.
