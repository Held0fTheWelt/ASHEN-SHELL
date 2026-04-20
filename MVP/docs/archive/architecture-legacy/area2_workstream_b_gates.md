# Area 2 Workstream B Gates

This workstream is documented against `area2_validation_commands`.

## G-B gates
- G-B-01 — reproducibility / validation command gate.
- G-B-02 — reproducibility / validation command gate.
- G-B-03 — reproducibility / validation command gate.
- G-B-04 — reproducibility / validation command gate.
- G-B-05 — reproducibility / validation command gate.
- G-B-06 — reproducibility / validation command gate.
- G-B-07 — reproducibility / validation command gate.

## Canonical command surface
- module: `area2_validation_commands`
- dual closure invocation: `python -m pytest tests/runtime/test_runtime_routing_registry_composed_proofs.py tests/runtime/test_runtime_operational_bootstrap_and_routing_registry.py tests/runtime/test_runtime_startup_profiles_operator_truth.py tests/runtime/test_cross_surface_operator_audit_contract.py tests/test_bootstrap_staged_runtime_integration.py tests/runtime/test_model_inventory_bootstrap.py -q --tb=short --no-cov`
- task4 closure invocation: `python -m pytest tests/runtime/test_runtime_routing_registry_composed_proofs.py tests/runtime/test_runtime_operational_bootstrap_and_routing_registry.py tests/runtime/test_runtime_startup_profiles_operator_truth.py tests/runtime/test_cross_surface_operator_audit_contract.py tests/test_bootstrap_staged_runtime_integration.py tests/runtime/test_model_inventory_bootstrap.py tests/runtime/test_runtime_operator_comparison_cross_surface.py tests/runtime/test_runtime_ai_turn_degraded_paths_tool_loop.py tests/runtime/test_runtime_drift_resistance.py tests/runtime/test_runtime_staged_orchestration.py tests/runtime/test_runtime_model_ranking_synthesis_contracts.py tests/improvement/test_improvement_model_routing_denied.py tests/runtime/test_ai_turn_executor.py::test_agent_orchestration_executes_real_separate_subagents_and_logs_trace tests/runtime/test_runtime_validation_commands_orchestration.py -q --tb=short --no-cov`
