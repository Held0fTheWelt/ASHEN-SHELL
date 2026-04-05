"""Area 2 Workstream B — reproducibility and environment discipline (G-B-01 .. G-B-07)."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

from app.runtime.area2_validation_commands import (
    AREA2_DUAL_CLOSURE_PYTEST_MODULES,
    area2_dual_closure_pytest_argv,
    area2_dual_closure_pytest_invocation,
)

from . import test_area2_convergence_gates as _conv
from . import test_area2_final_closure_gates as _final

REPO_ROOT = Path(__file__).resolve().parents[3]
BACKEND_ROOT = REPO_ROOT / "backend"


def test_g_b_01_startup_profile_determinism_gate() -> None:
    """G-B-01: named profiles deterministic for bootstrap and registry expectations."""
    _final.test_g_final_01_reproducible_bootstrap_gate()
    _final.test_g_final_01_expected_operational_state_matrix()


def test_g_b_02_bootstrap_reproducibility_gate() -> None:
    """G-B-02: isolated bootstrap-off vs healthy bootstrap-on behaviors are both testable."""
    _final.test_g_final_07_legacy_compatibility_gate()
    _conv.test_g_conv_06_legacy_compatibility_gate()
    _conv.test_g_conv_03_state_classification_gate_matrix()


def test_g_b_03_clean_environment_validation_gate() -> None:
    """G-B-03: explicit setup scripts and requirements paths exist for clean installs."""
    sh = REPO_ROOT / "setup-test-environment.sh"
    bat = REPO_ROOT / "setup-test-environment.bat"
    assert sh.is_file(), "setup-test-environment.sh must exist at repository root"
    assert bat.is_file(), "setup-test-environment.bat must exist at repository root"
    req = BACKEND_ROOT / "requirements.txt"
    rtest = BACKEND_ROOT / "requirements-test.txt"
    assert req.is_file()
    assert rtest.is_file()
    sh_text = sh.read_text(encoding="utf-8", errors="replace")
    bat_text = bat.read_text(encoding="utf-8", errors="replace")
    assert "requirements.txt" in sh_text and "requirements-test.txt" in sh_text
    assert "requirements.txt" in bat_text and "requirements-test.txt" in bat_text


def test_g_b_04_dependency_setup_explicitness_gate() -> None:
    """G-B-04: test requirements explicitly include pytest stack used by Area 2 async suites."""
    rtest = (BACKEND_ROOT / "requirements-test.txt").read_text(encoding="utf-8")
    lower = rtest.lower()
    assert "pytest" in lower
    assert "pytest-asyncio" in lower or "pytest_asyncio" in lower


def test_g_b_05_test_profile_stability_gate() -> None:
    """G-B-05: dual-closure modules collect without provider secrets or undocumented env."""
    env = os.environ.copy()
    for key in list(env.keys()):
        if any(
            p in key.upper()
            for p in (
                "OPENAI",
                "ANTHROPIC",
                "OLLAMA",
                "AZURE_OPENAI",
                "LANGCHAIN_API_KEY",
                "LANGFUSE",
            )
        ):
            env.pop(key, None)
    proc = subprocess.run(
        [sys.executable, *area2_dual_closure_pytest_argv(no_cov=True), "--collect-only"],
        cwd=str(BACKEND_ROOT),
        env=env,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    assert proc.returncode == 0, (
        f"collect-only failed without provider env:\nstdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
    )


def test_g_b_06_validation_command_reality_gate() -> None:
    """G-B-06: documented commands match code constants; collect-only from backend/ works."""
    inv = area2_dual_closure_pytest_invocation(no_cov=True)
    dual = (REPO_ROOT / "docs" / "architecture" / "area2_dual_workstream_closure_report.md").read_text(
        encoding="utf-8"
    )
    setup_doc = (REPO_ROOT / "docs" / "testing-setup.md").read_text(encoding="utf-8")
    assert inv in dual, "dual closure report must embed exact canonical pytest invocation line"
    assert inv in setup_doc, "testing-setup.md must embed the same canonical invocation line"
    for mod in AREA2_DUAL_CLOSURE_PYTEST_MODULES:
        assert mod in dual, f"dual report must list module {mod}"
    proc = subprocess.run(
        [sys.executable, *area2_dual_closure_pytest_argv(no_cov=True), "--collect-only", "-q"],
        cwd=str(BACKEND_ROOT),
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr


def test_g_b_07_documentation_truth_for_reproducibility_gate() -> None:
    """G-B-07: listed docs reference every G-B id and area2_validation_commands."""
    doc_paths = (
        REPO_ROOT / "docs" / "architecture" / "area2_workstream_b_gates.md",
        REPO_ROOT / "docs" / "architecture" / "area2_reproducibility_closure_report.md",
        REPO_ROOT / "docs" / "architecture" / "area2_dual_workstream_closure_report.md",
        REPO_ROOT / "docs" / "testing-setup.md",
        REPO_ROOT / "docs" / "architecture" / "llm_slm_role_stratification.md",
        REPO_ROOT / "docs" / "architecture" / "ai_story_contract.md",
    )
    for path in doc_paths:
        assert path.is_file(), f"missing doc {path}"
        text = path.read_text(encoding="utf-8")
        for n in range(1, 8):
            assert f"G-B-{n:02d}" in text, f"{path.name} missing G-B-{n:02d}"
        assert "area2_validation_commands" in text, f"{path.name} must reference area2_validation_commands"
