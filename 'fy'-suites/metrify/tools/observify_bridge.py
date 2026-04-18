from __future__ import annotations

from pathlib import Path
from typing import Any

from fy_platform.ai.workspace import write_json

from .repo_paths import fy_suite_dir


def write_observify_summary(repo_root: Path, summary: dict[str, Any]) -> dict[str, str]:
    payload = {
        'suite': 'metrify',
        'metric_kind': 'ai_cost_observability',
        'total_cost_usd': summary.get('total_cost_usd', 0.0),
        'today_cost_usd': summary.get('today_cost_usd', 0.0),
        'last_10_runs_cost_usd': summary.get('last_10_runs_cost_usd', 0.0),
        'top_models': summary.get('top_models', [])[:3],
        'top_suites': summary.get('top_suites', [])[:3],
        'optimization_suggestions': summary.get('optimization_suggestions', [])[:5],
    }
    out = repo_root / '.fydata' / 'bindings' / 'metrify.json'
    write_json(out, payload)
    obs = repo_root / "'fy'-suites" / 'observifyfy' / 'reports' / 'observifyfy_metrify_summary.json'
    write_json(obs, payload)
    fyobs = fy_suite_dir(repo_root) / 'reports' / 'metrify_observify_summary.json'
    write_json(fyobs, payload)
    return {
        'binding_json': str(out.relative_to(repo_root)),
        'observify_summary_json': str(obs.relative_to(repo_root)),
    }
