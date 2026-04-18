from fy_platform.tests.fixtures_autark import create_target_repo
from usabilify.tools.hub_cli import main


def test_usabilify_hub_cli_full(tmp_path, monkeypatch):
    repo = create_target_repo(tmp_path)
    monkeypatch.chdir(tmp_path)
    rc = main(['full', '--repo-root', str(repo)])
    assert rc == 0
