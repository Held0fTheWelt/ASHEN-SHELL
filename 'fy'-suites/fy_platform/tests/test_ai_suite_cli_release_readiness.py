from __future__ import annotations

from fy_platform.tests.fixtures_autark import create_target_repo
from fy_platform.tools.ai_suite_cli import main


def test_generic_ai_suite_cli_supports_self_audit_and_release_readiness(tmp_path, monkeypatch, capsys):
    repo = create_target_repo(tmp_path)
    monkeypatch.chdir(tmp_path)
    rc = main(['contractify', 'audit', '--target-repo', str(repo)])
    assert rc == 0
    _ = capsys.readouterr().out
    rc2 = main(['contractify', 'self-audit'])
    assert rc2 == 0
    out2 = capsys.readouterr().out.lower()
    assert 'schema_version' in out2
    rc3 = main(['contractify', 'release-readiness'])
    assert rc3 == 0
    out3 = capsys.readouterr().out.lower()
    assert 'release-readiness' in out3
