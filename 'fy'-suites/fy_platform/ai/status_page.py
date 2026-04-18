from __future__ import annotations

from pathlib import Path

from fy_platform.ai.decision_policy import DECISION_LANES
from fy_platform.ai.workspace import write_json, write_text


def _simple_governance_lines(governance: dict[str, any] | None) -> list[str]:
    if not governance:
        return []
    failures = governance.get('failures', []) or []
    warnings = governance.get('warnings', []) or []
    lines = ['## Governance', '']
    if failures:
        lines.append('There are still governance problems inside the suite workspace.')
        lines.append('')
        lines.extend(f'- {item}' for item in failures)
        lines.append('')
    elif warnings:
        lines.append('The suite is usable, but there are warnings you should look at soon.')
        lines.append('')
        lines.extend(f'- {item}' for item in warnings)
        lines.append('')
    else:
        lines.append('The suite workspace currently looks healthy.')
        lines.append('')
    return lines


def _decision_summary(payload: dict[str, any]) -> tuple[str, list[str]]:
    decision = payload.get('decision') or {}
    lane = str(decision.get('lane', '') or '')
    if not lane:
        return '', []
    lines = [f"Decision lane: `{lane}`", DECISION_LANES.get(lane, '')]
    if decision.get('recommended_action'):
        lines.append(str(decision['recommended_action']))
    uncertainty = list(decision.get('uncertainty_flags', []))
    return '\n\n'.join(item for item in lines if item), uncertainty


def _derive_next_steps(suite: str, command: str, payload: dict[str, any]) -> list[str]:
    steps: list[str] = []
    reason = str(payload.get('reason', '') or payload.get('error_code', '') or '')
    decision = payload.get('decision') or {}
    lane = str(decision.get('lane', '') or '')
    if payload.get('ok') is False:
        if reason.startswith('governance_gate_failed'):
            steps.append('Repair the missing governance files or rules shown below before running the suite again.')
        elif reason == 'target_repo_not_found':
            steps.append('Check the target repository path and run the command again.')
        elif reason == 'no_runs':
            steps.append('Run an audit first so the suite has a real result to explain.')
        elif reason == 'consolidate_not_supported':
            steps.append('Use a suite that supports consolidate, or run a normal audit first.')
        else:
            steps.append('Read the error details and rerun the command after the blocking issue is fixed.')
    else:
        if lane == 'abstain':
            steps.append('Do not act automatically. Collect more evidence first.')
        elif lane == 'user_input_required':
            steps.append('Provide the missing instruction or mapping before any outward change is applied.')
        elif lane == 'ambiguous':
            steps.append('Review the top candidate options manually. The system found more than one plausible path.')
        elif lane == 'likely_but_review':
            steps.append('The likely next move is visible, but it still needs human review before outward use.')
        elif lane == 'safe_to_apply':
            steps.append('The strongest evidence looks safe enough for automatic application in this narrow case.')
        if payload.get('finding_count', 0):
            steps.append(f"Review the {payload.get('finding_count')} finding(s) and decide which one should be fixed first.")
        if payload.get('drift_count', 0):
            steps.append(f"Inspect the {payload.get('drift_count')} drift item(s) before applying generated outputs.")
        if payload.get('local_spike_count', 0):
            steps.append('Open the local spike workstream first, even if the global category still looks low.')
        unmapped = payload.get('unmapped_adr_ids') or payload.get('adr_reflection', {}).get('unmapped_adr_ids', [])
        if unmapped:
            steps.append('Add or update explicit ADR-to-test mappings for the missing ADR ids.')
        weak = payload.get('weakly_mapped_adr_ids') or payload.get('adr_reflection', {}).get('weakly_mapped_adr_ids', [])
        if weak:
            steps.append('Strengthen weak ADR reflection so the test intent is easier to understand.')
        if payload.get('doc_count', 0):
            steps.append('Read the newly generated documentation and decide which tracks should be exported outward.')
        if payload.get('template_count', 0):
            steps.append('Validate the generated template previews before applying them to a target repo.')
        if payload.get('generated_dir'):
            steps.append('Open the generated output directory and review the new files in simple language first.')
        if payload.get('summary') and command in {'inspect', 'explain'}:
            steps.append('Read the summary first, then open the linked artifacts only where you still need detail.')
        cross = payload.get('cross_suite') or {}
        if cross.get('signal_count'):
            steps.append('Use the strongest cross-suite signal as a second opinion before acting in isolation.')
        if not steps:
            steps.append('No urgent problem is visible right now. Review the latest artifacts and continue with the next planned workflow.')
    return steps[:8]


