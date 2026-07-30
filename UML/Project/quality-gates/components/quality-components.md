# Quality Gates - Components

**Viewpoint:** `component`
**Concern:** Selection, execution, boundary proof, evidence and CI promotion

[PlantUML source](quality-components.puml)

## Modeled elements

| Element | Responsibility | Contract | Source |
| --- | --- | --- | --- |
| Test Selector | Map changes and profiles to declared suites | No silent omission | [`scripts/test_changed.py`](../../../../scripts/test_changed.py) |
| Central Runner | Execute subsystem and cross-system suites | One authoritative orchestration path | [`tests/run_tests.py`](../../../../tests/run_tests.py) |
| Architecture and Contract Gates | Enforce boundaries and anti-hardcoding policy | Behavioral assertions | [`tests/gates/test_table_b_anti_hardcoding_gate.py`](../../../../tests/gates/test_table_b_anti_hardcoding_gate.py) |
| Integration and E2E | Prove real authority boundaries and user paths | Disposable dependencies and production path | [`tests/integration/test_story_runtime_experience.py`](../../../../tests/integration/test_story_runtime_experience.py) |
| Evidence Reporter | Expose selected, executed, skipped and failed scope | Machine-readable and human summary | [`tests/reports/RUNNER_CI_TRUTH_MATRIX.md`](../../../../tests/reports/RUNNER_CI_TRUTH_MATRIX.md) |
| CI Policy | Apply required gates to repository changes | Blocking workflow matrix | [`.github/workflows/quality-gate.yml`](../../../../.github/workflows/quality-gate.yml) |

## Modeled relationships

| From | To | Semantics | Contract | Source |
| --- | --- | --- | --- | --- |
| Test Selector | Central Runner | supplies selected suites | selection rationale | [`scripts/test_changed.py`](../../../../scripts/test_changed.py) |
| Central Runner | Architecture and Contract Gates | executes static and contract gates | blocking assertions | [`tests/run_tests.py`](../../../../tests/run_tests.py) |
| Central Runner | Integration and E2E | executes boundary proof | disposable test environment | [`tests/run_tests.py`](../../../../tests/run_tests.py) |
| Architecture and Contract Gates | Evidence Reporter | emits findings | selected/executed truth | [`tests/reports/RUNNER_CI_TRUTH_MATRIX.md`](../../../../tests/reports/RUNNER_CI_TRUTH_MATRIX.md) |
| Integration and E2E | Evidence Reporter | emits evidence | production-path outcome | [`tests/integration/test_story_runtime_experience.py`](../../../../tests/integration/test_story_runtime_experience.py) |
| Evidence Reporter | CI Policy | controls promotion | exit status and artifacts | [`.github/workflows/quality-gate.yml`](../../../../.github/workflows/quality-gate.yml) |

Generated deterministically from Better Tomorrow's semantic model catalog; edit the catalog, not this projection.
