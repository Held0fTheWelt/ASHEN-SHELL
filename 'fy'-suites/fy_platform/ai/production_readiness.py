from __future__ import annotations

from pathlib import Path
from typing import Any

from fy_platform.ai.backup_manager import create_workspace_backup, list_backups
from fy_platform.ai.contracts import (
    COMMAND_ENVELOPE_COMPATIBILITY,
    MANIFEST_COMPATIBILITY,
    PRODUCTION_READINESS_SCHEMA_VERSION,
    RELEASE_MANAGEMENT_FILES,
)
from fy_platform.ai.observability import ObservabilityStore
from fy_platform.ai.persistence_state import ensure_schema_state, plan_storage_migrations
from fy_platform.ai.release_readiness import workspace_release_readiness
from fy_platform.ai.security_review import scan_workspace_security
from fy_platform.ai.workspace import utc_now, workspace_root, write_json, write_text, write_platform_doc_artifacts


def _release_management_status(workspace: Path) -> dict[str, Any]:
    missing = [rel for rel in RELEASE_MANAGEMENT_FILES if not (workspace / rel).is_file()]
    return {
        'ok': not missing,
        'missing': missing,
        'required_files': RELEASE_MANAGEMENT_FILES,
    }


def _multi_repo_status(workspace: Path) -> dict[str, Any]:
    fixtures_root = workspace / 'fy_platform' / 'fixtures'
    fixture_dirs = sorted(p.name for p in fixtures_root.iterdir() if p.is_dir()) if fixtures_root.is_dir() else []
    return {
        'ok': len(fixture_dirs) >= 3,
        'fixture_count': len(fixture_dirs),
        'fixtures': fixture_dirs,
    }


def _top_next_steps(release: dict[str, Any], persistence: dict[str, Any], security: dict[str, Any], release_management: dict[str, Any], multi_repo: dict[str, Any], observability: dict[str, Any]) -> list[str]:
    steps: list[str] = []
    if release.get('core_blocked_suites'):
        steps.append(f"Unblock core suites first: {', '.join(release['core_blocked_suites'])}.")
    if persistence.get('migration_plan', {}).get('required'):
        steps.append('Resolve required storage migrations before release.')
    if not security.get('ok'):
        steps.append('Resolve secret-risk findings and verify scope/index exclusions.')
    if release_management.get('missing'):
        steps.append('Complete release-management files before calling the platform production-ready.')
    if not multi_repo.get('ok'):
        steps.append('Add or validate multiple repository fixtures to keep portability honest.')
    if not observability.get('has_metrics'):
        steps.append('Run real suite commands so observability has baseline metrics.')
    if not steps:
        steps.append('Production-hardening MVP checks are green. The next work should be real-world field validation and longer-run stability exercises.')
    return steps[:6]


def workspace_production_readiness(root: Path | None = None, *, create_backup_if_missing: bool = True) -> dict[str, Any]:
    workspace = workspace_root(root)
    release = workspace_release_readiness(workspace)
    schema_state = ensure_schema_state(workspace)
    migration_plan = plan_storage_migrations(workspace)
    backups = list_backups(workspace)
    latest_backup = backups[-1] if backups else None
    if create_backup_if_missing and latest_backup is None:
        latest_backup = create_workspace_backup(workspace, reason='production-readiness-bootstrap')
        backups = list_backups(workspace)
    observability = ObservabilityStore(workspace).summarize()
    security = scan_workspace_security(workspace)
    release_management = _release_management_status(workspace)
    multi_repo = _multi_repo_status(workspace)
    persistence = {
        'ok': not migration_plan['required'],
        'schema_state': schema_state,
        'migration_plan': migration_plan,
        'backup_count': len(backups),
        'latest_backup': latest_backup,
    }
    compatibility = {
        'ok': True,
        'command_envelope': COMMAND_ENVELOPE_COMPATIBILITY,
        'manifest': MANIFEST_COMPATIBILITY,
        'backward_compatibility_rules': [
            'Read support for the previous command-envelope schema stays available while writes stay pinned to the current version.',
            'Manifest support is bounded to declared versions only.',
            'Breaking contract changes require changelog and deprecation entries before release.',
        ],
    }
    recovery = {
        'ok': bool(latest_backup),
        'latest_backup_id': (latest_backup or {}).get('backup_id'),
        'rollback_ready': bool(latest_backup),
        'notes': ['Workspace backups are stored under .fydata/backups and can be rolled back explicitly.'],
    }
    ok = all([
        release['ok'],
        persistence['ok'],
        compatibility['ok'],
        recovery['ok'],
        security['ok'],
        release_management['ok'],
        multi_repo['ok'],
    ])
    return {
        'schema_version': PRODUCTION_READINESS_SCHEMA_VERSION,
        'generated_at': utc_now(),
        'workspace_root': str(workspace),
        'ok': ok,
        'release_readiness': release,
        'persistence': persistence,
        'compatibility': compatibility,
        'recovery': recovery,
        'observability': observability,
        'security': security,
        'release_management': release_management,
        'multi_repo': multi_repo,
        'top_next_steps': _top_next_steps(release, persistence, security, release_management, multi_repo, observability),
    }


