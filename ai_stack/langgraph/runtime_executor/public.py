"""Runtime executor public surface (Wave 5: real assembled module, no exec)."""
from __future__ import annotations

from importlib import import_module

_impl = import_module("ai_stack.langgraph.langgraph_runtime_executor_impl")
_keep = {"__name__", "__file__", "__package__", "__loader__", "__spec__", "__doc__"}
for _key, _value in _impl.__dict__.items():
    if _key in _keep:
        continue
    globals()[_key] = _value
del import_module, _impl, _keep, _key, _value
