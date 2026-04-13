from __future__ import annotations

from docify.tools.hub_cli import main


def test_open_doc_lists_doc001(capsys) -> None:
    code = main(["open-doc"])
    assert code == 0
    out = capsys.readouterr().out
    assert "DOC-001" in out
