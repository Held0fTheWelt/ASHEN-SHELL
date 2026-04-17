from fy_platform.tests.fixtures_autark import create_target_repo
from fy_platform.tools.ai_suite_cli import main


def test_generic_ai_suite_cli_docify_and_contractify_consolidate(tmp_path, monkeypatch, capsys):
    repo = create_target_repo(tmp_path)
    monkeypatch.chdir(tmp_path)
    rc = main(['docify', 'audit', '--target-repo', str(repo)])
    assert rc == 0
    out = capsys.readouterr().out
    assert '"ok": true' in out.lower()

    rc2 = main(['contractify', 'consolidate', '--target-repo', str(repo), '--apply-safe'])
    assert rc2 == 0
    out2 = capsys.readouterr().out
    assert 'contractify' in out2.lower()
