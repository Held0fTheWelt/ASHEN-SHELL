"""Gate: no dynamic SOURCE / exec(compile) under world-engine/app, ai_stack/langgraph, backend game+governance."""
from __future__ import annotations

import ast
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
WE_APP = REPO / "world-engine" / "app"
AI_STACK_LANGGRAPH = REPO / "ai_stack" / "langgraph"
BACKEND_TARGETS = (
    REPO / "backend" / "app" / "api" / "v1" / "game",
    REPO / "backend" / "app" / "api" / "v1" / "game_routes.py",
    REPO / "backend" / "app" / "api" / "v1" / "game_routes_impl.py",
    REPO / "backend" / "app" / "services" / "governance" / "governance_runtime",
    REPO / "backend" / "app" / "services" / "governance" / "governance_runtime_service.py",
    REPO / "backend" / "app" / "services" / "governance" / "governance_runtime_service_impl.py",
)


def _py_files(root: Path) -> list[Path]:
    if root.is_file():
        return [root]
    return [path for path in root.rglob("*.py") if path.is_file()]


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def _source_offenders(root: Path) -> list[str]:
    offenders: list[str] = []
    for path in _py_files(root):
        tree = ast.parse(_read_text(path), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id in {"SOURCE", "SOURCE_LINES"}:
                        offenders.append(path.as_posix())
    return offenders


def _exec_compile_offenders(root: Path) -> list[str]:
    offenders: list[str] = []
    for path in _py_files(root):
        tree = ast.parse(_read_text(path), filename=str(path))
        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue
            if isinstance(node.func, ast.Name) and node.func.id == "exec":
                if node.args and isinstance(node.args[0], ast.Call):
                    inner = node.args[0]
                    if isinstance(inner.func, ast.Name) and inner.func.id == "compile":
                        offenders.append(f"{path.as_posix()}:{node.lineno}")
    return offenders


def test_no_source_or_source_lines_modules_under_world_engine_app() -> None:
    assert _source_offenders(WE_APP) == []


def test_no_exec_compile_under_world_engine_app() -> None:
    assert _exec_compile_offenders(WE_APP) == []


def test_no_source_lines_under_ai_stack_langgraph() -> None:
    assert _source_offenders(AI_STACK_LANGGRAPH) == []


def test_no_exec_compile_under_ai_stack_langgraph() -> None:
    assert _exec_compile_offenders(AI_STACK_LANGGRAPH) == []


def test_no_source_under_backend_game_and_governance() -> None:
    offenders: list[str] = []
    for root in BACKEND_TARGETS:
        offenders.extend(_source_offenders(root))
    assert offenders == []


def test_no_exec_compile_under_backend_game_and_governance() -> None:
    offenders: list[str] = []
    for root in BACKEND_TARGETS:
        offenders.extend(_exec_compile_offenders(root))
    assert offenders == []


def test_finalize_committed_turn_is_static_python_with_persist() -> None:
    path = WE_APP / "story_runtime" / "manager" / "commit_finalization.py"
    text = path.read_text(encoding="utf-8")
    assert "SOURCE" not in text
    assert "exec(compile" not in text
    assert "self._persist_session(session)" in text
