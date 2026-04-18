from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fy_platform.ai.policy.suite_quality_policy import CORE_SUITES, OPTIONAL_SUITES, evaluate_suite_quality, evaluate_workspace_quality
from fy_platform.ai.workspace import utc_now, write_json, write_text, workspace_root, write_platform_doc_artifacts
from fy_platform.ai.evidence_registry.registry import EvidenceRegistry

STATUS_REL_JSON = Path('reports/status/most_recent_next_steps.json')
STATUS_REL_MD = Path('reports/status/MOST_RECENT_NEXT_STEPS.md')


def _load_status_json(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except (OSError, json.JSONDecodeError):
        return None


def suite_release_readiness(workspace: Path, suite: str) -> dict[str, Any]:
    workspace = workspace_root(workspace)
    registry = EvidenceRegistry(workspace)
    latest = registry.latest_run(suite)
    suite_check = evaluate_suite_quality(workspace, suite)
    status = _load_status_json(workspace / suite / STATUS_REL_JSON)
    has_run = latest is not None
    latest_ok = bool(latest and latest.get('status') == 'ok')
    next_steps = list((status or {}).get('next_steps', []))[:8]
    warnings = list((status or {}).get('warnings', []))
    if suite_check['warnings']:
        warnings.extend(item for item in suite_check['warnings'] if item not in warnings)
    ready = bool(suite_check['ok'] and has_run and latest_ok)
    blocking_reasons: list[str] = []
    if not suite_check['ok']:
        blocking_reasons.extend([f'missing:{item}' for item in suite_check['missing']])
    if not has_run:
        blocking_reasons.append('no_successful_run_recorded')
    elif not latest_ok:
        blocking_reasons.append(f"latest_run_status:{latest.get('status')}")
    return {
        'suite': suite,
        'ready': ready,
        'has_run': has_run,
        'latest_run': latest,
        'status_page_json': str((workspace / suite / STATUS_REL_JSON).relative_to(workspace)) if (workspace / suite / STATUS_REL_JSON).is_file() else None,
        'status_page_md': str((workspace / suite / STATUS_REL_MD).relative_to(workspace)) if (workspace / suite / STATUS_REL_MD).is_file() else None,
        'next_steps': next_steps,
        'warnings': warnings,
        'blocking_reasons': blocking_reasons,
        'suite_check': suite_check,
    }


def workspace_release_readiness(workspace: Path, suites: list[str] | None = None) -> dict[str, Any]:
    workspace = workspace_root(workspace)
    workspace_check = evaluate_workspace_quality(workspace)
    if suites is None:
        suites = sorted({*CORE_SUITES, *OPTIONAL_SUITES, *[p.name for p in workspace.iterdir() if p.is_dir() and (p / 'adapter').is_dir()]})
    suite_rows = [suite_release_readiness(workspace, suite) for suite in suites if (workspace / suite).is_dir()]
    core_ready = [row['suite'] for row in suite_rows if row['suite'] in CORE_SUITES and row['ready']]
    core_missing = [row['suite'] for row in suite_rows if row['suite'] in CORE_SUITES and not row['ready']]
    optional_ready = [row['suite'] for row in suite_rows if row['suite'] in OPTIONAL_SUITES and row['ready']]
    optional_missing = [row['suite'] for row in suite_rows if row['suite'] in OPTIONAL_SUITES and not row['ready']]
    ok = bool(workspace_check['ok'] and not core_missing)
    return {
        'schema_version': 'fy.workspace-release-readiness.v1',
        'generated_at': utc_now(),
        'workspace_root': str(workspace),
        'ok': ok,
        'workspace_check': workspace_check,
        'core_ready_suites': core_ready,
        'core_blocked_suites': core_missing,
        'optional_ready_suites': optional_ready,
        'optional_blocked_suites': optional_missing,
        'suites': suite_rows,
    }


def render_workspace_release_markdown(payload: dict[str, Any]) -> str:
    lines = [
        '# fy Workspace Release Readiness',
        '',
        f"- ok: `{str(payload['ok']).lower()}`",
        f"- generated_at: `{payload['generated_at']}`",
        f"- core_ready: `{len(payload.get('core_ready_suites', []))}`",
        f"- core_blocked: `{len(payload.get('core_blocked_suites', []))}`",
        '',
        '## Core suites',
        '',
    ]
    for row in payload.get('suites', []):
        if row['suite'] not in CORE_SUITES:
            continue
        lines.append(f"- `{row['suite']}` ready=`{str(row['ready']).lower()}` latest_run=`{(row['latest_run'] or {}).get('run_id', 'none')}`")
        for reason in row.get('blocking_reasons', []):
            lines.append(f"  - blocking: `{reason}`")
        for step in row.get('next_steps', [])[:3]:
            lines.append(f"  - next: {step}")
    if payload.get('optional_ready_suites') or payload.get('optional_blocked_suites'):
        lines.extend(['', '## Optional suites', ''])
        for row in payload.get('suites', []):
            if row['suite'] not in OPTIONAL_SUITES:
                continue
            lines.append(f"- `{row['suite']}` ready=`{str(row['ready']).lower()}`")
    return '\n'.join(lines).strip() + '\n'


def write_workspace_release_site(workspace: Path, payload: dict[str, Any]) -> dict[str, str]:
    workspace = workspace_root(workspace)
    paths = write_platform_doc_artifacts(workspace, stem='workspace_release_readiness', json_payload=payload, markdown_text=render_workspace_release_markdown(payload))
    # Preserve legacy uppercase markdown filename alongside the mirrored internal copy.
    md_text = render_workspace_release_markdown(payload)
    write_text(workspace / 'docs' / 'platform' / 'WORKSPACE_RELEASE_READINESS.md', md_text)
    return {
        'workspace_status_json_path': str((workspace / 'docs' / 'platform' / 'workspace_release_readiness.json').relative_to(workspace)),
        'workspace_status_md_path': str((workspace / 'docs' / 'platform' / 'WORKSPACE_RELEASE_READINESS.md').relative_to(workspace)),
        'workspace_status_internal_json_path': str((workspace / 'docs' / 'platform' / 'workspace_release_readiness.json').relative_to(workspace)),
        'workspace_status_internal_md_path': str((workspace / 'docs' / 'platform' / 'WORKSPACE_RELEASE_READINESS.md').relative_to(workspace)),
    }
