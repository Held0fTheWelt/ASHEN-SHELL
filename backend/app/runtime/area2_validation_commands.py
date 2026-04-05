"""Canonical Area 2 dual-workstream validation command surface (Workstream B).

Single source for **G-B-06** (validation-command reality): documented markdown and
tests must stay aligned with these values.

Run from ``backend/`` so ``backend/pytest.ini`` applies (``pythonpath``, ``testpaths``).
Default ``addopts`` enable coverage; gate and closure runs MUST pass ``--no-cov`` to
match documented invocations.
"""

from __future__ import annotations

# Pytest targets: paths relative to backend/ (pytest.ini testpaths = tests).
AREA2_DUAL_CLOSURE_PYTEST_MODULES: tuple[str, ...] = (
    "tests/runtime/test_area2_workstream_a_closure_gates.py",
    "tests/runtime/test_area2_workstream_b_closure_gates.py",
    "tests/runtime/test_area2_task2_closure_gates.py",
    "tests/runtime/test_area2_convergence_gates.py",
    "tests/runtime/test_area2_final_closure_gates.py",
    "tests/runtime/test_cross_surface_operator_audit_contract.py",
    "tests/test_bootstrap_staged_runtime_integration.py",
    "tests/runtime/test_model_inventory_bootstrap.py",
)


def area2_dual_closure_pytest_invocation(*, no_cov: bool = True) -> str:
    """Single-line command string for documentation (shell; cwd = backend)."""
    parts = ["python", "-m", "pytest", *AREA2_DUAL_CLOSURE_PYTEST_MODULES, "-q", "--tb=short"]
    if no_cov:
        parts.append("--no-cov")
    return " ".join(parts)


def area2_dual_closure_pytest_argv(no_cov: bool = True) -> list[str]:
    """Argv for ``python -m pytest`` subprocess from backend cwd."""
    out = ["-m", "pytest", *AREA2_DUAL_CLOSURE_PYTEST_MODULES, "-q", "--tb=short"]
    if no_cov:
        out.append("--no-cov")
    return out
