from __future__ import annotations
import json
from pathlib import Path
from coda.adapter.service import CodaAdapter

def main(argv=None):
    root=Path(".").resolve()
    payload=CodaAdapter(root=root).audit(root)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0
