from __future__ import annotations

from typing import Any


def rank_next_steps(inventory: dict[str, Any]) -> dict[str, Any]:
    actions: list[dict[str, Any]] = []
    for suite in inventory.get('suites', []):
        if not suite.get('exists'):
            continue
        warnings = suite.get('warnings', [])
        if 'missing_workflow' in warnings:
            actions.append({
                'suite': suite['name'],
                'priority': 90,
                'reason': 'suite has no dedicated CI workflow',
                'recommended_action': f"Add or repair a workflow for {suite['name']}.",
            })
        if 'missing_state' in warnings:
            actions.append({
                'suite': suite['name'],
                'priority': 80,
                'reason': 'suite has no visible state file',
                'recommended_action': f"Create or refresh tracked state for {suite['name']}.",
            })
        if suite.get('run_count', 0) == 0:
            actions.append({
                'suite': suite['name'],
                'priority': 70,
                'reason': 'suite has no recorded runs',
                'recommended_action': f"Run {suite['name']} at least once and capture evidence.",
            })
    actions.append({
        'suite': 'contractify',
        'priority': 85,
        'reason': "internal ADR root should be actively governed under docs/ADR",
        'recommended_action': "Keep contractify's internal ADR management discoverable through observifyfy and align references to docs/ADR.",
    })
    actions.append({
        'suite': 'mvpify',
        'priority': 88,
        'reason': 'imported MVP docs should remain mirrored under docs/MVPs/imports and tracked through observifyfy',
        'recommended_action': 'Keep mvpify imports normalized and mirrored so temporary implementation folders can be removed safely.',
    })
    actions.append({
        'suite': 'metrify',
        'priority': 84,
        'reason': 'AI usage should remain measured and understandable across suites',
        'recommended_action': 'Keep metrify ledgers and reports fresh so AI spend and value stay visible.',
    })
    actions.append({
        'suite': 'documentify',
        'priority': 85,
        'reason': "internal docs root should be actively governed under docs",
        'recommended_action': "Keep documentify's internal docs management discoverable through observifyfy and align references to docs.",
    })
    actions.sort(key=lambda item: item['priority'], reverse=True)
    return {
        'recommended_next_steps': actions[:12],
        'highest_value_next_step': actions[0] if actions else None,
        'needs_human_decision': [item for item in actions if item['priority'] >= 85],
    }
