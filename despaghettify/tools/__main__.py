"""Entry for ``python -m despaghettify.tools`` (no editable install required when run from repo root)."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from despaghettify.tools.despaghettify import main

if __name__ == "__main__":
    raise SystemExit(main())
