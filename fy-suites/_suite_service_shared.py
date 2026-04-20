from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fy_platform.ai.workspace import write_text


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding='utf-8'))
    except Exception:
        return {}


def _write_md_summary(path: Path, title: str, lines: list[str]) -> None:
    write_text(path, f"# {title}\n\n" + "\n".join(lines).rstrip() + "\n")
