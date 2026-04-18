from pathlib import Path

from docify.tools.python_inline_explain import annotate_function_inline, main

SAMPLE = """
def helper():
    json_path = run_dir / f"{role_prefix}.json"
    write_json(json_path, payload)
    self.registry.record_artifact(payload=payload)
    return {"json_path": str(json_path)}
""".lstrip()


def test_annotate_function_inline_adds_contextful_comments() -> None:
    rendered = annotate_function_inline(SAMPLE, 'helper', mode='dense')
    assert 'Build filesystem locations' in rendered
    assert 'Persist the structured JSON representation' in rendered
    assert 'Register the written artifact in the evidence registry' in rendered
    assert 'Return the final outward-facing result' in rendered


def test_inline_explain_cli_writes_output(tmp_path: Path) -> None:
    src = tmp_path / 'sample.py'
    out = tmp_path / 'annotated.py'
    src.write_text(SAMPLE, encoding='utf-8')
    code = main(['--file', str(src), '--function', 'helper', '--output', str(out)])
    assert code == 0
    text = out.read_text(encoding='utf-8')
    assert 'Build filesystem locations' in text
