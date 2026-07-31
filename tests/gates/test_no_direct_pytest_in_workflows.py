"""Wave 8: CI must invoke the suite catalog, not bare pytest."""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = REPO_ROOT / ".github" / "workflows"

# Remaining direct-pytest workflows still migrating to ``tests/run_tests.py``.
# Shrink this allowlist until empty (W8 exit criterion).
DIRECT_PYTEST_ALLOWLIST: dict[str, str] = {
    "admin-tests.yml": "pending administration suite catalog invocation",
    "architecture-assurance.yml": "assurance suite pending catalog wiring (G4 WIP adjacent)",
    "ai-stack-tests.yml": "pending map to ai_stack suite family",
    "backend-tests.yml": "pending full backend suite catalog invocation",
    "engine-tests.yml": "pending full engine suite catalog invocation",
    "frontend-tests.yml": "pending mvp5/frontend suite catalog invocation",
    "pre-deployment.yml": "pending multi-suite orchestration via ALL_SUITE_SEQUENCE",
    "quality-gate.yml": "pending gates/security marker suites via catalog",
}

_DIRECT_PYTEST = re.compile(
    r"(?:^|\s)(?:python\s+-m\s+pytest|pytest)\b",
    re.MULTILINE,
)


def test_no_direct_pytest_in_workflows_outside_allowlist() -> None:
    assert WORKFLOWS.is_dir()
    offenders: list[str] = []
    for path in sorted(WORKFLOWS.glob("*.yml")):
        text = path.read_text(encoding="utf-8")
        if not _DIRECT_PYTEST.search(text):
            continue
        rel = path.name
        if rel in DIRECT_PYTEST_ALLOWLIST:
            continue
        offenders.append(rel)
    assert not offenders, (
        "Workflows still call pytest directly; route through tests/run_tests.py "
        f"or add a temporary allowlist reason:\n" + "\n".join(offenders)
    )


def test_direct_pytest_allowlist_entries_exist() -> None:
    stale = sorted(name for name in DIRECT_PYTEST_ALLOWLIST if not (WORKFLOWS / name).is_file())
    assert not stale, f"Stale direct-pytest allowlist entries:\n" + "\n".join(stale)
