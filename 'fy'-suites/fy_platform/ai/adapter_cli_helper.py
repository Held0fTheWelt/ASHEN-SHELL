from __future__ import annotations

import argparse
import json
from typing import Sequence

from fy_platform.ai.contracts import COMMAND_ENVELOPE_SCHEMA_VERSION
from fy_platform.ai.schemas.common import CommandEnvelope
from fy_platform.ai.status_page import build_status_payload, write_status_page
from fy_platform.ai.workspace import utc_now


def classify_error(payload: dict) -> tuple[str, int]:
    if payload.get('ok', False):
        return '', 0
    reason = payload.get('reason', '')
    if reason.startswith('governance_gate_failed'):
        return 'governance_gate_failed', 3
    if reason in {'target_repo_not_found', 'run_not_found', 'evidence_not_found', 'no_runs'}:
        return reason, 1
    if reason in {'consolidate_not_supported', 'import_not_supported'}:
        return reason, 4
    if reason == 'command_exception':
        return reason, 5
    return 'command_failed', 1


def build_command_envelope(suite: str, command: str, payload: dict) -> CommandEnvelope:
    warnings = list(payload.get('warnings', []))
    errors: list[str] = []
    if payload.get('ok') is False:
        if payload.get('reason'):
            errors.append(str(payload['reason']))
        elif payload.get('error'):
            errors.append(str(payload['error']))
    recovery_hints = list(payload.get('recovery_hints', []))
    error_code, exit_code = classify_error(payload)
    return CommandEnvelope(
        ok=bool(payload.get('ok', False)),
        suite=suite,
        command=command,
        payload=payload,
        warnings=warnings,
        errors=errors,
        recovery_hints=recovery_hints,
        error_code=error_code,
        exit_code=exit_code,
        timestamp=utc_now(),
        schema_version=COMMAND_ENVELOPE_SCHEMA_VERSION,
        contract_version='1.0',
        compatibility_mode='autark-outbound',
    )


def render_markdown_output(suite: str, command: str, payload: dict) -> str:
    envelope = build_command_envelope(suite, command, payload)
    lines = [f'# {suite}::{command}', '', f'- ok: `{str(envelope.ok).lower()}`', f'- schema_version: `{envelope.schema_version}`', f'- contract_version: `{envelope.contract_version}`', f'- compatibility_mode: `{envelope.compatibility_mode}`', f'- exit_code: `{envelope.exit_code}`']
    if envelope.error_code:
        lines.append(f'- error_code: `{envelope.error_code}`')
    if envelope.warnings:
        lines.append(f'- warnings: {len(envelope.warnings)} item(s)')
    inner = envelope.payload
    for key, value in inner.items():
        if key in {'ok', 'suite', 'warnings'}:
            continue
        if isinstance(value, (str, int, float, bool)) or value is None:
            lines.append(f'- {key}: `{value}`')
        elif isinstance(value, list):
            lines.append(f'- {key}: {len(value)} item(s)')
        elif isinstance(value, dict):
            lines.append(f'- {key}: {json.dumps(value, ensure_ascii=False)[:200]}')
    if envelope.errors:
        lines.extend(['', '## errors', ''])
        lines.extend(f'- `{item}`' for item in envelope.errors)
    if envelope.recovery_hints:
        lines.extend(['', '## recovery_hints', ''])
        lines.extend(f'- {item}' for item in envelope.recovery_hints)
    return '\n'.join(lines) + '\n'


def update_status_page(adapter, command: str, payload: dict) -> dict:
    governance = payload.get('governance')
    latest = adapter.registry.latest_run(adapter.suite)
    status = build_status_payload(suite=adapter.suite, command=command, payload=payload, latest_run=latest, governance=governance)
    payload.update(write_status_page(adapter.root, adapter.suite, status))
    return payload


def run_adapter_cli(adapter_cls, argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Run a single fy suite adapter directly.')
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
    args = parser.parse_args(list(argv) if argv is not None else None)

    adapter = adapter_cls()
    cmd = args.command
    if cmd == 'init':
        out = adapter.init(args.target_repo or None)
    elif cmd == 'inspect':
        out = adapter.inspect(args.query or None)
    elif cmd == 'audit':
        out = adapter.audit(args.target_repo)
    elif cmd == 'explain':
        out = adapter.explain(args.audience)
    elif cmd == 'prepare-context-pack':
        out = adapter.prepare_context_pack(args.query, args.audience)
    elif cmd == 'compare-runs':
        out = adapter.compare_runs(args.left_run_id, args.right_run_id)
    elif cmd == 'clean':
        out = adapter.clean(args.mode)
    elif cmd == 'reset':
        out = adapter.reset(args.mode)
    elif cmd == 'triage':
        out = adapter.triage(args.query or None)
    elif cmd == 'prepare-fix':
        out = adapter.prepare_fix(args.finding_id)
    elif cmd == 'consolidate':
        out = adapter.consolidate(args.target_repo, apply_safe=args.apply_safe, instruction=args.instruction or None)
    elif cmd == 'import':
        out = adapter.import_bundle(args.bundle, legacy=False)
    elif cmd == 'legacy-import':
        out = adapter.import_bundle(args.bundle, legacy=True)
    elif cmd == 'self-audit':
        out = adapter.self_audit()
    elif cmd == 'release-readiness':
        out = adapter.release_readiness()
    elif cmd == 'production-readiness':
        out = adapter.production_readiness()
    else:
        raise SystemExit(2)
    out = update_status_page(adapter, cmd, out)
    if args.format == 'markdown':
        print(render_markdown_output(adapter.suite, cmd, out), end='')
    else:
        env = build_command_envelope(adapter.suite, cmd, out)
        print(json.dumps({
            'ok': env.ok,
            'suite': env.suite,
            'command': env.command,
            'schema_version': env.schema_version,
            'exit_code': env.exit_code,
            'error_code': env.error_code,
            'warnings': env.warnings,
            'errors': env.errors,
            'timestamp': env.timestamp,
            'contract_version': env.contract_version,
            'compatibility_mode': env.compatibility_mode,
            'recovery_hints': env.recovery_hints,
            'payload': env.payload,
        }, indent=2, ensure_ascii=False))
    return build_command_envelope(adapter.suite, cmd, out).exit_code
