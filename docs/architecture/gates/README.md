# Architecture gates

Gates verify contracts and SAD decisions against code and CI.

| Gate surface | Command |
| --- | --- |
| Architecture enforcement | `python -m pytest tests/gates/ -v --tb=short --no-cov` |
| Documentation completeness | `python -m pytest tests/gates/test_architecture_documentation_gate.py -v` |
| Canonical test runner | `python tests/run_tests.py --suite engine` |

Owning SAD: [Quality Gates](../project/quality-gates/architecture.md).

Oracle inventory: [`docs/governance/gate_oracle_tightness_inventory.md`](../../governance/gate_oracle_tightness_inventory.md).
