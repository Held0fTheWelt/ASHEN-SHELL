from __future__ import annotations
import json
from pathlib import Path
from observifyfy.adapter.service import ObservifyfyAdapter

def main(argv=None):
    root=Path(".").resolve()
    payload=ObservifyfyAdapter(root=root).audit(root)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0
