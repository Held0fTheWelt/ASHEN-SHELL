"""Structural guards for the unsharded game route module (Wave 5)."""

from __future__ import annotations

import ast
import re
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[1]
GAME_ROUTE_MODULE = BACKEND_ROOT / "app" / "api" / "v1" / "game_routes.py"
GAME_ROUTE_IMPL = BACKEND_ROOT / "app" / "api" / "v1" / "game_routes_impl.py"
GAME_ROUTE_IMPLEMENTATION_DIR = BACKEND_ROOT / "app" / "api" / "v1" / "game"
INVENTORY_BASELINE = (
    BACKEND_ROOT.parent
    / "docs"
    / "superpowers"
    / "plans"
    / "baselines"
    / "W5-game-route-inventory.txt"
)


def test_game_routes_has_no_dynamic_source_loader() -> None:
    text = GAME_ROUTE_MODULE.read_text(encoding="utf-8")
    assert "_IMPLEMENTATION_FILES" not in text
    assert "exec(compiled" not in text
    assert "exec(compile" not in text
    assert "SOURCE =" not in text
    assert "_impl" in text


def test_game_route_impl_is_static_python() -> None:
    assert GAME_ROUTE_IMPL.is_file()
    text = GAME_ROUTE_IMPL.read_text(encoding="utf-8")
    assert "SOURCE =" not in text
    assert "exec(compile" not in text
    tree = ast.parse(text)
    assert any(isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) for n in tree.body)


def test_game_segment_stubs_have_no_source() -> None:
    for path in GAME_ROUTE_IMPLEMENTATION_DIR.glob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        assert target.id not in {"SOURCE", "SOURCE_LINES"}, path.name


def test_game_route_inventory_unchanged() -> None:
    body = GAME_ROUTE_IMPL.read_text(encoding="utf-8")
    pat = re.compile(
        r'@api_v1_bp\.route\(([^)]+)\)\s*\n(?:@[^\n]+\n)*def\s+(\w+)',
        re.M,
    )
    current = [f"{name}\t{args.strip()}" for args, name in pat.findall(body)]
    baseline = [
        line.strip()
        for line in INVENTORY_BASELINE.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    assert current == baseline
    assert len(current) == 29
