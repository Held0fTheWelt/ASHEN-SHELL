from __future__ import annotations

from fy_platform.ai.base_adapter import BaseSuiteAdapter
from fy_platform.tools import ai_suite_cli


class BrokenAdapter(BaseSuiteAdapter):
    def __init__(self, root=None):
        super().__init__('brokenify', root)

    def audit(self, target_repo_root: str) -> dict:
        raise RuntimeError('boom')


def test_ai_suite_cli_wraps_command_exceptions(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    original = dict(ai_suite_cli.SUITES)
    ai_suite_cli.SUITES['brokenify'] = BrokenAdapter
    try:
        rc = ai_suite_cli.main(['brokenify', 'audit', '--target-repo', str(tmp_path)])
        assert rc == 5
        out = capsys.readouterr().out.lower()
        assert 'command_exception' in out
        assert 'recovery_hints' in out
    finally:
        ai_suite_cli.SUITES.clear()
        ai_suite_cli.SUITES.update(original)
