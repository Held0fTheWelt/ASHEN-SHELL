from __future__ import annotations

import argparse
import json
from pathlib import Path

from .ai_support import build_ai_context, build_llms_txt
from .memory_bridge import write_memory_snapshot
from .next_steps import rank_next_steps
from .repo_paths import fy_observifyfy_root, resolve_repo_root
from .scanner import scan_workspace, write_json


def _reports_root(repo_root: Path) -> Path:
    return fy_observifyfy_root(repo_root) / 'reports'


def _state_root(repo_root: Path) -> Path:
    return fy_observifyfy_root(repo_root) / 'state'


def run_audit(repo_root: Path) -> dict:
    inventory = scan_workspace(repo_root)
    next_steps = rank_next_steps(inventory)
    ai_context = build_ai_context(inventory, next_steps)
    reports = _reports_root(repo_root)
    state = _state_root(repo_root)
    reports.mkdir(parents=True, exist_ok=True)
    state.mkdir(parents=True, exist_ok=True)
    write_json(reports / 'observifyfy_inventory.json', inventory)
    write_json(reports / 'observifyfy_next_steps.json', next_steps)
    write_json(reports / 'observifyfy_ai_context.json', ai_context)
    (reports / 'llms.txt').write_text(build_llms_txt(ai_context), encoding='utf-8')
    inv_md = ['# Observifyfy Inventory', '', f"- existing suites: {inventory['existing_suite_count']} / {inventory['suite_count']}", '']
    inv_md.append('## Internal roots')
    inv_md.append('')
    for key, value in inventory.get('internal_roots', {}).items():
        inv_md.append(f'- {key}: `{value}`')
    inv_md.extend(['', '## Suites', ''])
    for suite in inventory.get('suites', []):
        if suite.get('exists'):
            inv_md.append(f"- `{suite['name']}` — warnings: {', '.join(suite.get('warnings', [])) or 'none'}, runs: {suite.get('run_count', 0)}, journals: {suite.get('journal_count', 0)}")
    (reports / 'observifyfy_inventory_report.md').write_text('\n'.join(inv_md) + '\n', encoding='utf-8')
    ns_md = ['# Observifyfy Next Steps', '']
    hv = next_steps.get('highest_value_next_step')
    if hv:
        ns_md.append(f"- highest_value_next_step: **{hv['suite']}** — {hv['recommended_action']}")
    ns_md.extend(['', '## Ranked actions', ''])
    for item in next_steps.get('recommended_next_steps', []):
        ns_md.append(f"- P{item['priority']} `{item['suite']}` — {item['recommended_action']}")
    (reports / 'observifyfy_next_steps.md').write_text('\n'.join(ns_md) + '\n', encoding='utf-8')
    ai_md = ['# Observifyfy AI Context', '', ai_context['purpose'], '', '## Managed internal roots', '']
    for key, value in ai_context.get('managed_internal_roots', {}).items():
        ai_md.append(f'- {key}: `{value}`')
    ai_md.extend(['', '## Search hints', ''])
    ai_md.extend(f'- {item}' for item in ai_context.get('search_hints', []))
    (reports / 'observifyfy_ai_context.md').write_text('\n'.join(ai_md) + '\n', encoding='utf-8')
    mem = write_memory_snapshot(state / 'operations_memory.json', inventory, next_steps)
    state_md = ['# Observifyfy State', '', '- status: active', f"- tracked suites: {inventory['existing_suite_count']}", f"- last memory refresh: operations_memory.json", '', '## Managed roots', '']
    for key, value in inventory.get('internal_roots', {}).items():
        state_md.append(f'- {key}: `{value}`')
    (state / 'OBSERVIFYFY_STATE.md').write_text('\n'.join(state_md) + '\n', encoding='utf-8')
    return {'ok': True, 'inventory': inventory, 'next_steps': next_steps, 'ai_context': ai_context, 'memory': mem, 'reports_root': str(reports)}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog='observifyfy')
    sub = parser.add_subparsers(dest='command', required=True)
    for cmd in ('inspect', 'audit', 'ai-pack', 'full'):
        p = sub.add_parser(cmd)
        p.add_argument('--repo-root', default='.')
        p.add_argument('--quiet', action='store_true')
    args = parser.parse_args(argv)
    repo_root = resolve_repo_root(args.repo_root)
    result = run_audit(repo_root)
    if not args.quiet:
        if args.command == 'inspect':
            print(json.dumps(result['inventory'], indent=2, ensure_ascii=False))
        elif args.command == 'ai-pack':
            print(json.dumps(result['ai_context'], indent=2, ensure_ascii=False))
        else:
            print(json.dumps({'ok': True, 'reports_root': result['reports_root'], 'highest_value_next_step': result['next_steps'].get('highest_value_next_step')}, indent=2, ensure_ascii=False))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
