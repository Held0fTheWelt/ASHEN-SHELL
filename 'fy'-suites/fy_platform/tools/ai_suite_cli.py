from __future__ import annotations

import argparse
import json
import time
from typing import Sequence

from contractify.adapter.service import ContractifyAdapter
from testify.adapter.service import TestifyAdapter
from documentify.adapter.service import DocumentifyAdapter
from docify.adapter.service import DocifyAdapter
from despaghettify.adapter.service import DespaghettifyAdapter
from dockerify.adapter.service import DockerifyAdapter
from postmanify.adapter.service import PostmanifyAdapter
from templatify.adapter.service import TemplatifyAdapter
from usabilify.adapter.service import UsabilifyAdapter
from securify.adapter.service import SecurifyAdapter
from observifyfy.adapter.service import ObservifyfyAdapter
from mvpify.adapter.service import MVPifyAdapter
from metrify.adapter.service import MetrifyAdapter
from fy_platform.ai.adapter_cli_helper import build_command_envelope, render_markdown_output, update_status_page
from fy_platform.ai.observability import ObservabilityStore
from fy_platform.ai.graph_recipes import run_audit_recipe, run_context_pack_recipe, run_inspect_recipe, run_triage_recipe

SUITES = {
    'contractify': ContractifyAdapter,
    'testify': TestifyAdapter,
    'documentify': DocumentifyAdapter,
    'docify': DocifyAdapter,
    'despaghettify': DespaghettifyAdapter,
    'dockerify': DockerifyAdapter,
    'postmanify': PostmanifyAdapter,
    'templatify': TemplatifyAdapter,
    'usabilify': UsabilifyAdapter,
    'securify': SecurifyAdapter,
    'observifyfy': ObservifyfyAdapter,
    'mvpify': MVPifyAdapter,
    'metrify': MetrifyAdapter,
}


def _emit(payload: dict, suite: str, command: str, fmt: str) -> None:
    envelope = build_command_envelope(suite, command, payload)
    if fmt == 'markdown':
        print(render_markdown_output(suite, command, payload), end='')
    else:
        print(json.dumps({
            'ok': envelope.ok,
            'suite': envelope.suite,
            'command': envelope.command,
            'schema_version': envelope.schema_version,
            'exit_code': envelope.exit_code,
            'error_code': envelope.error_code,
            'warnings': envelope.warnings,
            'errors': envelope.errors,
            'timestamp': envelope.timestamp,
            'contract_version': envelope.contract_version,
            'compatibility_mode': envelope.compatibility_mode,
            'recovery_hints': envelope.recovery_hints,
            'payload': envelope.payload,
        }, indent=2, ensure_ascii=False))


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Run autark fy suite adapters against an outward target repository.')
    parser.add_argument('suite', choices=sorted(SUITES))
    parser.add_argument('command', choices=['init', 'inspect', 'audit', 'explain', 'prepare-context-pack', 'compare-runs', 'clean', 'reset', 'triage', 'prepare-fix', 'consolidate', 'import', 'legacy-import', 'self-audit', 'release-readiness', 'production-readiness', 'import', 'legacy-import'])
    parser.add_argument('--target-repo', default='')
    parser.add_argument('--query', default='')
    parser.add_argument('--audience', default='developer')
    parser.add_argument('--left-run-id', default='')
    parser.add_argument('--right-run-id', default='')
    parser.add_argument('--mode', default='standard')
    parser.add_argument('--finding-id', action='append', default=[])
    parser.add_argument('--apply-safe', action='store_true')
    parser.add_argument('--instruction', default='')
    parser.add_argument('--bundle', default='')
    parser.add_argument('--format', choices=['json', 'markdown'], default='json')
    parser.add_argument('--strict', action='store_true')
    args = parser.parse_args(list(argv) if argv is not None else None)

    adapter = SUITES[args.suite]()
    metrics = ObservabilityStore(adapter.root)
    started = time.perf_counter()
    try:
        if args.command == 'init':
            out = adapter.init(args.target_repo or None)
        elif args.command == 'inspect':
            recipe = run_inspect_recipe(adapter, args.query or None)
            out = {**recipe.output, 'recipe': recipe.recipe, 'steps': [step.__dict__ for step in recipe.steps]}
        elif args.command == 'audit':
            recipe = run_audit_recipe(adapter, args.target_repo)
            out = {**recipe.output, 'recipe': recipe.recipe, 'steps': [step.__dict__ for step in recipe.steps]}
        elif args.command == 'explain':
            out = adapter.explain(args.audience)
        elif args.command == 'prepare-context-pack':
            recipe = run_context_pack_recipe(adapter, args.query, args.audience)
            out = {**recipe.output, 'recipe': recipe.recipe, 'steps': [step.__dict__ for step in recipe.steps]}
        elif args.command == 'compare-runs':
            out = adapter.compare_runs(args.left_run_id, args.right_run_id)
        elif args.command == 'clean':
            out = adapter.clean(args.mode)
        elif args.command == 'reset':
            out = adapter.reset(args.mode)
        elif args.command == 'triage':
            recipe = run_triage_recipe(adapter, args.query or None)
            out = {**recipe.output, 'recipe': recipe.recipe, 'steps': [step.__dict__ for step in recipe.steps]}
        elif args.command == 'prepare-fix':
            out = adapter.prepare_fix(args.finding_id)
        elif args.command == 'consolidate':
            out = adapter.consolidate(args.target_repo, apply_safe=args.apply_safe, instruction=args.instruction or None)
        elif args.command == 'import':
            out = adapter.import_bundle(args.bundle, legacy=False)
        elif args.command == 'legacy-import':
            out = adapter.import_bundle(args.bundle, legacy=True)
        elif args.command == 'self-audit':
            out = adapter.self_audit()
        elif args.command == 'release-readiness':
            out = adapter.release_readiness()
        elif args.command == 'production-readiness':
            out = adapter.production_readiness()
        else:
            parser.error('unsupported command')
            return 2
    except Exception as exc:
        out = {
            'ok': False,
            'suite': args.suite,
            'reason': 'command_exception',
            'error': str(exc),
            'exception_type': type(exc).__name__,
            'recovery_hints': [
                'Inspect workspace status and production readiness before retrying.',
                'Retry with --format markdown if you need a simpler summary while debugging.',
            ],
        }
    out = update_status_page(adapter, args.command, out)
    _emit(out, args.suite, args.command, args.format)
    envelope = build_command_envelope(args.suite, args.command, out)
    duration_ms = int((time.perf_counter() - started) * 1000)
    metrics.record_command(suite=args.suite, command=args.command, exit_code=envelope.exit_code, duration_ms=duration_ms, ok=envelope.ok, warnings_count=len(envelope.warnings), errors_count=len(envelope.errors), target_repo_id=(out.get('binding') or {}).get('target_repo_id') or out.get('target_repo_id'))
    metrics.record_route(suite=args.suite, command=args.command, route=out.get('route'))
    return envelope.exit_code
