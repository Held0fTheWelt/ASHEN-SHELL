"""Deprecated shim — forwards to ``despaghettify/tools/ds005_runtime_import_check.py``.

Prefer: ``python "./'fy'-suites/despaghettify/tools/ds005_runtime_import_check.py"`` or invoke via the hub
``python -m despaghettify.tools check``. This file will be removed after downstream callers migrate.
"""
from __future__ import annotations

import runpy
import warnings
from pathlib import Path

warnings.warn(
    "tools/ds005_runtime_import_check.py is deprecated; use "
    "`python \"./'fy'-suites/despaghettify/tools/ds005_runtime_import_check.py\"` or `python -m despaghettify.tools check`. "
    "This shim will be removed in a future release.",
    DeprecationWarning,
    stacklevel=1,
)

_root = Path(__file__).resolve().parent.parent
_nested = _root / "'fy'-suites" / "despaghettify" / "tools" / "ds005_runtime_import_check.py"
_legacy = _root / "despaghettify" / "tools" / "ds005_runtime_import_check.py"
_TARGET = _nested if _nested.is_file() else _legacy
runpy.run_path(str(_TARGET), run_name="__main__")
