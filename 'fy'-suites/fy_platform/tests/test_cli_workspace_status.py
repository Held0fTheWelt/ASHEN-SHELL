from __future__ import annotations

import json
from pathlib import Path

from fy_platform.tools.cli import main


def test_platform_bootstrap_contains_new_suites(tmp_path: Path, capsys) -> None:
    code = main(['bootstrap', '--project-root', str(tmp_path)])
    assert code == 0
    manifest = tmp_path / 'fy-manifest.yaml'
    raw = manifest.read_text(encoding='utf-8')
    assert 'templatify:' in raw
    assert 'usabilify:' in raw
    _ = capsys.readouterr().out


def test_platform_workspace_status_and_release_readiness(tmp_path: Path, capsys, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / 'README.md').write_text('x', encoding='utf-8')
    (tmp_path / 'pyproject.toml').write_text('[project]\nname = "fy"\nversion = "0.0.0"\n', encoding='utf-8')
    (tmp_path / 'requirements.txt').write_text('', encoding='utf-8')
    (tmp_path / 'requirements-dev.txt').write_text('', encoding='utf-8')
    (tmp_path / 'requirements-test.txt').write_text('', encoding='utf-8')
    (tmp_path / 'fy_governance_enforcement.yaml').write_text('enabled: true\n', encoding='utf-8')
    (tmp_path / 'fy_platform').mkdir()
    (tmp_path / 'contractify' / 'adapter').mkdir(parents=True)
    (tmp_path / 'contractify' / 'reports' / 'status').mkdir(parents=True)
    (tmp_path / 'contractify' / 'state').mkdir(parents=True)
    (tmp_path / 'contractify' / 'tools').mkdir(parents=True)
    (tmp_path / 'contractify' / 'templates').mkdir(parents=True)
    (tmp_path / 'contractify' / 'README.md').write_text('x', encoding='utf-8')
    (tmp_path / 'contractify' / '__init__.py').write_text('', encoding='utf-8')
    (tmp_path / 'contractify' / 'adapter' / 'service.py').write_text('', encoding='utf-8')
    (tmp_path / 'contractify' / 'adapter' / 'cli.py').write_text('', encoding='utf-8')
    code = main(['workspace-status', '--project-root', str(tmp_path)])
    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload['suite_count'] >= 1
    code2 = main(['release-readiness', '--project-root', str(tmp_path)])
    assert code2 in {0, 3}
    payload2 = json.loads(capsys.readouterr().out)
    assert 'workspace_status_md_path' in payload2
