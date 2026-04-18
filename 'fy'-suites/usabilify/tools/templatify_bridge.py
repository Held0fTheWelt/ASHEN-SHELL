from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _candidate_report_roots(repo_root: Path) -> list[Path]:
    return [
        repo_root / 'templatify' / 'reports',
        repo_root / "'fy'-suites" / 'templatify' / 'reports',
    ]


def load_templatify_context(repo_root: Path) -> dict[str, Any]:
    payload: dict[str, Any] = {'available': False, 'inventory': {}, 'plan': {}, 'warnings': []}
    reports_root = next((root for root in _candidate_report_roots(repo_root) if root.is_dir()), None)
    if reports_root is None:
        payload['warnings'].append('templatify reports root missing')
        return payload
    inventory_path = reports_root / 'templatify_inventory.json'
    plan_path = reports_root / 'templatify_plan.json'
    if inventory_path.is_file():
        payload['inventory'] = json.loads(inventory_path.read_text(encoding='utf-8'))
        payload['available'] = True
    else:
        payload['warnings'].append('templatify inventory missing')
    if plan_path.is_file():
        payload['plan'] = json.loads(plan_path.read_text(encoding='utf-8'))
        payload['available'] = True
    else:
        payload['warnings'].append('templatify plan missing')
    return payload
