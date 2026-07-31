"""Wave 8: CI must invoke the suite catalog, not bare pytest."""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = REPO_ROOT / ".github" / "workflows"

# Remaining direct-pytest workflows still migrating to ``tests/run_tests.py``.
# W8 exit criterion: this allowlist must stay empty.
DIRECT_PYTEST_ALLOWLIST: dict[str, str] = {}

# Flag shell invocations of pytest only (not pip installs, job names, or comments).
_DIRECT_PYTEST = re.compile(
    r"^\s*(?:-\s+)?(?:python\s+-m\s+pytest|pytest)\s+",
    re.MULTILINE,
)


def _workflow_direct_pytest_lines(text: str) -> list[str]:
    hits: list[str] = []
    for line in text.splitlines():
        stripped = line.lstrip()
        if stripped.startswith("#"):
            continue
        if _DIRECT_PYTEST.search(line):
            hits.append(line.strip())
    return hits


def test_no_direct_pytest_in_workflows_outside_allowlist() -> None:
    assert WORKFLOWS.is_dir()
    offenders: list[str] = []
    for path in sorted(WORKFLOWS.glob("*.yml")):
        text = path.read_text(encoding="utf-8")
        hits = _workflow_direct_pytest_lines(text)
        if not hits:
            continue
        rel = path.name
        if rel in DIRECT_PYTEST_ALLOWLIST:
            continue
        offenders.append(f"{rel}: {hits[0]}")
    assert not offenders, (
        "Workflows still call pytest directly; route through tests/run_tests.py "
        f"or add a temporary allowlist reason:\n" + "\n".join(offenders)
    )


def test_direct_pytest_allowlist_entries_exist() -> None:
    stale = sorted(name for name in DIRECT_PYTEST_ALLOWLIST if not (WORKFLOWS / name).is_file())
    assert not stale, f"Stale direct-pytest allowlist entries:\n" + "\n".join(stale)


def test_direct_pytest_allowlist_is_draining() -> None:
    """Hard cap: direct pytest in workflows is forbidden (allowlist empty)."""
    assert len(DIRECT_PYTEST_ALLOWLIST) == 0, (
        "Direct-pytest allowlist must be empty; migrate remaining workflows to "
        f"tests/run_tests.py — got {sorted(DIRECT_PYTEST_ALLOWLIST)}"
    )
