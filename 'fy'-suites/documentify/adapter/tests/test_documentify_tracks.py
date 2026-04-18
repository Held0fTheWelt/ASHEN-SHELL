from fy_platform.tests.fixtures_autark import create_target_repo
from documentify.adapter.service import DocumentifyAdapter
from pathlib import Path
import json


def test_documentify_generates_track_manifest_and_ai_bundle(tmp_path, monkeypatch):
    repo = create_target_repo(tmp_path)
    monkeypatch.chdir(tmp_path)
    adapter = DocumentifyAdapter()
    audit = adapter.audit(str(repo))
    assert audit['ok'] is True
    generated_dir = Path(audit['generated_dir'])
    manifest = json.loads((generated_dir / 'document_manifest.json').read_text(encoding='utf-8'))
    assert 'ai-read' in manifest['tracks']
    assert (generated_dir / 'ai-read' / 'bundle.json').is_file()
    assert (generated_dir / 'INDEX.md').is_file()
