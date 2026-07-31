"""Wave 9 (safe): product code must not import the fy-suites tool platform."""

from __future__ import annotations

import ast
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

PRODUCT_ROOTS = (
    "backend",
    "world-engine",
    "frontend",
    "ai_stack",
    "story_runtime_core",
    "administration-tool",
    "database",
)

# Tooling / tests / fy itself may reference the platform; product packages may not.
ALLOWED_PREFIXES = (
    "tests/",
    "tools/",
    "'fy'-suites/",
    "fy-suites/",
    "docs/",
    "scripts/",
)


def _is_fy_import(module: str | None) -> bool:
    if not module:
        return False
    normalized = module.replace("\\", "/")
    return (
        "fy-suites" in normalized
        or normalized.startswith("fy_suites")
        or "'fy'-suites" in normalized
        or normalized.startswith("fy.contractify")
        or normalized.startswith("fy.despaghettify")
        or normalized.startswith("fy.docify")
    )


def test_no_fy_suites_import_in_product() -> None:
    offenders: list[str] = []
    for root_name in PRODUCT_ROOTS:
        root = REPO_ROOT / root_name
        if not root.is_dir():
            continue
        for path in root.rglob("*.py"):
            rel = path.relative_to(REPO_ROOT).as_posix()
            if any(part in {"__pycache__", ".venv", "node_modules"} for part in path.parts):
                continue
            if "/tests/" in f"/{rel}" or rel.endswith("_test.py"):
                continue
            try:
                tree = ast.parse(path.read_text(encoding="utf-8"), filename=rel)
            except SyntaxError:
                continue
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if _is_fy_import(alias.name):
                            offenders.append(f"{rel}: import {alias.name}")
                elif isinstance(node, ast.ImportFrom):
                    if _is_fy_import(node.module):
                        offenders.append(f"{rel}: from {node.module}")
    assert not offenders, "Product packages import fy-suites:\n" + "\n".join(offenders[:40])
