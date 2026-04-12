"""Deprecated shim — forwards to ``despaghettify/tools/ds005_runtime_import_check.py``.

Prefer: ``python despaghettify/tools/ds005_runtime_import_check.py`` or invoke via the hub
``python -m despaghettify.tools check``. This file will be removed after downstream callers migrate.
"""
from __future__ import annotations

import runpy
import warnings
from pathlib import Path

warnings.warn(
    "tools/ds005_runtime_import_check.py is deprecated; use "
    "`python despaghettify/tools/ds005_runtime_import_check.py` or `python -m despaghettify.tools check`. "
    "This shim will be removed in a future release.",
    DeprecationWarning,
    stacklevel=1,
)

_TARGET = Path(__file__).resolve().parent.parent / "despaghettify" / "tools" / "ds005_runtime_import_check.py"
runpy.run_path(str(_TARGET), run_name="__main__")
