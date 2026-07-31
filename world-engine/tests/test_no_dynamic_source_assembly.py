"""Gate: no dynamic SOURCE / exec(compile) assembly under world-engine/app."""
from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "app"


def _py_files() -> list[Path]:
    return [path for path in ROOT.rglob("*.py") if path.is_file()]


def test_no_source_or_source_lines_modules_under_world_engine_app() -> None:
    offenders: list[str] = []
    for path in _py_files():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id in {"SOURCE", "SOURCE_LINES"}:
                        offenders.append(path.as_posix())
    assert offenders == [], offenders


def test_no_exec_compile_under_world_engine_app() -> None:
    offenders: list[str] = []
    for path in _py_files():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            # exec(compile(...))
            if isinstance(node.func, ast.Name) and node.func.id == "exec":
                if node.args and isinstance(node.args[0], ast.Call):
                    inner = node.args[0]
                    if isinstance(inner.func, ast.Name) and inner.func.id == "compile":
                        offenders.append(f"{path.as_posix()}:{node.lineno}")
    assert offenders == [], offenders


def test_finalize_committed_turn_is_static_python_with_persist() -> None:
    path = ROOT / "story_runtime" / "manager" / "commit_finalization.py"
    text = path.read_text(encoding="utf-8")
    assert "SOURCE" not in text
    assert "exec(compile" not in text
    assert "self._persist_session(session)" in text