def render_workspace_production_markdown(payload: dict[str, Any]) -> str:
    lines = [
        '# fy Workspace Production Readiness',
        '',
        f"- ok: `{str(payload['ok']).lower()}`",
        f"- schema_version: `{payload['schema_version']}`",
        f"- generated_at: `{payload['generated_at']}`",
        '',
        '## Top Next Steps',
        '',
    ]
    lines.extend(f'- {item}' for item in payload.get('top_next_steps', []))
    lines.extend([
        '', '## Persistence', '',
        f"- backup_count: `{payload['persistence']['backup_count']}`",
        f"- migrations_required: `{str(payload['persistence']['migration_plan']['required']).lower()}`",
        '', '## Compatibility', '',
        f"- command_envelope_current: `{payload['compatibility']['command_envelope']['current']}`",
        f"- manifest_current: `{payload['compatibility']['manifest']['current_manifest_version']}`",
        '', '## Observability', '',
        f"- command_event_count: `{payload['observability']['command_event_count']}`",
        f"- route_event_count: `{payload['observability']['route_event_count']}`",
        '', '## Security', '',
        f"- ok: `{str(payload['security']['ok']).lower()}`",
        f"- risky_file_count: `{payload['security']['risky_file_count']}`",
        f"- secret_hit_count: `{payload['security']['secret_hit_count']}`",
        '', '## Release Management', '',
        f"- ok: `{str(payload['release_management']['ok']).lower()}`",
        f"- missing_files: `{len(payload['release_management']['missing'])}`",
        '', '## Multi-repo Stability', '',
        f"- fixture_count: `{payload['multi_repo']['fixture_count']}`",
    ])
    return '\n'.join(lines).strip() + '\n'


def write_workspace_production_site(root: Path | None, payload: dict[str, Any]) -> dict[str, str]:
    workspace = workspace_root(root)
    write_platform_doc_artifacts(workspace, stem='workspace_production_readiness', json_payload=payload, markdown_text=render_workspace_production_markdown(payload))
    md_text = render_workspace_production_markdown(payload)
    write_text(workspace / 'docs' / 'platform' / 'WORKSPACE_PRODUCTION_READINESS.md', md_text)
    return {
        'workspace_production_json_path': str((workspace / 'docs' / 'platform' / 'workspace_production_readiness.json').relative_to(workspace)),
        'workspace_production_md_path': str((workspace / 'docs' / 'platform' / 'WORKSPACE_PRODUCTION_READINESS.md').relative_to(workspace)),
        'workspace_production_internal_json_path': str((workspace / 'docs' / 'platform' / 'workspace_production_readiness.json').relative_to(workspace)),
        'workspace_production_internal_md_path': str((workspace / 'docs' / 'platform' / 'WORKSPACE_PRODUCTION_READINESS.md').relative_to(workspace)),
    }
