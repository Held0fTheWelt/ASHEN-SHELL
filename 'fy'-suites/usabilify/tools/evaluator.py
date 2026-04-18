from __future__ import annotations

from pathlib import Path
from typing import Any

from usabilify.tools.contract_bridge import scan_contracts
from usabilify.tools.template_inventory import inspect_areas
from usabilify.tools.templatify_bridge import load_templatify_context
from usabilify.tools.usability_rules import RULES


def _area_contracts(contracts: list[dict[str, Any]], area: str) -> list[dict[str, Any]]:
    return [contract for contract in contracts if area in contract['area_tags']]


def _score_view(view: dict[str, Any]) -> tuple[int, list[dict[str, str]]]:
    score = 100
    findings: list[dict[str, str]] = []
    counts = view['element_counts']
    signals = view['signals']
    blocks = set(view['blocks'])
    path = view['path']
    is_base = path == 'base.html'

    if not is_base and counts['forms'] > 0 and counts['labels'] == 0 and not (signals['aria_label'] or signals['aria_labelledby']):
        score -= 20
        findings.append({'severity': 'warn', 'message': 'Form surface has inputs/forms but no labels or aria naming signals.'})
    if not is_base and counts['headings'] == 0 and 'title' not in blocks:
        score -= 10
        findings.append({'severity': 'warn', 'message': 'View has neither explicit heading tags nor a title block override.'})
    if not is_base and counts['buttons'] + counts['links'] == 0 and counts['forms'] == 0:
        score -= 5
        findings.append({'severity': 'info', 'message': 'View has no obvious interactive affordances; verify this is intentional.'})
    if is_base and counts['mains'] == 0:
        score -= 15
        findings.append({'severity': 'warn', 'message': 'Base template does not expose a <main> landmark.'})
    if is_base and counts['navs'] == 0:
        score -= 10
        findings.append({'severity': 'info', 'message': 'Base template does not expose a <nav> landmark.'})
    if counts['forms'] > 0 and not (signals['role_alert'] or signals['role_status'] or signals['aria_live'] or signals['flash_message']):
        score -= 10
        findings.append({'severity': 'info', 'message': 'Interactive surface lacks visible status/error signaling patterns.'})
    if counts['forms'] + counts['buttons'] + counts['links'] > 0 and not (signals['aria_label'] or signals['aria_labelledby'] or counts['labels'] > 0):
        score -= 8
        findings.append({'severity': 'info', 'message': 'Interactive elements exist but accessible naming signals are sparse.'})

    return max(score, 0), findings


def evaluate(repo_root: Path) -> dict[str, Any]:
    inventory = inspect_areas(repo_root)
    contract_payload = scan_contracts(repo_root)
    templatify = load_templatify_context(repo_root)
    contracts = contract_payload['contracts']
    views = inventory['views']
    area_results: dict[str, Any] = {}
    view_results: list[dict[str, Any]] = []

    for view in views:
        score, findings = _score_view(view)
        view_results.append(
            {
                'area': view['area'],
                'path': view['path'],
                'score': score,
                'findings': findings,
                'element_counts': view['element_counts'],
                'signals': view['signals'],
            }
        )

    for area, area_info in inventory['areas'].items():
        relevant_contracts = _area_contracts(contracts, area)
        area_views = [view for view in view_results if view['area'] == area]
        base = next((view for view in area_views if view['path'] == area_info['base_template']), None)
        warnings: list[str] = []
        if area_info['exists'] and not relevant_contracts:
            warnings.append('No directly mapped UI contract/guidance files found for this area.')
        avg_score = round(sum(view['score'] for view in area_views) / max(len(area_views), 1), 1)
        plan_info = templatify.get('plan', {}).get('areas', {}).get(area, {}) if templatify.get('plan') else {}
        if plan_info.get('unmapped_base_blocks'):
            warnings.append('Templatify reports unmapped base blocks: ' + ', '.join(plan_info['unmapped_base_blocks']))
        if base and base['signals'].get('skip_link'):
            warnings.append('Skip-link pattern already visible in base surface.')
        area_results[area] = {
            'target_root': area_info['target_root'],
            'template_count': area_info['template_count'],
            'average_score': avg_score,
            'contracts': [
                {'path': item['path'], 'title': item['title'], 'requirement_count': item['requirement_count']}
                for item in relevant_contracts
            ],
            'templatify': {
                'available': templatify['available'],
                'base_blocks': templatify.get('inventory', {}).get('areas', {}).get(area, {}).get('base_blocks', []),
                'unmapped_base_blocks': plan_info.get('unmapped_base_blocks', []),
            },
            'warnings': warnings,
            'priority_views': sorted(area_views, key=lambda item: item['score'])[:5],
        }

    return {
        'suite': 'usabilify',
        'rules': RULES,
        'inventory': inventory,
        'contracts': contract_payload,
        'templatify': templatify,
        'areas': area_results,
        'views': view_results,
    }


def inventory_markdown(payload: dict[str, Any]) -> str:
    lines = ['# Usabilify inventory report', '']
    for area, info in payload['areas'].items():
        lines.append(f'## {area}')
        lines.append('')
        for key in ['target_root', 'template_count', 'view_count', 'base_template']:
            lines.append(f'- {key}: `{info[key]}`')
        lines.append(f"- base_blocks: `{', '.join(info['base_blocks'])}`")
        lines.append('')
    return '\n'.join(lines).rstrip() + '\n'


def evaluation_markdown(payload: dict[str, Any]) -> str:
    lines = ['# Usabilify evaluation report', '']
    for area, info in payload['areas'].items():
        lines.append(f'## {area}')
        lines.append('')
        lines.append(f"- target_root: `{info['target_root']}`")
        lines.append(f"- template_count: `{info['template_count']}`")
        lines.append(f"- average_score: `{info['average_score']}`")
        contract_paths = ', '.join(item['path'] for item in info['contracts']) or 'none'
        lines.append(f'- contracts: `{contract_paths}`')
        if info['templatify']['available']:
            lines.append(f"- templatify base blocks: `{', '.join(info['templatify']['base_blocks'])}`")
            lines.append(f"- templatify unmapped base blocks: `{', '.join(info['templatify']['unmapped_base_blocks'])}`")
        if info['warnings']:
            lines.append('- warnings:')
            for warning in info['warnings']:
                lines.append(f'  - {warning}')
        lines.append('- priority views:')
        for view in info['priority_views']:
            lines.append(f"  - `{view['path']}` score `{view['score']}`")
            for finding in view['findings'][:3]:
                lines.append(f"    - {finding['severity']}: {finding['message']}")
        lines.append('')
    return '\n'.join(lines).rstrip() + '\n'


def view_map(payload: dict[str, Any]) -> str:
    lines = ['graph TD']
    for area, info in payload['areas'].items():
        area_node = area.replace('-', '_')
        lines.append(f'  {area_node}["{area}"]')
        for view in info['priority_views']:
            view_id = (area_node + '_' + view['path'].replace('/', '_').replace('.', '_')).replace('-', '_')
            label = f"{view['path']} ({view['score']})"
            lines.append(f'  {area_node} --> {view_id}["{label}"]')
    return '\n'.join(lines) + '\n'
