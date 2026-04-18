from pathlib import Path
import json

from fy_platform.tests.fixtures_autark import create_target_repo
from contractify.adapter.service import ContractifyAdapter


def test_contractify_consolidate_can_autoresolve_and_apply_safe(tmp_path, monkeypatch):
    repo = create_target_repo(tmp_path)
    (repo / 'tests' / 'test_health_contract.py').write_text(
        'ADR_0001 = True\n\n\ndef test_health_contract_marker():\n    assert ADR_0001 is True\n',
        encoding='utf-8',
    )
    monkeypatch.chdir(tmp_path)
    adapter = ContractifyAdapter()
    result = adapter.consolidate(str(repo), apply_safe=True)
    assert result['ok'] is True
    assert result['can_apply_safe'] is True
    assert result['smart_auto_resolved_count'] >= 1
    assert (repo / 'tests' / 'adr_contract_matrix.py').is_file()
    payload = json.loads(Path(result['json_path']).read_text(encoding='utf-8'))
    assert payload['stats']['smart_auto_resolved_count'] >= 1
