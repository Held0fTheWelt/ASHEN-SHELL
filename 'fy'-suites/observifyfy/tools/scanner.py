from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .models import SuiteObservation
from .repo_paths import ensure_internal_layout, fy_adr_root, fy_docs_root, fy_internal_root, fy_observifyfy_root

KNOWN_SUITES = [
    'contractify',
    'documentify',
    'docify',
    'despaghettify',
    'dockerify',
    'testify',
    'templatify',
    'usabilify',
    'securify',
    'cryptify',
    'decryptify',
    'observifyfy',
    'mvpify',
    'metrify',
]


def _suite_root(repo_root: Path, suite: str) -> Path:
    return repo_root / suite


def _status_files(suite_root: Path) -> list[str]:
    out: list[str] = []
    status_dir = suite_root / 'reports' / 'status'
    if status_dir.is_dir():
        out.extend(str(p.relative_to(suite_root)) for p in sorted(status_dir.glob('*')) if p.is_file())
    return out


def _workflow_count(repo_root: Path, suite: str) -> int:
    wf_root = repo_root / '.github' / 'workflows'
    if not wf_root.is_dir():
        return 0
    return sum(1 for p in wf_root.glob(f'*{suite}*.yml')) + sum(1 for p in wf_root.glob(f'*{suite}*.yaml'))


def _count_files(path: Path) -> int:
    if not path.exists():
        return 0
    if path.is_file():
        return 1
    return sum(1 for p in path.rglob('*') if p.is_file())


def scan_workspace(repo_root: Path) -> dict[str, Any]:
    created = ensure_internal_layout(repo_root)
    observations: list[SuiteObservation] = []
    journal_root = repo_root / '.fydata' / 'journal'
    runs_root = repo_root / '.fydata' / 'runs'
    for suite in KNOWN_SUITES:
        root = _suite_root(repo_root, suite)
        exists = root.exists()
        obs = SuiteObservation(
            name=suite,
            hub_path=str(root.relative_to(repo_root)),
            exists=exists,
            has_readme=(root / 'README.md').exists(),
            has_reports=(root / 'reports').exists(),
            has_state=(root / 'state').exists(),
            has_tools=(root / 'tools').exists(),
            has_adapter=(root / 'adapter').exists(),
            run_count=_count_files(runs_root / suite),
            journal_count=_count_files(journal_root / suite),
            workflow_count=_workflow_count(repo_root, suite),
            status_files=_status_files(root),
        )
        if exists and not obs.has_readme:
            obs.warnings.append('missing_readme')
        if exists and not obs.has_state:
            obs.warnings.append('missing_state')
        if exists and not obs.has_reports:
            obs.warnings.append('missing_reports')
        if exists and obs.workflow_count == 0:
            obs.warnings.append('missing_workflow')
        observations.append(obs)
    internal_roots = {
        'fy_internal_root': str(fy_internal_root(repo_root).relative_to(repo_root)),
        'contractify_internal_adr_root': str(fy_adr_root(repo_root).relative_to(repo_root)),
        'documentify_internal_docs_root': str(fy_docs_root(repo_root).relative_to(repo_root)),
        'observifyfy_root': str(fy_observifyfy_root(repo_root).relative_to(repo_root)),
    }
    docs_summary = {
        'docs_file_count': _count_files(fy_docs_root(repo_root)),
        'adr_file_count': _count_files(fy_adr_root(repo_root)),
    }
    return {
        'created_internal_layout': created,
        'suite_count': len(observations),
        'existing_suite_count': sum(1 for item in observations if item.exists),
        'suites': [item.to_dict() for item in observations],
        'internal_roots': internal_roots,
        'docs_summary': docs_summary,
    }


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
