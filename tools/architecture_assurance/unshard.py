"""Deterministic unshard helper for SOURCE / SOURCE_LINES modules.

Reads shard modules via AST, concatenates payload strings, and writes real
Python source. Dry-run capable and idempotent when the target already matches.
"""
from __future__ import annotations

import argparse
import ast
from pathlib import Path


def extract_source_payload(path: Path) -> str:
    """Return concatenated SOURCE or SOURCE_LINES text from a shard file."""
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if not isinstance(target, ast.Name):
                continue
            if target.id == "SOURCE" and isinstance(node.value, ast.Constant) and isinstance(
                node.value.value, str
            ):
                return node.value.value
            if target.id == "SOURCE_LINES" and isinstance(node.value, (ast.List, ast.Tuple)):
                parts: list[str] = []
                for elt in node.value.elts:
                    if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                        parts.append(elt.value)
                    else:
                        raise ValueError(f"{path}: non-string SOURCE_LINES element")
                return "".join(parts)
    raise ValueError(f"{path}: no SOURCE / SOURCE_LINES assignment found")


def assemble_chunks(chunk_paths: list[Path]) -> str:
    body = "".join(extract_source_payload(path) for path in chunk_paths)
    # Shard files use r'''\ ... ''' so the payload often starts with a stray backslash.
    if body.startswith("\\"):
        body = body[1:]
    if body.startswith("\n"):
        body = body[1:]
    return body


def write_if_changed(path: Path, content: str, *, dry_run: bool) -> bool:
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = path.read_text(encoding="utf-8") if path.exists() else None
    if existing == content:
        return False
    if dry_run:
        return True
    path.write_text(content, encoding="utf-8", newline="\n")
    return True


def render_method_module(
    *,
    module_doc: str,
    method_body: str,
    class_name: str,
) -> str:
    """Wrap indented method source as a real mixin module."""
    return (
        f'"""{module_doc}"""\n'
        "from __future__ import annotations\n\n"
        "from ._deps import *\n\n\n"
        f"class {class_name}:\n"
        f"{method_body}"
        "\n\n"
        f"__all__ = [{class_name!r}]\n"
    )


def render_toplevel_module(*, module_doc: str, body: str) -> str:
    return (
        f'"""{module_doc}"""\n'
        "from __future__ import annotations\n\n"
        "from ._deps import *\n\n"
        f"{body}"
        "\n"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--manager-root",
        type=Path,
        default=Path("world-engine/world_engine/story_runtime/manager"),
    )
    args = parser.parse_args(argv)
    manager_root: Path = args.manager_root
    sources = manager_root / "_legacy_sources"
    manifest_path = sources / "manifest.py"
    # Import SOURCE_CHUNKS without executing package side effects.
    tree = ast.parse(manifest_path.read_text(encoding="utf-8"), filename=str(manifest_path))
    chunks_map: dict[str, list[str]] = {}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "SOURCE_CHUNKS":
                    chunks_map = ast.literal_eval(node.value)
    if not chunks_map:
        raise SystemExit(f"SOURCE_CHUNKS missing in {manifest_path}")

    targets = {
        "method:_finalize_committed_turn": manager_root / "commit_finalization.py",
        "method:_build_narrator_path_opening_state": manager_root / "narrator_path_opening_state.py",
        "_build_langfuse_path_summary": manager_root
        / "observability"
        / "langfuse_path_summary.py",
        "_emit_langfuse_evidence_observations": manager_root
        / "observability"
        / "langfuse_evidence_observations.py",
        "_emit_langfuse_path_spans": manager_root / "observability" / "langfuse_path_spans.py",
        "_emit_langfuse_runtime_aspect_observability": manager_root
        / "observability"
        / "langfuse_runtime_aspect_observability.py",
        "_live_scene_blocks_from_visible_bundle": manager_root / "live_scene_blocks.py",
        "_record_visible_projection_aspect": manager_root / "visible_projection_aspect.py",
    }

    changed = 0
    for key, out_path in targets.items():
        names = chunks_map[key]
        chunk_paths = [sources / f"{name}.py" for name in names]
        body = assemble_chunks(chunk_paths)
        if key.startswith("method:"):
            method_name = key.split(":", 1)[1]
            class_name = {
                "_finalize_committed_turn": "_CommitFinalizationMixin",
                "_build_narrator_path_opening_state": "_NarratorPathOpeningStateMixin",
            }[method_name]
            content = render_method_module(
                module_doc=f"Unsharded manager method `{method_name}` (Wave 1).",
                method_body=body,
                class_name=class_name,
            )
        else:
            # Observability helpers live under manager/observability/ — import deps from parent.
            deps_import = (
                "from .._deps import *\n\n"
                if "observability" in out_path.as_posix()
                else "from ._deps import *\n\n"
            )
            content = (
                f'"""Unsharded manager helper `{key}` (Wave 1)."""\n'
                "from __future__ import annotations\n\n"
                f"{deps_import}"
                f"{body}"
                "\n"
            )
            # Ensure __all__ for package re-exports.
            symbol = key
            if f"__all__" not in content:
                content = content.rstrip() + f"\n\n__all__ = [{symbol!r}]\n"
        if write_if_changed(out_path, content, dry_run=args.dry_run):
            changed += 1
            print(("DRY " if args.dry_run else "WROTE"), out_path.as_posix())
        else:
            print("OK", out_path.as_posix())
    print(f"changed={changed} dry_run={args.dry_run}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
