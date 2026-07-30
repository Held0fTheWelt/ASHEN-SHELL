"""Generate Better Tomorrow's tailored semantic UML landscape."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

from .manifest_builder import load_config
from .semantic_models import (
    load_model_catalog,
    render_package_readme,
    render_semantic_view,
    render_traceability,
    render_view_companion,
    validate_model_catalog,
)


def _project(
    path: Path,
    rendered: str,
    repo_root: Path,
    *,
    dry_run: bool,
    subsystem: str,
    view: str,
    artifact: str,
) -> dict[str, Any]:
    current = (
        path.read_text(encoding="utf-8-sig") if path.is_file() else None
    )
    changed = current != rendered
    if changed and not dry_run:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(rendered, encoding="utf-8", newline="\n")
    return {
        "subsystem": subsystem,
        "view": view,
        "artifact": artifact,
        "path": path.relative_to(repo_root).as_posix(),
        "action": (
            "would_write"
            if dry_run and changed
            else "write"
            if changed
            else "unchanged"
        ),
    }


def generate_views(
    config_path: Path,
    repo_root: Path,
    *,
    dry_run: bool = False,
) -> dict[str, Any]:
    config = load_config(config_path)
    catalog_path = repo_root / str(config["model_catalog"])
    catalog = load_model_catalog(catalog_path)
    findings = validate_model_catalog(catalog, repo_root)
    if findings:
        joined = "\n".join(
            f"{item['subsystem']}:{item['view']}: {item['error']}"
            for item in findings
        )
        raise ValueError(f"semantic model catalog is invalid:\n{joined}")

    actions: list[dict[str, Any]] = []
    configured = {str(item["id"]) for item in config["subsystems"]}
    modeled = set(catalog["subsystems"])
    if configured != modeled:
        raise ValueError(
            "semantic catalog/config subsystem mismatch: "
            f"missing={sorted(configured - modeled)}, "
            f"extra={sorted(modeled - configured)}"
        )

    for subsystem_id, raw_model in catalog["subsystems"].items():
        model: Mapping[str, Any] = raw_model
        for view in model["views"]:
            destination = repo_root / str(view["path"])
            actions.append(
                _project(
                    destination,
                    render_semantic_view(
                        subsystem_id,
                        model,
                        view,
                        repo_root,
                    ),
                    repo_root,
                    dry_run=dry_run,
                    subsystem=subsystem_id,
                    view=str(view["id"]),
                    artifact="plantuml",
                )
            )
            companion = destination.with_suffix(".md")
            actions.append(
                _project(
                    companion,
                    render_view_companion(subsystem_id, model, view),
                    repo_root,
                    dry_run=dry_run,
                    subsystem=subsystem_id,
                    view=str(view["id"]),
                    artifact="companion",
                )
            )
        package_path = repo_root / str(model["package_path"])
        actions.append(
            _project(
                package_path / "README.md",
                render_package_readme(subsystem_id, model),
                repo_root,
                dry_run=dry_run,
                subsystem=subsystem_id,
                view="package",
                artifact="readme",
            )
        )
        actions.append(
            _project(
                package_path / "TRACEABILITY.md",
                render_traceability(subsystem_id, model),
                repo_root,
                dry_run=dry_run,
                subsystem=subsystem_id,
                view="package",
                artifact="traceability",
            )
        )
    return {
        "schema_version": "bt.semantic_view_generation_result.v1",
        "dry_run": dry_run,
        "catalog": str(config["model_catalog"]),
        "actions": actions,
    }
