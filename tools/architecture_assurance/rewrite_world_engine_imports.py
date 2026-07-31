"""Rewrite ``app.*`` → ``world_engine.*`` only under ``world-engine/`` (Wave 6).

Never touch ``backend/app`` — ``config``/``api`` collide with backend package names.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WE_ROOT = ROOT / "world-engine"

WE_TOP_LEVEL = (
    "api",
    "auth",
    "config",
    "content",
    "main",
    "middleware",
    "narrative",
    "observability",
    "repo_root",
    "runtime",
    "story_runtime",
    "story_runtime_shell_readout",
    "ui_backend_proxy",
)

_FROM_RE = re.compile(r"\bfrom\s+app\.(" + "|".join(WE_TOP_LEVEL) + r")\b")
_IMPORT_RE = re.compile(r"\bimport\s+app\.(" + "|".join(WE_TOP_LEVEL) + r")\b")


def rewrite_text(text: str) -> str:
    text = _FROM_RE.sub(r"from world_engine.\1", text)
    text = _IMPORT_RE.sub(r"import world_engine.\1", text)
    text = text.replace('importlib.import_module("app.', 'importlib.import_module("world_engine.')
    text = text.replace("importlib.import_module('app.", "importlib.import_module('world_engine.")
    return text


def main() -> int:
    changed = 0
    for path in WE_ROOT.rglob("*.py"):
        if "__pycache__" in path.parts:
            continue
        text = path.read_text(encoding="utf-8")
        new = rewrite_text(text)
        if new != text:
            path.write_text(new, encoding="utf-8", newline="\n")
            changed += 1
            print("rewrote", path.relative_to(ROOT))
    print("files_changed", changed)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
