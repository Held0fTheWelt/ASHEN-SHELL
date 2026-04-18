from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fy_platform.ai.evidence_registry.registry import EvidenceRegistry
from fy_platform.ai.workspace import workspace_root

RELATED_SUITES = {
    'contractify': ['testify', 'documentify', 'docify', 'templatify', 'usabilify', 'securify'],
    'testify': ['contractify', 'documentify', 'docify', 'despaghettify', 'securify'],
    'documentify': ['docify', 'templatify', 'usabilify', 'contractify', 'securify'],
    'docify': ['documentify', 'contractify', 'despaghettify', 'securify'],
    'despaghettify': ['docify', 'testify', 'documentify', 'securify'],
    'templatify': ['documentify', 'usabilify', 'contractify', 'securify'],
    'usabilify': ['templatify', 'documentify', 'contractify', 'securify'],
    'securify': ['contractify', 'testify', 'documentify', 'docify', 'usabilify', 'observifyfy', 'metrify'],
    'observifyfy': ['contractify', 'documentify', 'testify', 'docify', 'templatify', 'usabilify', 'securify', 'mvpify', 'metrify'],
    'mvpify': ['contractify', 'despaghettify', 'testify', 'documentify', 'templatify', 'usabilify', 'securify', 'observifyfy', 'metrify'],
    'metrify': ['observifyfy', 'contractify', 'testify', 'documentify', 'docify', 'mvpify'],
}


def _status_json_path(root: Path, suite: str) -> Path:
    return root / suite / 'reports' / 'status' / 'most_recent_next_steps.json'


def _load_status(root: Path, suite: str) -> dict[str, Any] | None:
    path = _status_json_path(root, suite)
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return None


def _suite_matches_query(suite: str, query: str) -> bool:
    query_l = (query or '').lower()
    return bool(query_l and suite.lower() in query_l)


def collect_cross_suite_signals(root: Path, suite: str, query: str | None = None, limit: int = 5) -> dict[str, Any]:
    root = workspace_root(root)
    registry = EvidenceRegistry(root)
    related = RELATED_SUITES.get(suite, [])
    rows: list[dict[str, Any]] = []
    for rel in related:
        latest = registry.latest_run(rel)
        status = _load_status(root, rel)
        if not latest and not status:
            continue
        score = 0
        if latest and latest.get('status') == 'ok':
            score += 2
        if status and status.get('ok'):
            score += 2
        if _suite_matches_query(rel, query or ''):
            score += 3
        if status and status.get('next_steps'):
            score += 1
        rows.append({
            'suite': rel,
            'score': score,
            'latest_run': latest,
            'status_summary': (status or {}).get('summary', ''),
            'next_steps': list((status or {}).get('next_steps', []))[:3],
            'status_ok': bool((status or {}).get('ok', False)),
            'relation_reason': f'{suite}_related_signal',
        })
    rows.sort(key=lambda item: (item['score'], item['suite']), reverse=True)
    top = rows[:limit]
    return {
        'suite': suite,
        'related_suites': related,
        'signal_count': len(top),
        'signals': top,
        'summary': _render_summary(suite, top),
    }


def _render_summary(suite: str, signals: list[dict[str, Any]]) -> str:
    if not signals:
        return f'No recent cross-suite signals are available for {suite}.'
    top = signals[0]
    return f'The strongest cross-suite signal for {suite} currently comes from {top["suite"]}. Use it to connect the latest result with nearby suite work instead of treating the suite in isolation.'
