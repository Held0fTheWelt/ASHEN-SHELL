"""Operational settings and runtime governance services.

Wave 5: implementation lives in ``governance_runtime_service_impl.py``.
Module identity is bound to the impl so importers and patches share one namespace.
"""

from __future__ import annotations

import sys as _sys

from app.services.governance import governance_runtime_service_impl as _impl

_sys.modules[__name__] = _impl
