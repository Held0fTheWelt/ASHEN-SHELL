from __future__ import annotations

from pathlib import Path

REQUIRED_LIFECYCLE_COMMANDS = (
    'init', 'inspect', 'audit', 'explain', 'prepare-context-pack', 'compare-runs', 'clean', 'reset'
)
CORE_SUITES = {'contractify', 'testify', 'documentify', 'docify', 'despaghettify', 'templatify', 'usabilify', 'securify', 'observifyfy', 'mvpify', 'metrify'}
OPTIONAL_SUITES = {'dockerify', 'postmanify'}


def evaluate_workspace_quality(workspace_root: Path) -> dict:
    required_root_files = ['README.md', 'pyproject.toml', 'requirements.txt', 'requirements-dev.txt', 'requirements-test.txt']
    missing = [rel for rel in required_root_files if not (workspace_root / rel).exists()]
    warnings: list[str] = []
    if not (workspace_root / 'fy_governance_enforcement.yaml').exists():
        warnings.append('missing:fy_governance_enforcement.yaml')
    return {
        'ok': not missing,
        'missing': missing,
        'warnings': warnings,
    }


def evaluate_suite_quality(workspace_root: Path, suite: str) -> dict:
    suite_root = workspace_root / suite
    required = [
        'README.md',
        'adapter/service.py',
        'adapter/cli.py',
        'tools',
        'reports',
        'state',
    ]
    if suite in CORE_SUITES:
        required.append('templates')
    missing: list[str] = []
    for rel in required:
        if not (suite_root / rel).exists():
            missing.append(rel)
    warnings: list[str] = []
    if not (suite_root / 'docs').exists():
        warnings.append('missing_optional:docs')
    if not any((suite_root / rel).exists() for rel in ['tests', 'adapter/tests', 'tools/tests']):
        warnings.append('missing_optional:tests')
    if not (suite_root / '__init__.py').exists():
        warnings.append('missing_optional:__init__.py')
    return {
        'ok': not missing,
        'suite': suite,
        'missing': missing,
        'warnings': warnings,
    }
