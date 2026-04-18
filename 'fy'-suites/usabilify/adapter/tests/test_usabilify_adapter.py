from fy_platform.tests.fixtures_autark import create_target_repo
from usabilify.adapter.service import UsabilifyAdapter


def test_usabilify_adapter_audit(tmp_path, monkeypatch):
    repo = create_target_repo(tmp_path)
    monkeypatch.chdir(tmp_path)
    adapter = UsabilifyAdapter()
    audit = adapter.audit(str(repo))
    assert audit['ok'] is True
    assert audit['area_count'] >= 5
    assert 'status_md_path' in audit
    assert audit['average_score'] >= 0
