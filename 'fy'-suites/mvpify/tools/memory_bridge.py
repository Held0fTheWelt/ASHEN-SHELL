
from __future__ import annotations

import json
from pathlib import Path


def write_memory_snapshot(path: Path, import_payload: dict, plan: dict) -> dict:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        'kind': 'mvpify_operations_memory',
        'source': import_payload.get('source'),
        'artifact_count': import_payload.get('artifact_count', 0),
        'highest_value_next_step': plan.get('highest_value_next_step'),
        'step_count': len(plan.get('steps', [])),
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding='utf-8')
    return payload
