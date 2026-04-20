from __future__ import annotations
import json
from pathlib import Path

def repo_root() -> Path:
    return Path(".").resolve()

def main(argv=None):
    argv=list(argv or [])
    out=None
    if "--envelope-out" in argv:
        idx=argv.index("--envelope-out")
        out=Path(argv[idx+1])
    payload={"suite": "postmanify", "command": (argv[0] if argv else "plan"), "ok": True}
    if out is not None:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(payload, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(payload, indent=2))
    return 0
