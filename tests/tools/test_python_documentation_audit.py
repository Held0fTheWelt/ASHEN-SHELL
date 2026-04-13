"""Unit tests for ``'fy'-suites/docify/tools/python_documentation_audit.py``."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "'fy'-suites" / "docify" / "tools" / "python_documentation_audit.py"


def _load_audit_module():
    """Load the script as a module without packaging ``scripts/``."""
    spec = importlib.util.spec_from_file_location("python_documentation_audit", SCRIPT_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


AUDIT = _load_audit_module()


def test_audit_file_detects_missing_docstrings(tmp_path: Path) -> None:
    sample = tmp_path / "sample.py"
    sample.write_text(
        "\n".join(
            [
                "class Example:",
                "    def method(self):",
                "        return 1",
                "",
                "def top_level():",
                "    return 2",
                "",
            ]
        ),
        encoding="utf-8",
    )

    findings = AUDIT.audit_file(sample, rel_path="sample.py", include_private=False)
    kinds = {(f.kind, f.name) for f in findings}

    assert ("module", "<module>") in kinds
    assert ("class", "Example") in kinds
    assert ("method", "method") in kinds
    assert ("function", "top_level") in kinds


def test_iter_python_files_respects_exclude_glob(tmp_path: Path) -> None:
    pkg = tmp_path / "pkg"
    (pkg / "migrations").mkdir(parents=True)
    keep = pkg / "ok.py"
    keep.write_text('"""ok."""\n', encoding="utf-8")
    skipped = pkg / "migrations" / "bad.py"
    skipped.write_text("x = 1\n", encoding="utf-8")

    files = list(
        AUDIT.iter_python_files(
            [pkg],
            repo_root=tmp_path,
            exclude_globs=AUDIT.DEFAULT_EXCLUDE_GLOBS,
            include_tests=True,
        )
    )
    assert keep in files
    assert skipped not in files


def test_main_exit_codes(tmp_path: Path) -> None:
    pkg = tmp_path / "pkg"
    pkg.mkdir()
    (pkg / "thin.py").write_text("def needs_docs():\n    return 1\n", encoding="utf-8")

    base = [
        "--repo-root",
        str(tmp_path),
        "--root",
        "pkg",
    ]
    assert AUDIT.main([*base]) == 1
    assert AUDIT.main([*base, "--exit-zero"]) == 0


def test_google_docstring_audit_accepts_indented_sections(tmp_path: Path) -> None:
    sample = tmp_path / "g.py"
    sample.write_text(
        'def ok(a: int) -> str:\n'
        '    """Short.\n'
        '\n'
        '    Args:\n'
        '        a: x.\n'
        '\n'
        '    Returns:\n'
        '        str:\n'
        '            y.\n'
        '    """\n'
        '    return str(a)\n',
        encoding="utf-8",
    )
    findings = AUDIT.audit_file(
        sample,
        rel_path="g.py",
        include_private=False,
        google_docstring_audit=True,
    )
    bar = [f for f in findings if f.name == "ok"]
    assert not bar


def test_main_reports_syntax_errors(tmp_path: Path) -> None:
    pkg = tmp_path / "pkg"
    pkg.mkdir()
    (pkg / "broken.py").write_text("def broken(:\n    pass\n", encoding="utf-8")

    rc = AUDIT.main(
        [
            "--repo-root",
            str(tmp_path),
            "--root",
            "pkg",
            "--json",
        ]
    )
    assert rc == 2
