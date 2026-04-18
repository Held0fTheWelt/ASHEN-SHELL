from pathlib import Path

from fy_platform.ai.policy.suite_quality_policy import evaluate_suite_quality


def test_mature_optional_tests_paths_count_for_recent_suites(tmp_path: Path) -> None:
    root = tmp_path
    for name in ['securify', 'usabilify', 'observifyfy']:
        suite = root / name
        (suite / 'adapter').mkdir(parents=True)
        (suite / 'tools' / 'tests').mkdir(parents=True)
        (suite / 'reports').mkdir(parents=True)
        (suite / 'state').mkdir(parents=True)
        (suite / 'templates').mkdir(parents=True)
        (suite / 'docs').mkdir(parents=True)
        (suite / 'README.md').write_text('# ok\n', encoding='utf-8')
        (suite / '__init__.py').write_text('', encoding='utf-8')
        (suite / 'adapter' / 'service.py').write_text('', encoding='utf-8')
        (suite / 'adapter' / 'cli.py').write_text('', encoding='utf-8')
    for name in ['requirements.txt', 'requirements-dev.txt', 'requirements-test.txt', 'README.md', 'pyproject.toml']:
        (root / name).write_text('', encoding='utf-8')
    result = evaluate_suite_quality(root, 'securify')
    assert 'missing_optional:tests' not in result['warnings']
