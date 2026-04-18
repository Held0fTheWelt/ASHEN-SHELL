from __future__ import annotations

from pathlib import Path
from typing import Any

from fy_platform.ai.workspace import write_json

from .repo_paths import fy_suite_dir, suite_dir


def write_ai_pack(repo_root: Path, summary: dict[str, Any]) -> dict[str, str]:
    payload = {
        'kind': 'ai_cost_context',
        'summary': {
            'total_cost_usd': summary.get('total_cost_usd', 0.0),
            'today_cost_usd': summary.get('today_cost_usd', 0.0),
            'last_10_runs_cost_usd': summary.get('last_10_runs_cost_usd', 0.0),
            'top_models': summary.get('top_models', [])[:5],
            'top_suites': summary.get('top_suites', [])[:5],
            'optimization_suggestions': summary.get('optimization_suggestions', [])[:5],
        },
        'recommended_usage': [
            'Use this pack before selecting a model for a new suite wave.',
            'Compare intended model choice against the current top cost drivers.',
            'Record utility_score where possible so future runs can measure cost versus value.',
        ],
    }
    hints = '\n'.join(f'- {item}' for item in summary.get('optimization_suggestions', [])[:5])
    md = (
        '# Metrify AI Context\n\n'
        f"- Total cost (USD): {summary.get('total_cost_usd', 0.0)}\n"
        f"- Today cost (USD): {summary.get('today_cost_usd', 0.0)}\n"
        f"- Last 10 runs cost (USD): {summary.get('last_10_runs_cost_usd', 0.0)}\n\n"
        '## Optimization hints\n' + hints + '\n'
    )
    out1 = suite_dir(repo_root) / 'reports' / 'metrify_ai_context.json'
    out2 = suite_dir(repo_root) / 'reports' / 'metrify_ai_context.md'
    llms = suite_dir(repo_root) / 'reports' / 'llms.txt'
    write_json(out1, payload)
    out2.parent.mkdir(parents=True, exist_ok=True)
    out2.write_text(md, encoding='utf-8')
    llms.write_text(
        'Metrify AI context\n\n'
        '- Start with reports/metrify_cost_report.md\n'
        '- Then inspect reports/metrify_ai_context.md\n'
        '- Use state/latest_summary.json for machine-readable totals and top drivers\n',
        encoding='utf-8',
    )
    fyout1 = fy_suite_dir(repo_root) / 'reports' / 'metrify_ai_context.json'
    fyout2 = fy_suite_dir(repo_root) / 'reports' / 'metrify_ai_context.md'
    fyllms = fy_suite_dir(repo_root) / 'reports' / 'llms.txt'
    write_json(fyout1, payload)
    fyout2.parent.mkdir(parents=True, exist_ok=True)
    fyout2.write_text(md, encoding='utf-8')
    fyllms.write_text(llms.read_text(encoding='utf-8'), encoding='utf-8')
    return {
        'ai_context_json': str(out1.relative_to(repo_root)),
        'ai_context_md': str(out2.relative_to(repo_root)),
        'llms_txt': str(llms.relative_to(repo_root)),
    }
