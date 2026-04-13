from __future__ import annotations

from pathlib import Path

from docify.tools.python_documentation_audit import audit_file


def test_audit_file_flags_missing_module_docstring(tmp_path: Path) -> None:
    path = tmp_path / "sample.py"
    path.write_text("def public() -> int:\n    return 1\n", encoding="utf-8")
    findings = audit_file(path, rel_path="sample.py", include_private=False)
    kinds = {f.kind for f in findings}
    assert "module" in kinds
    assert "function" in kinds


def test_audit_skips_visit_methods_on_private_visitor(tmp_path: Path) -> None:
    path = tmp_path / "visitor.py"
    path.write_text(
        "import ast\n\n"
        "class _V(ast.NodeVisitor):\n"
        "    def visit_Name(self, node: ast.Name) -> None:\n"
        "        return None\n",
        encoding="utf-8",
    )
    findings = audit_file(path, rel_path="visitor.py", include_private=False)
    names = {f.name for f in findings}
    assert "visit_Name" not in names
