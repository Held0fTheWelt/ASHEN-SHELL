"""Deprecated shim — forwards to ``despaghettify/tools/spaghetti_ast_scan.py``.

Prefer: ``python -m despaghettify.tools`` (hub CLI) or run the canonical script under
``'fy'-suites/despaghettify/tools/``. This file will be removed after downstream callers migrate.
"""
from __future__ import annotations

import runpy
import warnings
from pathlib import Path

warnings.warn(
    "tools/spaghetti_ast_scan.py is deprecated; use "
    "`python \"./'fy'-suites/despaghettify/tools/spaghetti_ast_scan.py\"` or `python -m despaghettify.tools check`. "
    "This shim will be removed in a future release.",
    DeprecationWarning,
    stacklevel=1,
)

_root = Path(__file__).resolve().parent.parent
_nested = _root / "'fy'-suites" / "despaghettify" / "tools" / "spaghetti_ast_scan.py"
_legacy = _root / "despaghettify" / "tools" / "spaghetti_ast_scan.py"
_TARGET = _nested if _nested.is_file() else _legacy
runpy.run_path(str(_TARGET), run_name="__main__")
