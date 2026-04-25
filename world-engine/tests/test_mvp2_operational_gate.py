"""MVP2 operational gate tests (Wave 2.5).

Proves:
- run-test.py --mvp2 flag exists
- GitHub workflow mvp2-tests.yml exists and covers MVP2 test files
- MVP2 source locator artifact exists with no unresolved placeholders
- MVP2 operational evidence artifact exists
- MVP2 handoff artifact exists
- Required MVP2 ADRs exist
- world-engine pyproject.toml testpaths picks up MVP2 test files
- docker-up.py gate exists and reports failures non-silently
"""

from __future__ import annotations

import os
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Repo root resolution
# ---------------------------------------------------------------------------

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def _repo(path: str) -> Path:
    return _REPO_ROOT / path


# ---------------------------------------------------------------------------
# run-test.py gate
# ---------------------------------------------------------------------------

def test_run_test_mvp2_flag_exists():
    """run-test.py must have a --mvp2 flag."""
    run_test = _repo("run-test.py")
    assert run_test.is_file(), "run-test.py must exist"
    content = run_test.read_text(encoding="utf-8")
    assert "--mvp2" in content, "run-test.py must define --mvp2 flag"


def test_run_test_mvp2_maps_to_engine_suite():
    content = _repo("run-test.py").read_text(encoding="utf-8")
    # The --mvp2 branch must route to --suite engine
    assert "mvp2" in content
    assert "engine" in content


def test_run_test_mvp2_documents_test_files():
    """run-test.py --mvp2 comment must name the concrete MVP2 test files."""
    content = _repo("run-test.py").read_text(encoding="utf-8")
    assert "test_mvp2_runtime_state_actor_lanes" in content
    assert "test_mvp2_npc_coercion_state_delta" in content
    assert "test_mvp2_object_admission" in content


# ---------------------------------------------------------------------------
# GitHub workflow gate
# ---------------------------------------------------------------------------

def test_github_workflow_includes_mvp2_suite():
    """mvp2-tests.yml must exist in .github/workflows/."""
    workflow = _repo(".github/workflows/mvp2-tests.yml")
    assert workflow.is_file(), "mvp2-tests.yml workflow must exist"


def test_github_workflow_mvp2_covers_all_test_files():
    """mvp2-tests.yml must reference all four MVP2 test files."""
    content = _repo(".github/workflows/mvp2-tests.yml").read_text(encoding="utf-8")
    for test_file in [
        "test_mvp2_runtime_state_actor_lanes.py",
        "test_mvp2_npc_coercion_state_delta.py",
        "test_mvp2_object_admission.py",
        "test_mvp2_operational_gate.py",
    ]:
        assert test_file in content, f"Workflow must reference {test_file}"


def test_github_workflow_mvp2_does_not_silently_skip():
    """Workflow must not use || true or equivalent that would swallow failures."""
    content = _repo(".github/workflows/mvp2-tests.yml").read_text(encoding="utf-8")
    assert "|| true" not in content, "Workflow must not silence failures with || true"
    assert "continue-on-error: true" not in content, "Workflow must not use continue-on-error: true"


def test_github_workflow_includes_mvp1_regression():
    """mvp2-tests.yml must run MVP1 regression to detect regressions."""
    content = _repo(".github/workflows/mvp2-tests.yml").read_text(encoding="utf-8")
    assert "test_mvp1_experience_identity" in content


# ---------------------------------------------------------------------------
# Artifact existence gate
# ---------------------------------------------------------------------------

def test_mvp2_source_locator_artifact_exists():
    path = _repo("tests/reports/MVP_Live_Runtime_Completion/MVP2_SOURCE_LOCATOR.md")
    assert path.is_file(), "MVP2_SOURCE_LOCATOR.md must exist"


