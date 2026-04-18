from __future__ import annotations

from pathlib import Path

from documentify.tools.track_engine import generate_track_bundle


def test_documentify_generates_status_and_blueprint(tmp_path: Path) -> None:
    (tmp_path / 'docs').mkdir()
    (tmp_path / '.github' / 'workflows').mkdir(parents=True)
    (tmp_path / '.github' / 'workflows' / 'ci.yml').write_text('name: ci', encoding='utf-8')
    (tmp_path / 'README.md').write_text('root', encoding='utf-8')
    out_dir = tmp_path / 'generated'
    manifest = generate_track_bundle(tmp_path, out_dir, maturity='cross-linked')
    assert 'status' in manifest['tracks']
    assert (out_dir / 'technical' / 'DOCS_SITE_BLUEPRINT.md').is_file()
    assert (out_dir / 'status' / 'MOST_RECENT_NEXT_STEPS.md').is_file()
