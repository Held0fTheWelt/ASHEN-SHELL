from __future__ import annotations

from fy_platform.ai.final_product import ai_capability_payload, suite_catalog_payload


def test_ai_capability_payload_includes_mvpify(tmp_path):
    payload = ai_capability_payload(tmp_path)
    assert payload['schema_version'] == 'fy.ai-capability.v1'
    assert 'mvpify' in payload['per_suite']
    assert 'prepared MVP import' in ' '.join(payload['per_suite']['mvpify'])


def test_suite_catalog_can_include_mvpify(tmp_path):
    (tmp_path / 'fy_governance_enforcement.yaml').write_text('mode: test\n', encoding='utf-8')
    (tmp_path / 'README.md').write_text('# test\n', encoding='utf-8')
    (tmp_path / 'pyproject.toml').write_text('[project]\nname="x"\nversion="0"\n', encoding='utf-8')
    for req in ['requirements.txt', 'requirements-dev.txt', 'requirements-test.txt']:
        (tmp_path / req).write_text('\n', encoding='utf-8')
    (tmp_path / 'mvpify' / 'adapter').mkdir(parents=True)
    (tmp_path / 'mvpify' / 'adapter' / 'service.py').write_text('', encoding='utf-8')
    (tmp_path / 'mvpify' / 'README.md').write_text('# mvpify\n', encoding='utf-8')
    (tmp_path / 'mvpify' / 'reports').mkdir(parents=True)
    (tmp_path / 'mvpify' / 'state').mkdir(parents=True)
    (tmp_path / 'mvpify' / 'tools').mkdir(parents=True)
    (tmp_path / 'mvpify' / 'templates').mkdir(parents=True)
    payload = suite_catalog_payload(tmp_path)
    assert any(row['suite'] == 'mvpify' for row in payload['suites'])
