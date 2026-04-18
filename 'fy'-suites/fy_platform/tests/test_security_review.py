from __future__ import annotations

from fy_platform.ai.security_review import scan_workspace_security


def test_security_review_finds_tracked_env_file(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / 'README.md').write_text('x', encoding='utf-8')
    (tmp_path / 'fy_platform').mkdir()
    (tmp_path / '.env').write_text('OPENAI_API_KEY="secret"\n', encoding='utf-8')
    payload = scan_workspace_security(tmp_path)
    assert payload['ok'] is False
    assert payload['risky_file_count'] >= 1 or payload['secret_hit_count'] >= 1
