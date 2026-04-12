"""Deprecated shim — forwards to ``despaghettify/tools/spaghetti_ast_scan.py``.

Prefer: ``python -m despaghettify.tools`` (hub CLI) or run the canonical script under
``despaghettify/tools/``. This file will be removed after downstream callers migrate.
"""
from __future__ import annotations

import runpy
import warnings
from pathlib import Path

warnings.warn(
    "tools/spaghetti_ast_scan.py is deprecated; use "
    "`python despaghettify/tools/spaghetti_ast_scan.py` or `python -m despaghettify.tools check`. "
    "This shim will be removed in a future release.",
    DeprecationWarning,
    stacklevel=1,
)

_TARGET = Path(__file__).resolve().parent.parent / "despaghettify" / "tools" / "spaghetti_ast_scan.py"
runpy.run_path(str(_TARGET), run_name="__main__")
