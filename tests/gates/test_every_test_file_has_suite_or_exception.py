"""Wave 8: every test file belongs to a suite catalog entry or a reasoned exception."""

from __future__ import annotations

import ast
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
RUN_TESTS = REPO_ROOT / "tests" / "run_tests.py"
EXCEPTIONS = REPO_ROOT / "tests" / "suite_catalog_exceptions.txt"

SEARCH_ROOTS = (
    "backend/tests",
    "world-engine/tests",
    "ai_stack/tests",
    "story_runtime_core/tests",
    "frontend/tests",
    "tests",
)


def _string_literals_from_run_tests() -> set[str]:
    tree = ast.parse(RUN_TESTS.read_text(encoding="utf-8"))
    literals: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            literals.add(node.value.replace("\\", "/"))
    return literals


def _load_exceptions() -> dict[str, str]:
    if not EXCEPTIONS.is_file():
        return {}
    out: dict[str, str] = {}
    for raw in EXCEPTIONS.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "|" not in line:
            raise AssertionError(f"Malformed suite exception (need path|reason): {line}")
        path, reason = [part.strip() for part in line.split("|", 1)]
        assert reason, f"Suite exception missing reason: {path}"
        out[path.replace("\\", "/")] = reason
    return out


def _discover_test_files() -> list[str]:
    found: list[str] = []
    for root_name in SEARCH_ROOTS:
        root = REPO_ROOT / root_name
        if not root.exists():
            continue
        for path in root.rglob("test_*.py"):
            if any(part in {"__pycache__", ".worktrees", ".claude"} for part in path.parts):
                continue
            found.append(path.relative_to(REPO_ROOT).as_posix())
    return sorted(set(found))


def _covered(rel: str, literals: set[str]) -> bool:
    if rel in literals:
        return True
    # Directory targets in the catalog cover children.
    parts = rel.split("/")
    for i in range(1, len(parts)):
        prefix = "/".join(parts[:i])
        if prefix in literals or (prefix + "/") in {lit if lit.endswith("/") else lit + "/" for lit in literals}:
            # Exact dir token match used by SuiteConfig targets like "tests/model_governance"
            if prefix in literals:
                return True
    # Common pattern: target="tests" under a package cwd covers that tree only via suite, not path string.
    # Treat known package test roots as covered when their package suite exists.
    if rel.startswith("backend/tests/") and ("tests" in literals or "backend" in literals):
        return True
    if rel.startswith("world-engine/tests/") and ("tests" in literals or "engine" in literals):
        return True
    if rel.startswith("ai_stack/tests/") and ("ai_stack" in literals or "tests" in literals):
        return True
    if rel.startswith("frontend/tests/") and ("frontend" in literals or "mvp5" in literals):
        return True
    if rel.startswith("story_runtime_core/tests/") and "story_runtime_core" in literals:
        return True
    if rel.startswith("tests/") and any(
        lit == "tests" or lit.startswith("tests/") for lit in literals
    ):
        # Root tests/ files need explicit mention or directory target under PROJECT_ROOT suites.
        parent = str(Path(rel).parent).replace("\\", "/")
        return parent in literals or rel in literals or any(
            lit.startswith(parent + "/") or parent.startswith(lit.rstrip("/") + "/")
            for lit in literals
            if lit.startswith("tests")
        )
    return False


def test_every_test_file_has_suite_or_exception() -> None:
    literals = _string_literals_from_run_tests()
    exceptions = _load_exceptions()
    orphans: list[str] = []
    for rel in _discover_test_files():
        if rel in exceptions:
            continue
        if _covered(rel, literals):
            continue
        orphans.append(rel)
    assert not orphans, (
        "Test files missing from suite catalog (tests/run_tests.py) and exceptions file:\n"
        + "\n".join(orphans[:80])
        + (f"\n... and {len(orphans) - 80} more" if len(orphans) > 80 else "")
    )


def test_suite_catalog_exceptions_are_not_stale() -> None:
    exceptions = _load_exceptions()
    stale = [path for path in exceptions if not (REPO_ROOT / path).is_file()]
    assert not stale, "Stale suite catalog exceptions:\n" + "\n".join(stale)
