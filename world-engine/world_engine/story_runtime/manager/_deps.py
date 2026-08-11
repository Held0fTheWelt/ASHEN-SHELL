"""Manager dependency aliases.

Collects dependency imports that are shared by compatibility-loaded manager methods and newer split manager modules.
"""
from __future__ import annotations

import logging
import sys

from .external_imports_core import *
from .external_imports_runtime import *

logger = logging.getLogger("app.story_runtime.manager")

SESSION_LOOP_LOG_POLICY_VERSION = "session_loop_logging.v1"
SESSION_LOOP_LOG_EVENT_VERSION = "session_loop_log_event.v1"
DEFAULT_SESSION_LANGUAGE = "de"
SESSION_LOOP_LOG_LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
}

_load_module_runtime_policy_original = load_module_runtime_policy
_log_story_turn_event_original = log_story_turn_event
_log_story_runtime_failure_original = log_story_runtime_failure

def _dispatch_package_symbol(name, original, self_symbol, *args, **kwargs):
    # Resolve the package that actually loaded this compatibility module.
    # The runtime is importable through both the canonical ``world_engine``
    # namespace and the legacy ``app`` namespace; hard-coding either one makes
    # package-level adapter injection silently ineffective for the other.
    package = sys.modules.get(__package__)
    target = getattr(package, name, None) if package is not None else None
    if target is not None and target is not self_symbol:
        return target(*args, **kwargs)
    return original(*args, **kwargs)

def load_module_runtime_policy(*args, **kwargs):
    return _dispatch_package_symbol(
        "load_module_runtime_policy",
        _load_module_runtime_policy_original,
        load_module_runtime_policy,
        *args,
        **kwargs,
    )

def log_story_turn_event(*args, **kwargs):
    return _dispatch_package_symbol(
        "log_story_turn_event",
        _log_story_turn_event_original,
        log_story_turn_event,
        *args,
        **kwargs,
    )

def log_story_runtime_failure(*args, **kwargs):
    return _dispatch_package_symbol(
        "log_story_runtime_failure",
        _log_story_runtime_failure_original,
        log_story_runtime_failure,
        *args,
        **kwargs,
    )

__all__ = [
    name
    for name in globals()
    if not name.startswith("__") and name != "annotations"
]
