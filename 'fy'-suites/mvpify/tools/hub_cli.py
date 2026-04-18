from __future__ import annotations

import argparse
import json
from pathlib import Path

from .ai_support import build_ai_context, build_llms_txt
from .importer import materialize_import
from .memory_bridge import write_memory_snapshot
from .observifyfy_bridge import load_observifyfy_signal
from .planner import build_plan
from .repo_paths import reports_root, resolve_repo_root, state_root
from .task_writer import build_audit_task, build_implementation_task


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding='utf-8')


def _inventory_md(payload: dict) -> str:
    inventory = payload.get('inventory', payload)
    lines = [
        '# MVPify import inventory',
        '',
        f"- source: `{payload.get('source')}`",
        f"- source_mode: `{payload.get('source_mode')}`",
        f"- artifact_count: {payload.get('artifact_count', 0)}",
        f"- mirrored_docs_root: `{payload.get('mirrored_docs_root', '')}`",
        '',
        '## Counters',
        '',
    ]
    for key, value in sorted(inventory.get('counters', {}).items()):
        lines.append(f'- {key}: {value}')
    lines.extend(['', '## Detected suites in imported MVP', ''])
    for item in inventory.get('suite_signals', []):
        if item.get('present'):
            lines.append(f"- `{item['name']}` — {', '.join(item.get('evidence', [])[:3])}")
    lines.append('')
    return "\n".join(lines)


def _plan_md(plan: dict) -> str:
    lines = ['# MVPify orchestration plan', '']
    hv = plan.get('highest_value_next_step') or {}
    if hv:
        lines.append(f"- highest_value_next_step: **{hv.get('suite', 'mvpify')}** / `{hv.get('phase', '')}`")
        lines.append('')
    for idx, step in enumerate(plan.get('steps', []), 1):
        lines.extend([
            f"## {idx}. {step['phase']} / {step['suite']}",
            '',
            step['objective'],
            '',
            f"Why now: {step['why_now']}",
            '',
        ])
    return "\n".join(lines) + "\n"


def run(repo_root: Path, *, source_root: str = '', mvp_zip: str = '') -> dict:
    imported = materialize_import(repo_root=repo_root, source_root=source_root, mvp_zip=mvp_zip)
    import_payload = imported['inventory']
    plan = build_plan(import_payload, str(repo_root))
    ai_context = build_ai_context(imported, plan)
    obs = load_observifyfy_signal(repo_root)
    if obs.get('present') and plan.get('highest_value_next_step'):
        ai_context['observifyfy_signal'] = obs
    reports = reports_root(repo_root)
    state = state_root(repo_root)
    reports.mkdir(parents=True, exist_ok=True)
    state.mkdir(parents=True, exist_ok=True)
    _write_json(reports / 'mvpify_import_inventory.json', imported)
    (reports / 'mvpify_import_inventory.md').write_text(_inventory_md(imported), encoding='utf-8')
    _write_json(reports / 'mvpify_orchestration_plan.json', plan)
    (reports / 'mvpify_orchestration_plan.md').write_text(_plan_md(plan), encoding='utf-8')
    _write_json(reports / 'mvpify_ai_context.json', ai_context)
    (reports / 'mvpify_ai_context.md').write_text('# MVPify AI context\n\n' + ai_context['purpose'] + '\n', encoding='utf-8')
    (reports / 'llms.txt').write_text(build_llms_txt(ai_context), encoding='utf-8')
    (reports / 'mvpify_audit_task.md').write_text(build_audit_task(imported, plan), encoding='utf-8')
    (reports / 'mvpify_implementation_task.md').write_text(build_implementation_task(imported, plan), encoding='utf-8')
    mem = write_memory_snapshot(state / 'operations_memory.json', imported, plan)
    (state / 'MVPIFY_STATE.md').write_text(
        '\n'.join(
            [
                '# MVPify State',
                '',
                '- status: active',
                f"- import_source: `{imported.get('source')}`",
                f"- artifact_count: {imported.get('artifact_count', 0)}",
                f"- mirrored_docs_root: `{imported.get('mirrored_docs_root', '')}`",
                f"- highest_value_next_step: `{(plan.get('highest_value_next_step') or {}).get('suite', 'mvpify')}`",
                '',
            ]
        ),
        encoding='utf-8',
    )
    return {
        'ok': True,
        'import_inventory': imported,
        'plan': plan,
        'ai_context': ai_context,
        'memory': mem,
        'reports_root': str(reports),
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog='mvpify', description='Prepared MVP import and orchestration for fy suites')
    sub = parser.add_subparsers(dest='command', required=True)
    for cmd in ('inspect', 'plan', 'ai-pack', 'full'):
        p = sub.add_parser(cmd)
        p.add_argument('--repo-root', default='.')
        p.add_argument('--source-root', default='')
        p.add_argument('--mvp-zip', default='')
        p.add_argument('--quiet', action='store_true')
    args = parser.parse_args(argv)
    repo_root = resolve_repo_root(args.repo_root)
    result = run(repo_root, source_root=args.source_root, mvp_zip=args.mvp_zip)
    if not args.quiet:
        if args.command == 'inspect':
            print(json.dumps(result['import_inventory'], indent=2, ensure_ascii=False))
        elif args.command == 'plan':
            print(json.dumps(result['plan'], indent=2, ensure_ascii=False))
        elif args.command == 'ai-pack':
            print(json.dumps(result['ai_context'], indent=2, ensure_ascii=False))
        else:
            print(json.dumps({'ok': True, 'reports_root': result['reports_root'], 'highest_value_next_step': result['plan'].get('highest_value_next_step')}, indent=2, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