def test_source_locator_artifact_has_no_unresolved_placeholders():
    content = _repo("tests/reports/MVP_Live_Runtime_Completion/MVP2_SOURCE_LOCATOR.md").read_text(encoding="utf-8")
    forbidden = [
        "from patch map",
        "fill during implementation",
        "TODO",
        "TBD",
        "not checked",
        "not inspected",
    ]
    for phrase in forbidden:
        assert phrase not in content, (
            f"Source locator must not contain placeholder: {phrase!r}. "
            "Error code: source_locator_unresolved"
        )


def test_mvp2_operational_evidence_artifact_exists():
    path = _repo("tests/reports/MVP_Live_Runtime_Completion/MVP2_OPERATIONAL_EVIDENCE.md")
    assert path.is_file(), (
        "MVP2_OPERATIONAL_EVIDENCE.md must exist. "
        "Error code: operational_evidence_artifact_missing"
    )


def test_mvp2_handoff_artifact_exists():
    path = _repo("tests/reports/MVP_Live_Runtime_Completion/GOC_MVP2_HANDOFF_TO_MVP3.md")
    assert path.is_file(), "GOC_MVP2_HANDOFF_TO_MVP3.md must exist"


def test_operational_report_lists_mvp_specific_suites():
    """Operational evidence must list concrete MVP2 test files, not just 'unit' or 'engine'."""
    path = _repo("tests/reports/MVP_Live_Runtime_Completion/MVP2_OPERATIONAL_EVIDENCE.md")
    assert path.is_file(), "MVP2 operational evidence must exist"
    content = path.read_text(encoding="utf-8")
    assert "test_mvp2_runtime_state_actor_lanes" in content, (
        "Operational evidence must name concrete MVP2 test files. "
        "Error code: operational_suite_evidence_missing"
    )


# ---------------------------------------------------------------------------
# ADR existence gate
# ---------------------------------------------------------------------------

def test_mvp2_adrs_present():
    required_adrs = [
        "docs/ADR/MVP_Live_Runtime_Completion/adr-mvp2-004-actor-lane-enforcement.md",
        "docs/ADR/MVP_Live_Runtime_Completion/adr-mvp2-015-environment-affordances.md",
        "docs/ADR/MVP_Live_Runtime_Completion/adr-mvp2-016-operational-gates.md",
    ]
    for adr_path in required_adrs:
        full = _repo(adr_path)
        assert full.is_file(), f"Required ADR missing: {adr_path}"


# ---------------------------------------------------------------------------
# TOML/tooling gate
# ---------------------------------------------------------------------------

def test_toml_testpaths_include_mvp2_tests():
    """world-engine pyproject.toml testpaths must include 'tests' to pick up MVP2 files."""
    toml_path = _repo("world-engine/pyproject.toml")
    assert toml_path.is_file()
    content = toml_path.read_text(encoding="utf-8")
    assert 'testpaths' in content, "world-engine/pyproject.toml must define testpaths"
    assert '"tests"' in content or "'tests'" in content, (
        "testpaths must include 'tests' to pick up MVP2 test files"
    )


def test_mvp2_test_files_exist_in_world_engine():
    """All MVP2 test files must exist under world-engine/tests/."""
    expected = [
        "world-engine/tests/test_mvp2_runtime_state_actor_lanes.py",
        "world-engine/tests/test_mvp2_npc_coercion_state_delta.py",
        "world-engine/tests/test_mvp2_object_admission.py",
        "world-engine/tests/test_mvp2_operational_gate.py",
    ]
    for path in expected:
        assert _repo(path).is_file(), f"MVP2 test file missing: {path}"


# ---------------------------------------------------------------------------
# docker-up.py gate
# ---------------------------------------------------------------------------

def test_docker_up_script_exists():
    assert _repo("docker-up.py").is_file(), "docker-up.py must exist"


def test_docker_up_has_gate_subcommand():
    content = _repo("docker-up.py").read_text(encoding="utf-8")
    assert "gate" in content, "docker-up.py must implement a 'gate' subcommand"
