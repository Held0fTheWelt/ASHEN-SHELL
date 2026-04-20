from __future__ import annotations
import json
from pathlib import Path
from diagnosta.adapter.service import DiagnostaAdapter

def main(argv=None):
    root=Path(".").resolve()
    payload=DiagnostaAdapter(root=root).audit(root)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0
