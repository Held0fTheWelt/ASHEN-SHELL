from pathlib import Path

from contractify.adapter.service import ContractifyAdapter
from fy_platform.tests.fixtures_autark import create_target_repo


def test_contractify_consolidate_blocks_safe_apply_when_candidates_are_ambiguous(tmp_path, monkeypatch):
    repo = create_target_repo(tmp_path)
    # create a second equally plausible test file so contractify must stop for review/input
    (repo / 'tests' / 'test_health_contract_secondary.py').write_text(
        'def test_health_contract_secondary():\n    assert True\n',
        encoding='utf-8',
    )
    monkeypatch.chdir(tmp_path)
    adapter = ContractifyAdapter()
    result = adapter.consolidate(str(repo), apply_safe=True)
    assert result['ok'] is True
    assert result['can_apply_safe'] is False
    assert result['decision']['lane'] in {'ambiguous', 'user_input_required', 'abstain'}
    assert result['applied_actions'] == []
