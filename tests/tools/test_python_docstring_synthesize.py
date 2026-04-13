"""Unit tests for ``'fy'-suites/docify/tools/python_docstring_synthesize.py`` (inline block comments)."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SYNTH_PATH = REPO_ROOT / "'fy'-suites" / "docify" / "tools" / "python_docstring_synthesize.py"
AUDIT_SCRIPT = REPO_ROOT / "'fy'-suites" / "docify" / "tools" / "python_documentation_audit.py"


def _load_audit_module():
    spec = importlib.util.spec_from_file_location("audit_for_docstring_synth_tests", AUDIT_SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _load_synth_module():
    spec = importlib.util.spec_from_file_location("python_docstring_synthesize", SYNTH_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


SYNTH = _load_synth_module()


def test_plan_block_comments_inserts_for_if_and_return(tmp_path: Path) -> None:
    src = '''def foo(x: int) -> int:
    if x > 0:
        return 1
    return 0
'''
    path = tmp_path / "m.py"
    path.write_text(src, encoding="utf-8")
    inserts, err = SYNTH.plan_block_comments(src, start_line=2, end_line=4, function_name=None)
    assert err is None
    assert inserts
    lines_before = {before for before, _ in inserts}
    assert 2 in lines_before  # if
    assert 4 in lines_before or 3 in lines_before  # return branches


def test_apply_planned_comments(tmp_path: Path) -> None:
    src = '''def bar():
    if True:
        return 3
'''
    path = tmp_path / "m.py"
    path.write_text(src, encoding="utf-8")
    inserts, err = SYNTH.plan_block_comments(src, start_line=2, end_line=3, function_name=None)
    assert err is None
    SYNTH.apply_planned_comments(path, inserts)
    out = path.read_text(encoding="utf-8")
    assert "#" in out
    assert "Branch when" in out or "Branch" in out


def test_emit_google_docstring_has_args_returns_and_type_line() -> None:
    src = "def foo(a: int) -> str:\n    return str(a)\n"
    new_src, err = SYNTH.apply_function_google_docstring(src, "foo")
    assert err is None and new_src
    assert "Args:" in new_src
    assert "Returns:" in new_src
    assert "str:" in new_src
    for line in new_src.splitlines():
        assert len(line) <= 79, line


def test_emit_google_docstring_apply_then_passes_google_audit(tmp_path: Path) -> None:
    src = "def bar(x: int) -> int:\n    return x + 1\n"
    p = tmp_path / "m.py"
    p.write_text(src, encoding="utf-8")
    assert (
        SYNTH.main(
            [
                "--repo-root",
                str(tmp_path),
                "--file",
                str(p.relative_to(tmp_path)),
                "--function",
                "bar",
                "--emit-google-docstring",
                "--apply-docstring",
            ]
        )
        == 0
    )
    audit_mod = _load_audit_module()
    findings = audit_mod.audit_file(
        p,
        rel_path="m.py",
        include_private=False,
        google_docstring_audit=True,
    )
    bar_only = [f for f in findings if f.kind == "function" and f.name == "bar"]
    codes = {f.code for f in bar_only}
    assert "DOCSTRING_MISSING_ARGS_SECTION" not in codes
    assert "DOCSTRING_MISSING_RETURNS_SECTION" not in codes
    assert "DOCSTRING_RETURNS_WITHOUT_TYPE_LINE" not in codes
    assert "DOCSTRING_LINE_OVER_LONG" not in codes


def test_main_json(tmp_path: Path) -> None:
    p = tmp_path / "t.py"
    p.write_text(
        "def g():\n    x = 1\n    return x\n",
        encoding="utf-8",
    )
    out = tmp_path / "o.json"
    code = SYNTH.main(
        [
            "--repo-root",
            str(tmp_path),
            "--file",
            str(p.relative_to(tmp_path)),
            "--start-line",
            "2",
            "--end-line",
            "3",
            "--json",
            "--out",
            str(out),
        ]
    )
    assert code == 0
    payload = __import__("json").loads(out.read_text(encoding="utf-8"))
    assert payload["insertions"]
