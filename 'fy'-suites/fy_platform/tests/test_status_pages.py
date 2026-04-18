from __future__ import annotations

from pathlib import Path

from fy_platform.ai.base_adapter import BaseSuiteAdapter


class DummyAdapter(BaseSuiteAdapter):
    def __init__(self, root: Path) -> None:
        super().__init__('documentify', root)

    def audit(self, target_repo_root: str) -> dict:
        return self._attach_status_page('audit', {'ok': True, 'suite': self.suite, 'finding_count': 2, 'summary': 'Two issues need attention.'})


def test_status_page_written(tmp_path: Path) -> None:
    (tmp_path / 'README.md').write_text('x', encoding='utf-8')
    (tmp_path / 'fy_platform').mkdir()
    (tmp_path / 'documentify').mkdir()
    (tmp_path / 'documentify' / 'reports').mkdir(parents=True)
    (tmp_path / 'documentify' / 'state').mkdir(parents=True)
    (tmp_path / 'documentify' / 'generated').mkdir(parents=True)
    adapter = DummyAdapter(tmp_path)
    payload = adapter.audit(str(tmp_path))
    assert 'status_md_path' in payload
    md_path = tmp_path / payload['status_md_path']
    assert md_path.is_file()
    text = md_path.read_text(encoding='utf-8')
    assert 'Most-Recent-Next-Steps' in text
    assert 'Two issues need attention.' in text
