from __future__ import annotations

from pathlib import Path

from metrify.adapter.service import MetrifyAdapter


def _workspace(tmp_path: Path) -> Path:
    root = tmp_path / 'ws'
    root.mkdir()
    (root / 'README.md').write_text('workspace\n', encoding='utf-8')
    (root / 'pyproject.toml').write_text('[project]\nname = "demo"\n', encoding='utf-8')
    (root / 'requirements.txt').write_text('\n', encoding='utf-8')
    (root / 'requirements-dev.txt').write_text('\n', encoding='utf-8')
    (root / 'requirements-test.txt').write_text('\n', encoding='utf-8')
    (root / 'fy_platform').mkdir()
    (root / 'fy_governance_enforcement.yaml').write_text('ok: true\n', encoding='utf-8')
    suite = root / 'metrify'
    (suite / 'adapter').mkdir(parents=True)
    (suite / 'tools').mkdir(parents=True)
    (suite / 'reports').mkdir(parents=True)
    (suite / 'state').mkdir(parents=True)
    (suite / 'templates').mkdir(parents=True)
    (suite / 'README.md').write_text('metrify\n', encoding='utf-8')
    (suite / 'adapter' / 'service.py').write_text('# stub\n', encoding='utf-8')
    (suite / 'adapter' / 'cli.py').write_text('# stub\n', encoding='utf-8')
    return root


def test_adapter_audit_runs(tmp_path: Path) -> None:
    root = _workspace(tmp_path)
    target = root / 'target'
    target.mkdir()
    adapter = MetrifyAdapter(root)
    result = adapter.audit(str(target))
    assert result['ok'] is True
    assert 'json_path' in result
