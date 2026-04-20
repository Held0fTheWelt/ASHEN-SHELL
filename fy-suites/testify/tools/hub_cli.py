from __future__ import annotations
import json
from pathlib import Path
from testify.adapter.service import TestifyAdapter

def main(argv=None):
    root=Path(".").resolve()
    payload=TestifyAdapter(root=root).audit(root)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0
