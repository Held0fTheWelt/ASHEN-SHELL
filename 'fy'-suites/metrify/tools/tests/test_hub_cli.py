from __future__ import annotations

import json
from pathlib import Path

from metrify.tools.hub_cli import main


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
    return root


def test_cli_record_and_report(tmp_path: Path, monkeypatch) -> None:
    root = _workspace(tmp_path)
    monkeypatch.setenv('METRIFY_REPO_ROOT', str(root))
    assert main(['record', '--suite', 'contractify', '--run-id', 'r1', '--model', 'gpt-5.4-mini', '--timestamp-utc', '2026-04-18T00:00:00+00:00', '--input-tokens', '1000', '--output-tokens', '1000', '--quiet']) == 0
    assert main(['report', '--quiet']) == 0
    payload = json.loads((root / 'metrify' / 'reports' / 'metrify_cost_report.json').read_text(encoding='utf-8'))
    assert payload['event_count'] == 1