def build_status_payload(*, suite: str, command: str, payload: dict[str, any], latest_run: dict[str, any] | None, governance: dict[str, any] | None) -> dict[str, any]:
    decision_text, uncertainty = _decision_summary(payload)
    return {
        'suite': suite,
        'command': command,
        'ok': bool(payload.get('ok', False)),
        'latest_run': latest_run,
        'summary': payload.get('summary', ''),
        'decision': payload.get('decision', {}),
        'decision_summary': decision_text,
        'next_steps': _derive_next_steps(suite, command, payload),
        'warnings': list(payload.get('warnings', [])),
        'governance': governance or {},
        'cross_suite': payload.get('cross_suite', {}),
        'key_signals': {
            'finding_count': payload.get('finding_count', 0),
            'doc_count': payload.get('doc_count', 0),
            'track_count': payload.get('track_count', 0),
            'template_count': payload.get('template_count', 0),
            'drift_count': payload.get('drift_count', payload.get('drift', {}).get('drift_count', 0) if isinstance(payload.get('drift'), dict) else 0),
            'local_spike_count': payload.get('local_spike_count', 0),
            'evidence_confidence': payload.get('evidence_confidence', ''),
            'signal_count': payload.get('cross_suite', {}).get('signal_count', 0),
        },
        'uncertainty': list(payload.get('uncertainty', [])) + uncertainty,
    }


def render_status_markdown(status: dict[str, any]) -> str:
    latest = status.get('latest_run') or {}
    lines = [
        f"# {status['suite']} — Most-Recent-Next-Steps",
        '',
        'This page uses simple language. It should help you understand the latest result and what to do next.',
        '',
        '## Current status',
        '',
        f"- suite: `{status['suite']}`",
        f"- command: `{status['command']}`",
        f"- ok: `{str(status['ok']).lower()}`",
        f"- latest_run_id: `{latest.get('run_id', 'none')}`",
        f"- latest_run_mode: `{latest.get('mode', 'none')}`",
        f"- latest_run_status: `{latest.get('status', 'none')}`",
        '',
    ]
    if status.get('summary'):
        lines.extend(['## Plain summary', '', str(status['summary']), ''])
    if status.get('decision_summary'):
        lines.extend(['## Decision guidance', '', str(status['decision_summary']), ''])
    lines.extend(['## Most-Recent-Next-Steps', ''])
    lines.extend(f'- {item}' for item in status.get('next_steps', []))
    lines.append('')
    lines.extend(['## Key signals', ''])
    for key, value in (status.get('key_signals') or {}).items():
        lines.append(f'- {key}: `{value}`')
    lines.append('')
    if status.get('uncertainty'):
        lines.extend(['## Uncertainty', ''])
        lines.extend(f'- {item}' for item in status['uncertainty'])
        lines.append('')
    cross = status.get('cross_suite') or {}
    if cross.get('signals'):
        lines.extend(['## Cross-suite signals', ''])
        for signal in cross['signals']:
            lines.append(f"- `{signal['suite']}`: {signal.get('status_summary') or 'No summary available.'}")
            for step in signal.get('next_steps', [])[:2]:
                lines.append(f'  - next: {step}')
        lines.append('')
    lines.extend(_simple_governance_lines(status.get('governance')))
    warnings = status.get('warnings', []) or []
    if warnings:
        lines.extend(['## Warnings', ''])
        lines.extend(f'- {item}' for item in warnings)
        lines.append('')
    return '\n'.join(lines).strip() + '\n'


def write_status_page(workspace_root: Path, suite: str, status: dict[str, any]) -> dict[str, str]:
    base = workspace_root / suite / 'reports' / 'status'
    base.mkdir(parents=True, exist_ok=True)
    json_path = base / 'most_recent_next_steps.json'
    md_path = base / 'MOST_RECENT_NEXT_STEPS.md'
    write_json(json_path, status)
    write_text(md_path, render_status_markdown(status))
    return {
        'status_json_path': str(json_path.relative_to(workspace_root)),
        'status_md_path': str(md_path.relative_to(workspace_root)),
    }
