"""Wave 8: CI must invoke the suite catalog, not bare pytest."""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = REPO_ROOT / ".github" / "workflows"

# Remaining direct-pytest workflows still migrating to ``tests/run_tests.py``.
# Shrink this allowlist until empty (W8 exit criterion).
# architecture-assurance.yml stays until G4 user WIP on that file is cleared.
DIRECT_PYTEST_ALLOWLIST: dict[str, str] = {
    "architecture-assurance.yml": (
        "G4: user WIP owns this workflow; migrate to "
        "`python tests/run_tests.py --suite architecture_assurance` after WIP lands"
    ),
}

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
    """Hard cap so the allowlist cannot grow during W8/W9."""
    assert len(DIRECT_PYTEST_ALLOWLIST) <= 1, (
        "Direct-pytest allowlist must stay at most architecture-assurance (G4) "
        f"until empty; got {sorted(DIRECT_PYTEST_ALLOWLIST)}"
    )
