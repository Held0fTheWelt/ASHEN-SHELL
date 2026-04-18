from __future__ import annotations

from typing import Any


def build_ai_context(inventory: dict[str, Any], next_steps: dict[str, Any]) -> dict[str, Any]:
    suites = inventory.get('suites', [])
    focus = [
        {
            'suite': item['name'],
            'warnings': item.get('warnings', []),
            'run_count': item.get('run_count', 0),
            'journal_count': item.get('journal_count', 0),
        }
        for item in suites if item.get('exists')
    ]
    return {
        'purpose': 'AI-readable cross-suite operational context for fy-suite self-management.',
        'managed_internal_roots': inventory.get('internal_roots', {}),
        'suite_focus': focus,
        'next_steps': next_steps.get('recommended_next_steps', []),
        'search_hints': [
            'suite health',
            'freshness',
            'cross-suite conflicts',
            'contractify internal ADR management',
            'documentify internal docs management',
            'status pages',
            'run journals',
            'mvpify imported MVP mirroring',
            'metrify cost and usage summaries',
        ],
        'memory_contract': {
            'store': 'observifyfy tracks suite operations memory, not project-facing truth',
            'refresh_rule': 'prefer latest run evidence and internal docs over stale summaries',
            'guardrails': ['do_not_overwrite_project_truth', 'do_not_flatten_contractify_or_testify_findings'],
        },
    }


def build_llms_txt(ai_context: dict[str, Any]) -> str:
    roots = ai_context.get('managed_internal_roots', {})
    lines = [
        '# observifyfy AI context',
        '',
        'Use these internal fy roots first when reasoning about suite-family operations:',
    ]
    for key, value in roots.items():
        lines.append(f'- {key}: `{value}`')
    lines.extend([
        '',
        'Rules:',
        '- Treat observifyfy as internal suite-operations truth only.',
        '- Do not overwrite project-facing truth from specialist suites.',
        '- Prefer latest evidence, state, journals, and status outputs.',
    ])
    return '\n'.join(lines) + '\n'
