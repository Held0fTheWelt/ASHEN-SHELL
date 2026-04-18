from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .models import UsageEvent
from .pricing_catalog import get_price


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_ledger(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text('', encoding='utf-8')


def compute_cost(model: str, service_tier: str, input_tokens: int, cached_input_tokens: int, output_tokens: int) -> float:
    price = get_price(model, service_tier)
    usd = (
        (input_tokens / 1_000_000.0) * price.get('input', 0.0)
        + (cached_input_tokens / 1_000_000.0) * price.get('cached_input', 0.0)
        + (output_tokens / 1_000_000.0) * price.get('output', 0.0)
    )
    return round(usd, 8)


def append_event(path: Path, event: UsageEvent) -> None:
    ensure_ledger(path)
    with path.open('a', encoding='utf-8') as fh:
        fh.write(json.dumps(event.to_dict(), ensure_ascii=False) + '\n')


def read_events(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    out = []
    for line in path.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line:
            continue
        out.append(json.loads(line))
    return out


def normalize_event(raw: dict[str, Any]) -> UsageEvent:
    model = str(raw.get('model', 'unknown'))
    service_tier = str(raw.get('service_tier', 'standard'))
    input_tokens = int(raw.get('input_tokens', raw.get('prompt_tokens', 0)) or 0)
    cached_input_tokens = int(raw.get('cached_input_tokens', raw.get('cached_prompt_tokens', 0)) or 0)
    output_tokens = int(raw.get('output_tokens', raw.get('completion_tokens', 0)) or 0)
    cost = raw.get('cost_usd')
    if cost is None:
        cost = compute_cost(model, service_tier, input_tokens, cached_input_tokens, output_tokens)
    return UsageEvent(
        timestamp_utc=str(raw.get('timestamp_utc', utc_now())),
        suite=str(raw.get('suite', 'unknown')),
        run_id=str(raw.get('run_id', 'unknown-run')),
        model=model,
        service_tier=service_tier,
        input_tokens=input_tokens,
        cached_input_tokens=cached_input_tokens,
        output_tokens=output_tokens,
        reasoning_tokens=int(raw.get('reasoning_tokens', 0) or 0),
        cost_usd=float(cost),
        technique_tags=[str(item) for item in raw.get('technique_tags', [])],
        utility_score=(float(raw['utility_score']) if raw.get('utility_score') is not None else None),
        resolved_findings=int(raw.get('resolved_findings', 0) or 0),
        notes=str(raw.get('notes', '')),
        source=str(raw.get('source', 'manual')),
    )


def ingest_jsonl(path: Path, source_path: Path) -> int:
    ensure_ledger(path)
    count = 0
    for line in source_path.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line:
            continue
        event = normalize_event(json.loads(line))
        append_event(path, event)
        count += 1
    return count
