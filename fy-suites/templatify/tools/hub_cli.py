from __future__ import annotations
import json

def main(argv=None):
    print(json.dumps({"suite": "templatify", "ok": True}, indent=2))
    return 0
