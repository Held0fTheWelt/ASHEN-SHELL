"""Generate compact, deterministic and source-linked PlantUML depth views."""

from __future__ import annotations

from collections.abc import Mapping
import json
import os
from pathlib import Path
import re
from typing import Any

from .manifest_builder import load_config


_TARGETS = {"context": 4, "container": 6, "component": 8, "class": 6}


def _safe(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_]", "_", value)


def _short(value: str, limit: int = 54) -> str:
    compact = re.sub(r"\s+", " ", value).strip()
    return compact if len(compact) <= limit else compact[: limit - 1] + "…"


def _candidates(manifest: Mapping[str, Any]) -> list[dict[str, str]]:
    values: list[dict[str, str]] = []
    for entry in manifest.get("building_blocks", []):
        anchors = entry.get("anchors", [])
        if anchors:
            values.append(
                {
                    "id": str(entry["id"]),
                    "title": str(entry["title"]),
                    "path": str(anchors[0]["file"]),
                    "kind": "declared building block",
                    "category": "declared",
                }
            )
    for unit in manifest.get("discovered_units", []):
        anchor = unit["anchor"]
        title = (
            anchor.get("symbol")
            or anchor.get("object")
            or anchor.get("route")
            or str(unit["id"]).split(":")[-1]
        )
        values.append(
            {
                "id": str(unit["id"]),
                "title": str(title),
                "path": str(anchor["file"]),
                "kind": str(unit["kind"]),
                "category": str(unit["kind"]),
            }
        )
    unique: dict[tuple[str, str], dict[str, str]] = {}
    for value in values:
        unique[(value["title"], value["path"])] = value
    return [unique[key] for key in sorted(unique)]


def _selected_candidates(
    candidates: list[dict[str, str]],
    level: str,
) -> list[dict[str, str]]:
    preferences = {
        "context": ("declared", "deployment", "api", "python"),
        "container": ("declared", "deployment", "api", "content", "python"),
        "component": ("api", "python", "web", "schema", "content", "declared"),
        "class": ("python", "schema", "api", "content", "web", "declared"),
    }
    order = preferences.get(level, tuple())
    rank = {category: index for index, category in enumerate(order)}
    ordered = sorted(
        candidates,
        key=lambda item: (
            rank.get(item["category"], len(rank)),
            item["title"],
            item["path"],
        ),
    )
    return ordered[: _TARGETS.get(level, 6)]


def render_view(
    manifest: Mapping[str, Any],
    view: Mapping[str, Any],
    repo_root: Path,
) -> str:
    level = str(view["level"])
    destination = repo_root / str(view["path"])
    candidates = _candidates(manifest)
    selected = _selected_candidates(candidates, level)
    sad_relative = Path(
        os.path.relpath(repo_root / str(manifest["sad_path"]), destination.parent)
    ).as_posix()
    lines = [
        "@startuml",
        f"title {_short(str(manifest['subsystem']))} — {level.title()} View",
        "left to right direction",
        "skinparam shadowing false",
        "skinparam rectangle {",
        "  BackgroundColor #F7F9FC",
        "  BorderColor #34495E",
        "}",
        "",
        (
            f'rectangle "{_short(str(manifest["subsystem"]))}\\n'
            "Responsibility: architecture boundary\\n"
            "Owns: declarations and implementation evidence\\n"
            f'[[{sad_relative} SAD]]" as ROOT'
        ),
        "",
    ]
    for index, item in enumerate(selected, start=1):
        relative = Path(
            os.path.relpath(repo_root / item["path"], destination.parent)
        ).as_posix()
        label = (
            f"{_short(item['title'])}\\n"
            f"Responsibility: {_short(item['kind'])}\\n"
            f"Evidence contract: source anchor\\n"
            f"[[{relative} source]]"
        )
        lines.append(f'rectangle "{label}" as E{index}')
    lines.append("")
    for index in range(1, len(selected) + 1):
        lines.append(f'E{index} ..> ROOT : "evidence for boundary"')
    lines.extend(
        [
            "",
            "legend bottom",
            "Every element links to its implementation anchor.",
            "Generated from architecture.bindings.json; do not hand-edit.",
            "endlegend",
            "@enduml",
            "",
        ]
    )
    return "\n".join(lines)


def generate_views(
    config_path: Path,
    repo_root: Path,
    *,
    dry_run: bool = False,
) -> dict[str, Any]:
    config = load_config(config_path)
    actions: list[dict[str, Any]] = []
    for subsystem in config["subsystems"]:
        manifest_path = (
            repo_root / str(subsystem["sad_path"])
        ).parent / "architecture.bindings.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
        for view in subsystem.get("required_views", []):
            destination = repo_root / str(view["path"])
            rendered = render_view(manifest, view, repo_root)
            current = (
                destination.read_text(encoding="utf-8-sig")
                if destination.is_file()
                else None
            )
            changed = current != rendered
            if changed and not dry_run:
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_text(rendered, encoding="utf-8", newline="\n")
            actions.append(
                {
                    "subsystem": subsystem["id"],
                    "view": view["id"],
                    "path": view["path"],
                    "action": (
                        "would_write"
                        if dry_run and changed
                        else "write"
                        if changed
                        else "unchanged"
                    ),
                }
            )
    return {
        "schema_version": "bt.architecture_view_generation_result.v1",
        "dry_run": dry_run,
        "actions": actions,
    }
