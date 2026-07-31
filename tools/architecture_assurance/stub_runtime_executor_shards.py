"""Replace runtime_executor SOURCE_LINES shards with stubs (Wave 5)."""
from __future__ import annotations

from pathlib import Path

from ai_stack.langgraph.runtime_executor.semantic_boundaries import iter_source_module_names

ROOT = Path(__file__).resolve().parents[2]
PKG = ROOT / "ai_stack" / "langgraph" / "runtime_executor"

STUB = '''"""Retired SOURCE_LINES shard — logic lives in langgraph_runtime_executor_impl (Wave 5).

Boundary registry still lists this module name for documentation; it no longer
contributes executable string payloads.
"""
from __future__ import annotations

__all__: list[str] = []
'''


def main() -> int:
    for name in iter_source_module_names():
        path = PKG / f"{name}.py"
        path.write_text(STUB, encoding="utf-8", newline="\n")
        print("stubbed", path.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
