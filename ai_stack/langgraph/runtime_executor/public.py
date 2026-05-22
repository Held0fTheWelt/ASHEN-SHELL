"""Runtime executor assembled from semantic source boundaries."""
from __future__ import annotations

from importlib import import_module
import linecache

from ai_stack.langgraph.runtime_executor.semantic_boundaries import (
    iter_source_module_names,
)

_source_lines: list[str] = []
for _part in iter_source_module_names():
    _source_lines.extend(import_module(f"{__package__}.{_part}").SOURCE_LINES)

_source = "".join(_source_lines)
linecache.cache["ai_stack/langgraph/langgraph_runtime_executor.py"] = (
    len(_source),
    None,
    _source.splitlines(keepends=True),
    "ai_stack/langgraph/langgraph_runtime_executor.py",
)
exec(compile(_source, "ai_stack/langgraph/langgraph_runtime_executor.py", "exec"), globals())

del import_module, iter_source_module_names, linecache, _part, _source, _source_lines
