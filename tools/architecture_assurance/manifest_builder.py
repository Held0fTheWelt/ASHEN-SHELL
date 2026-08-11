"""Build deterministic Better Tomorrow binding manifests from declared evidence."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
import json
from pathlib import Path
from typing import Any

from .discovery import (
    anchor_for_declared_path,
    discover_subsystem,
    path_matches_declared,
)
from .sad_parser import Declaration, evidence_paths, parse_sad
from .schemas import BINDINGS_SCHEMA_VERSION, validate_manifest
from .semantic_models import load_model_catalog, view_requirements


GENERATOR_VERSION = "bt-architecture-assurance/1"


def load_config(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if value.get("schema_version") != "bt.architecture_assurance_config.v1":
        raise ValueError("unsupported Better Tomorrow assurance config")
    if not isinstance(value.get("subsystems"), list):
        raise ValueError("assurance config requires subsystems")
    return value


def _source_roots(config: Mapping[str, Any]) -> list[str]:
    values: list[str] = []
    for roots in config.get("lane_roots", {}).values():
        values.extend(str(root) for root in roots)
    return list(dict.fromkeys(values))


def _normalize_relative_evidence(
    raw: str,
    sad_path: Path,
    repo_root: Path,
) -> str:
    target = raw.split("#", 1)[0].replace("\\", "/")
    if target.startswith(("../", "./")):
        candidate = (sad_path.parent / target).resolve()
        try:
            return candidate.relative_to(repo_root.resolve()).as_posix()
        except ValueError:
            return target
    return target


def _supporting_evidence(
    declaration_id: str,
    sad_path: Path,
) -> tuple[str, ...]:
    candidates: list[str] = []
    for filename in ("evidence-matrix.md", "mechanism-catalog.md", "decision-detail.md"):
        path = sad_path.parent / filename
        if not path.is_file():
            continue
        for line in path.read_text(encoding="utf-8-sig").splitlines():
            if declaration_id not in line:
                continue
            candidates.extend(evidence_paths(line))
    return tuple(dict.fromkeys(candidates))


def _anchors_for_declaration(
    declaration: Declaration,
    *,
    sad_path: Path,
    repo_root: Path,
    source_roots: Iterable[str],
    overrides: Iterable[str] = (),
) -> list[dict[str, Any]]:
    raw_paths = [
        *overrides,
        *declaration.evidence_paths,
        *_supporting_evidence(declaration.id, sad_path),
    ]
    anchors: list[dict[str, Any]] = []
    seen: set[tuple[str, int, str]] = set()
    for raw in raw_paths:
        normalized = _normalize_relative_evidence(raw, sad_path, repo_root)
        anchor = anchor_for_declared_path(
            normalized,
            repo_root,
            source_roots,
            title=declaration.title,
        )
        if anchor is None:
            continue
        key = (anchor["file"], anchor["line"], anchor["kind"])
        if key in seen:
            continue
        seen.add(key)
        anchors.append(anchor)
    anchors.sort(key=lambda item: (item["file"], item["line"], item["kind"]))
    return anchors


def _entry(
    declaration: Declaration,
    anchors: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "id": declaration.id,
        "title": declaration.title,
        "status": declaration.status,
        "state": "bound" if anchors else "claimed_only",
        "anchors": anchors,
    }


def _ownership_for_unit(
    unit: Mapping[str, Any],
    blocks: list[dict[str, Any]],
) -> str | None:
    unit_file = str(unit["anchor"]["file"])
    exact: list[tuple[int, str]] = []
    for block in blocks:
        for anchor in block["anchors"]:
            declared_path = str(anchor.get("declared_path", ""))
            if declared_path and path_matches_declared(unit_file, declared_path):
                exact.append((len(declared_path), str(block["id"])))
            elif anchor["file"] == unit_file:
                exact.append((len(anchor["file"]) + 1000, str(block["id"])))
    if exact:
        return sorted(exact, reverse=True)[0][1]
    if len(blocks) == 1:
        return str(blocks[0]["id"])
    return None


def build_manifest(
    subsystem: Mapping[str, Any],
    repo_root: Path,
    *,
    required_views: Iterable[Mapping[str, Any]] | None = None,
) -> tuple[dict[str, Any], list[dict[str, str]]]:
    sad_path = repo_root / str(subsystem["sad_path"])
    sad = parse_sad(sad_path.read_text(encoding="utf-8-sig"))
    roots = _source_roots(subsystem)
    overrides = subsystem.get("binding_overrides", {})

    blocks = [
        _entry(
            declaration,
            _anchors_for_declaration(
                declaration,
                sad_path=sad_path,
                repo_root=repo_root,
                source_roots=roots,
                overrides=overrides.get(declaration.id, []),
            ),
        )
        for declaration in sad.blocks
    ]
    decisions = [
        _entry(
            declaration,
            _anchors_for_declaration(
                declaration,
                sad_path=sad_path,
                repo_root=repo_root,
                source_roots=roots,
                overrides=overrides.get(declaration.id, []),
            ),
        )
        for declaration in sad.decisions
    ]
    discovered_units, errors = discover_subsystem(subsystem, repo_root)
    representation: dict[str, str] = {}
    out_of_scope: dict[str, str] = {}
    for unit in discovered_units:
        owner = _ownership_for_unit(unit, blocks)
        if owner:
            representation[str(unit["id"])] = owner
        else:
            from tools.architecture_assurance.out_of_scope_policy import (
                format_out_of_scope_reason,
            )

            out_of_scope[str(unit["id"])] = format_out_of_scope_reason(
                "unmapped",
                "Discovered inside the subsystem scan boundary but no declared "
                "building block owns its path. This is classified inventory, "
                "not architecture representation; see AR-V009.",
            )

    manifest = {
        "schema_version": BINDINGS_SCHEMA_VERSION,
        "generator": GENERATOR_VERSION,
        "subsystem": subsystem["id"],
        "scope": subsystem["scope"],
        "critical": bool(subsystem.get("critical")),
        "sad_path": subsystem["sad_path"],
        "lanes": list(subsystem["lanes"]),
        "building_blocks": blocks,
        "decisions": decisions,
        "discovered_units": discovered_units,
        "representation_map": dict(sorted(representation.items())),
        "out_of_scope": dict(sorted(out_of_scope.items())),
        "required_views": list(
            required_views
            if required_views is not None
            else subsystem.get("required_views", [])
        ),
    }
    return validate_manifest(manifest), errors


def render_manifest(manifest: Mapping[str, Any]) -> str:
    return json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def generate_manifests(
    config_path: Path,
    repo_root: Path,
    *,
    dry_run: bool = False,
) -> dict[str, Any]:
    config = load_config(config_path)
    catalog = load_model_catalog(repo_root / str(config["model_catalog"]))
    actions: list[dict[str, Any]] = []
    parse_errors: list[dict[str, str]] = []
    for subsystem in config["subsystems"]:
        manifest, errors = build_manifest(
            subsystem,
            repo_root,
            required_views=view_requirements(
                catalog,
                str(subsystem["id"]),
            ),
        )
        parse_errors.extend(
            {"subsystem": subsystem["id"], **error} for error in errors
        )
        destination = (
            repo_root / str(subsystem["sad_path"])
        ).parent / "architecture.bindings.json"
        rendered = render_manifest(manifest)
        current = (
            destination.read_text(encoding="utf-8-sig")
            if destination.is_file()
            else None
        )
        changed = current != rendered
        actions.append(
            {
                "subsystem": subsystem["id"],
                "path": destination.relative_to(repo_root).as_posix(),
                "action": (
                    "would_write"
                    if dry_run and changed
                    else "write"
                    if changed
                    else "unchanged"
                ),
            }
        )
        if changed and not dry_run:
            destination.write_text(
                rendered, encoding="utf-8", newline="\n"
            )
    return {
        "schema_version": "bt.manifest_generation_result.v1",
        "dry_run": dry_run,
        "actions": actions,
        "parse_errors": sorted(
            parse_errors,
            key=lambda item: (
                item["subsystem"],
                item["file"],
                item["error"],
            ),
        ),
    }
