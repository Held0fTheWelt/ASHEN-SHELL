#!/usr/bin/env python3
"""DS-015 optional: static import fan-in for ``app.runtime`` (no third-party deps).

Scans ``backend/app/runtime/*.py`` for ``from app.runtime.<mod>`` and
``import app.runtime.<mod>``-style edges; prints how many files reference each
target module stem. Run from repo root:

  python tools/ds015_runtime_import_fanin.py
  python tools/ds015_runtime_import_fanin.py --targets turn_executor,runtime_models,ai_turn_executor
"""

from __future__ import annotations

import argparse
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "backend" / "app" / "runtime"
FROM_RE = re.compile(
    r"^\s*from\s+app\.runtime\.([a-zA-Z0-9_]+)\s+import",
    re.MULTILINE,
)
IMPORT_AS_RE = re.compile(
    r"^\s*import\s+app\.runtime\.([a-zA-Z0-9_]+)\s+as",
    re.MULTILINE,
)


def _edges(source_stem: str, text: str) -> list[str]:
    out: list[str] = []
    for m in FROM_RE.finditer(text):
        out.append(m.group(1))
    for m in IMPORT_AS_RE.finditer(text):
        out.append(m.group(1))
    return out


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--targets",
        default="turn_executor,runtime_models,ai_turn_executor,supervisor_orchestrator",
        help="Comma-separated module stems to highlight (default: hot runtime seams).",
    )
    args = p.parse_args()
    targets = {t.strip() for t in args.targets.split(",") if t.strip()}

    fan_in: Counter[str] = Counter()
    for path in sorted(ROOT.glob("*.py")):
        if path.name.startswith("__"):
            continue
        stem = path.stem
        text = path.read_text(encoding="utf-8")
        for dep in _edges(stem, text):
            if dep != stem:
                fan_in[dep] += 1

    print("app.runtime import fan-in (intra-package 'from app.runtime.X import ...' counts)\n")
    for mod, n in fan_in.most_common(40):
        mark = " *" if mod in targets else ""
        print(f"  {n:3d}  {mod}{mark}")

    print("\nHighlighted targets detail:")
    for t in sorted(targets):
        n = fan_in.get(t, 0)
        print(f"  {t}: {n} importing file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
