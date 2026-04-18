from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def write_memory_snapshot(path: Path, inventory: dict[str, Any], next_steps: dict[str, Any]) -> dict[str, Any]:
    payload = {
        'memory_kind': 'fy_suite_operations',
        'suite_count': inventory.get('suite_count', 0),
        'existing_suite_count': inventory.get('existing_suite_count', 0),
        'internal_roots': inventory.get('internal_roots', {}),
        'highest_value_next_step': next_steps.get('highest_value_next_step'),
        'recommended_next_steps': next_steps.get('recommended_next_steps', [])[:5],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    return payload
