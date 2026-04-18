"""Fy platform bootstrap and workspace governance CLI."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence

import yaml

from fy_platform.ai.backup_manager import create_workspace_backup, rollback_workspace_backup
from fy_platform.ai.observability import ObservabilityStore
from fy_platform.ai.production_readiness import workspace_production_readiness, write_workspace_production_site
from fy_platform.ai.release_readiness import workspace_release_readiness, write_workspace_release_site
from fy_platform.ai.workspace_status_site import build_workspace_status_site, write_workspace_status_site
from fy_platform.ai.final_product import ai_capability_payload, command_reference_payload, doctor_payload, export_contract_schemas, final_release_bundle, render_ai_capability_markdown, render_command_reference_markdown, render_doctor_markdown, render_suite_catalog_markdown, suite_catalog_payload
from fy_platform.ai.workspace import write_platform_doc_artifacts
from fy_platform.core.manifest import load_manifest, manifest_path
from fy_platform.core.project_resolver import resolve_project_root

CORE_SUITES = [
    'contractify',
    'testify',
    'documentify',
    'docify',
    'despaghettify',
    'templatify',
    'usabilify',
    'securify',
    'observifyfy',
]
OPTIONAL_SUITES = ['dockerify', 'postmanify']


def _detect_roots(repo: Path) -> dict[str, list[str]]:
    buckets = {
        'source': ['backend', 'world-engine', 'ai_stack', 'story_runtime_core', 'frontend', 'writers-room', 'src'],
        'docs': ['docs'],
        'tests': ['tests'],
        'templates': ['templates', 'frontend/templates', 'administration-tool/templates'],
    }
    out: dict[str, list[str]] = {key: [] for key in buckets}
    for bucket, candidates in buckets.items():
        for rel in candidates:
            if (repo / rel).exists():
                out[bucket].append(rel)
    return out


def build_manifest_payload(repo: Path) -> dict:
    roots = _detect_roots(repo)
    project_id = repo.name.lower().replace(' ', '-')
    payload = {
        'manifestVersion': 1,
        'platformVersion': '1.0',
        'compat': 'autark-outbound',
        'generatedBy': {
            'tool': 'fy-platform bootstrap',
            'generated_at': datetime.now(timezone.utc).isoformat(),
        },
        'project': {
            'id': project_id,
            'name': repo.name,
            'repository_type': 'python-project',
        },
        'roots': roots,
        'docsStrategy': {
            'tracks': ['easy', 'technical', 'role-admin', 'role-developer', 'role-operator', 'role-writer', 'ai-read', 'status'],
            'status_pages': True,
            'outbound_only': True,
        },
        'suites': {},
    }
    source_roots = roots['source'] or ['src']
    payload['suites']['contractify'] = {'roots': roots['docs'] + source_roots, 'openapi': 'docs/api/openapi.yaml'}
    payload['suites']['testify'] = {'roots': roots['tests'] or ['tests'], 'ci_workflows': ['.github/workflows']}
    payload['suites']['documentify'] = {'roots': roots['docs'] + source_roots, 'tracks': payload['docsStrategy']['tracks']}
    payload['suites']['docify'] = {'roots': source_roots}
    payload['suites']['despaghettify'] = {'scan_roots': source_roots, 'spike_policy': 'local-and-global'}
    payload['suites']['templatify'] = {'template_roots': roots['templates'] or ['templates']}
    payload['suites']['usabilify'] = {'ui_roots': roots['templates'] or roots['docs']}
    payload['suites']['observifyfy'] = {'internal_roots': ["docs", "docs/ADR"], 'role': 'internal-fy-observability'}
    payload['suites']['metrify'] = {'ledger_root': 'metrify/state', 'role': 'ai-usage-observer'}
    payload['suites']['dockerify'] = {'enabled': True, 'compose_roots': ['docker-compose.yml', 'compose.yml']}
    payload['suites']['postmanify'] = {'enabled': True, 'openapi': 'docs/api/openapi.yaml'}
    return payload


def _resolve_repo(project_root: str) -> Path:
    if project_root:
        return Path(project_root).expanduser().resolve()
    return resolve_project_root(start=Path(__file__), env_var='FY_PLATFORM_PROJECT_ROOT', marker_text=None)


def cmd_bootstrap(args: argparse.Namespace) -> int:
    repo = _resolve_repo(args.project_root)
    path = manifest_path(repo)
    if path.is_file() and not args.force:
        print(json.dumps({'ok': False, 'reason': 'manifest_exists', 'path': str(path.relative_to(repo))}, indent=2))
        return 2
    payload = build_manifest_payload(repo)
    text = yaml.safe_dump(payload, sort_keys=False)
    path.write_text(text, encoding='utf-8')
    print(json.dumps({'ok': True, 'manifest': str(path.relative_to(repo)), 'suite_count': len(payload['suites'])}, indent=2))
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    repo = _resolve_repo(args.project_root)
    manifest, warnings = load_manifest(repo)
    if manifest is None:
        print(json.dumps({'ok': False, 'warnings': warnings or ['manifest_missing']}, indent=2))
        return 2
    suite_names = sorted((manifest.get('suites') or {}).keys()) if isinstance(manifest, dict) else []
    payload = {'ok': not warnings, 'manifest': 'fy-manifest.yaml', 'warnings': warnings, 'suite_count': len(suite_names), 'suites': suite_names}
    print(json.dumps(payload, indent=2))
    return 0 if not warnings else 2


def cmd_workspace_status(args: argparse.Namespace) -> int:
    repo = _resolve_repo(args.project_root)
    payload = build_workspace_status_site(repo)
    payload.update(write_workspace_status_site(repo, payload))
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


def cmd_release_readiness(args: argparse.Namespace) -> int:
    repo = _resolve_repo(args.project_root)
    payload = workspace_release_readiness(repo)
    payload.update(write_workspace_release_site(repo, payload))
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0 if payload['ok'] else 3




def cmd_production_readiness(args: argparse.Namespace) -> int:
    repo = _resolve_repo(args.project_root)
    payload = workspace_production_readiness(repo)
    payload.update(write_workspace_production_site(repo, payload))
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0 if payload['ok'] else 4


def cmd_create_backup(args: argparse.Namespace) -> int:
    repo = _resolve_repo(args.project_root)
    payload = create_workspace_backup(repo, reason=args.reason or 'manual')
    print(json.dumps({'ok': True, **payload}, indent=2, ensure_ascii=False))
    return 0


def cmd_rollback_backup(args: argparse.Namespace) -> int:
    repo = _resolve_repo(args.project_root)
    payload = rollback_workspace_backup(repo, backup_id=args.backup_id or None)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0 if payload.get('ok') else 2


def cmd_observability_status(args: argparse.Namespace) -> int:
    repo = _resolve_repo(args.project_root)
    payload = ObservabilityStore(repo).summarize()
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


def cmd_suite_catalog(args: argparse.Namespace) -> int:
    repo = _resolve_repo(args.project_root)
    payload = suite_catalog_payload(repo)
    write_platform_doc_artifacts(repo, stem='suite_catalog', json_payload=payload, markdown_text=render_suite_catalog_markdown(payload))
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


def cmd_command_reference(args: argparse.Namespace) -> int:
    repo = _resolve_repo(args.project_root)
    payload = command_reference_payload(repo)
    paths = write_platform_doc_artifacts(repo, stem='command_reference', json_payload=payload, markdown_text=render_command_reference_markdown(payload))
    # keep legacy uppercase markdown name for backward compatibility
    from fy_platform.ai.workspace import write_text
    write_text(repo / 'docs' / 'platform' / 'SUITE_COMMAND_REFERENCE.md', render_command_reference_markdown(payload))
    write_text(repo / "'fy'-suites" / 'docs' / 'platform' / 'SUITE_COMMAND_REFERENCE.md', render_command_reference_markdown(payload))
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


def cmd_export_schemas(args: argparse.Namespace) -> int:
    repo = _resolve_repo(args.project_root)
    payload = export_contract_schemas(repo)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


def cmd_doctor(args: argparse.Namespace) -> int:
    repo = _resolve_repo(args.project_root)
    payload = doctor_payload(repo)
    write_platform_doc_artifacts(repo, stem='doctor', json_payload=payload, markdown_text=render_doctor_markdown(payload))
    from fy_platform.ai.workspace import write_text
    write_text(repo / 'docs' / 'platform' / 'DOCTOR.md', render_doctor_markdown(payload))
    write_text(repo / "'fy'-suites" / 'docs' / 'platform' / 'DOCTOR.md', render_doctor_markdown(payload))
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0 if payload.get('ok') else 5


def cmd_final_release_bundle(args: argparse.Namespace) -> int:
    repo = _resolve_repo(args.project_root)
    payload = final_release_bundle(repo)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0 if payload.get('workspace_release', {}).get('ok') else 6

def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Fy platform utilities.')
    sub = parser.add_subparsers(dest='command', required=True)
    p_boot = sub.add_parser('bootstrap', help='Generate fy-manifest.yaml with conservative defaults.')
    p_boot.add_argument('--force', action='store_true', help='Overwrite existing manifest.')
    p_boot.add_argument('--project-root', default='', help='Optional explicit project root path.')
    p_boot.set_defaults(func=cmd_bootstrap)

    p_val = sub.add_parser('validate-manifest', help='Validate fy-manifest.yaml shape minimally.')
    p_val.add_argument('--project-root', default='', help='Optional explicit project root path.')
    p_val.set_defaults(func=cmd_validate)

    p_ws = sub.add_parser('workspace-status', help='Write and print an aggregated workspace status site.')
    p_ws.add_argument('--project-root', default='', help='Optional explicit fy workspace path.')
    p_ws.set_defaults(func=cmd_workspace_status)

    p_rr = sub.add_parser('release-readiness', help='Write and print aggregated release readiness for the fy workspace.')
    p_rr.add_argument('--project-root', default='', help='Optional explicit fy workspace path.')
    p_rr.set_defaults(func=cmd_release_readiness)

    p_pr = sub.add_parser('production-readiness', help='Write and print aggregated production-hardening readiness for the fy workspace.')
    p_pr.add_argument('--project-root', default='', help='Optional explicit fy workspace path.')
    p_pr.set_defaults(func=cmd_production_readiness)

    p_cb = sub.add_parser('create-backup', help='Create a managed backup for workspace state and contracts.')
    p_cb.add_argument('--project-root', default='', help='Optional explicit fy workspace path.')
    p_cb.add_argument('--reason', default='manual', help='Reason to record in the backup manifest.')
    p_cb.set_defaults(func=cmd_create_backup)

    p_rb = sub.add_parser('rollback-backup', help='Restore a managed backup into the fy workspace.')
    p_rb.add_argument('--project-root', default='', help='Optional explicit fy workspace path.')
    p_rb.add_argument('--backup-id', default='', help='Specific backup identifier; defaults to latest.')
    p_rb.set_defaults(func=cmd_rollback_backup)


    p_obs = sub.add_parser('observability-status', help='Print current command/route observability summary.')
    p_obs.add_argument('--project-root', default='', help='Optional explicit fy workspace path.')
    p_obs.set_defaults(func=cmd_observability_status)
    
    p_cat = sub.add_parser('suite-catalog', help='Write and print the full suite catalog for this fy workspace.')
    p_cat.add_argument('--project-root', default='', help='Optional explicit fy workspace path.')
    p_cat.set_defaults(func=cmd_suite_catalog)
    
    p_ref = sub.add_parser('command-reference', help='Write and print the stable suite command reference.')
    p_ref.add_argument('--project-root', default='', help='Optional explicit fy workspace path.')
    p_ref.set_defaults(func=cmd_command_reference)
    
    p_schemas = sub.add_parser('export-schemas', help='Export JSON-schema-style contract files for shared platform payloads.')
    p_schemas.add_argument('--project-root', default='', help='Optional explicit fy workspace path.')
    p_schemas.set_defaults(func=cmd_export_schemas)

    p_ai = sub.add_parser('ai-capability-report', help='Write and print the current AI capability matrix for all suites.')
    p_ai.add_argument('--project-root', default='', help='Optional explicit fy workspace path.')
    p_ai.set_defaults(func=cmd_ai_capability_report)
    
    p_doc = sub.add_parser('doctor', help='Write and print the top-level workspace doctor report.')
    p_doc.add_argument('--project-root', default='', help='Optional explicit fy workspace path.')
    p_doc.set_defaults(func=cmd_doctor)
    
    p_frb = sub.add_parser('final-release-bundle', help='Write and print the full final release bundle for this fy workspace.')
    p_frb.add_argument('--project-root', default='', help='Optional explicit fy workspace path.')
    p_frb.set_defaults(func=cmd_final_release_bundle)
    
    args = parser.parse_args(list(argv) if argv is not None else None)
    return int(args.func(args))



def cmd_ai_capability_report(args: argparse.Namespace) -> int:
    repo = resolve_project_root(args.project_root or '.')
    payload = ai_capability_payload(repo)
    paths = write_platform_doc_artifacts(repo, stem='ai_capability_matrix', json_payload=payload, markdown_text=render_ai_capability_markdown(payload))
    print(json.dumps({'ok': True, **paths}, indent=2, ensure_ascii=False))
    return 0
