from fy_platform.tests.fixtures_autark import create_target_repo
from fy_platform.tools.ai_suite_cli import main


def test_generic_ai_suite_cli_securify_audit(tmp_path, monkeypatch, capsys):
    repo = create_target_repo(tmp_path)
    monkeypatch.chdir(tmp_path)
    rc = main(['securify', 'audit', '--target-repo', str(repo)])
    assert rc == 0
    out = capsys.readouterr().out
    assert 'securify' in out.lower()
