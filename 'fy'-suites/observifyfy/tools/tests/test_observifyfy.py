from __future__ import annotations

import json
from pathlib import Path

from observifyfy.tools.hub_cli import run_audit
from observifyfy.tools.repo_paths import fy_adr_root, fy_docs_root


def test_run_audit_creates_internal_roots(tmp_path: Path) -> None:
    (tmp_path / 'pyproject.toml').write_text("[project]\nname='x'\n", encoding='utf-8')
    (tmp_path / '.fydata').mkdir()
    (tmp_path / 'contractify' / 'reports').mkdir(parents=True)
    (tmp_path / 'contractify' / 'state').mkdir(parents=True)
    (tmp_path / 'contractify' / 'tools').mkdir(parents=True)
    (tmp_path / 'contractify' / 'README.md').write_text('x', encoding='utf-8')
    result = run_audit(tmp_path)
    assert result['ok'] is True
    assert fy_docs_root(tmp_path).exists()
    assert fy_adr_root(tmp_path).exists()
    inventory = json.loads((tmp_path / 'observifyfy' / 'reports' / 'observifyfy_inventory.json').read_text(encoding='utf-8'))
    assert inventory['internal_roots']['contractify_internal_adr_root'] == "docs/ADR"


def test_next_steps_mentions_contractify_and_documentify(tmp_path: Path) -> None:
    (tmp_path / 'pyproject.toml').write_text("[project]\nname='x'\n", encoding='utf-8')
    (tmp_path / '.fydata').mkdir()
    result = run_audit(tmp_path)
    actions = result['next_steps']['recommended_next_steps']
    suites = {item['suite'] for item in actions}
    assert 'contractify' in suites
    assert 'documentify' in suites
