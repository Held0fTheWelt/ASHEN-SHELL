from pathlib import Path
import json

from fy_platform.tests.fixtures_autark import create_target_repo
from despaghettify.adapter.service import DespaghettifyAdapter


def test_despaghettify_generates_wave_plan(tmp_path, monkeypatch):
    repo = create_target_repo(tmp_path)
    spike = repo / 'src' / 'spike.py'
    spike.write_text('\n'.join(['x = 1'] * 420), encoding='utf-8')
    monkeypatch.chdir(tmp_path)
    adapter = DespaghettifyAdapter()
    audit = adapter.audit(str(repo))
    assert audit['ok'] is True
    payload = json.loads(Path(audit['json_path']).read_text(encoding='utf-8'))
    assert payload['wave_plan']['action_count'] >= 1
    assert payload['global_category'] == 'low'
