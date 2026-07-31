"""Assemble runtime_executor SOURCE_LINES into a real Python module (Wave 5)."""
from __future__ import annotations

from pathlib import Path

from tools.architecture_assurance.unshard import extract_source_payload

ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    from ai_stack.langgraph.runtime_executor.semantic_boundaries import (
        iter_source_module_names,
    )

    pkg = ROOT / "ai_stack" / "langgraph" / "runtime_executor"
    parts: list[str] = []
    for name in iter_source_module_names():
        parts.append(extract_source_payload(pkg / f"{name}.py"))
    body = "".join(parts)
    if body.startswith("\\"):
        body = body[1:]
    if body.startswith("\n"):
        body = body[1:]
    out = ROOT / "ai_stack" / "langgraph" / "langgraph_runtime_executor_impl.py"
    # Payload already starts with a module docstring + ``from __future__``.
    text = body
    if not text.endswith("\n"):
        text += "\n"
    # Stamp Wave-5 provenance as a comment after the future import.
    stamp = (
        "# Wave 5: assembled from runtime_executor SOURCE_LINES via "
        "tools/architecture_assurance/assemble_runtime_executor.py\n"
    )
    marker = "from __future__ import annotations\n"
    if marker in text and stamp not in text:
        text = text.replace(marker, marker + "\n" + stamp, 1)
    out.write_text(text, encoding="utf-8", newline="\n")
    compile(text, str(out), "exec")
    print(f"wrote {out} bytes={out.stat().st_size} lines={text.count(chr(10))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
