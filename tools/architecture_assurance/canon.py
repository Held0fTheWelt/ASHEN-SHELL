"""Deterministic file projection used beside AKDB's DB-native canon export."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
import hashlib
import json
from pathlib import Path
import shutil
from typing import Any


CANON_SCHEMA_VERSION = "bt.akdb_canon_manifest.v1"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_paths(
    config: Mapping[str, Any],
    repo_root: Path,
) -> list[str]:
    paths: set[str] = set()
    for raw in config.get("canonical_files", []):
        value = str(raw).replace("\\", "/")
        if any(token in value for token in "*?["):
            paths.update(
                path.relative_to(repo_root).as_posix()
                for path in repo_root.glob(value)
                if path.is_file()
            )
        else:
            paths.add(value)
    for subsystem in config["subsystems"]:
        sad_path = Path(str(subsystem["sad_path"]))
        paths.add(sad_path.as_posix())
        paths.add((sad_path.parent / "architecture.bindings.json").as_posix())
        for view in subsystem.get("required_views", []):
            paths.add(str(view["path"]).replace("\\", "/"))
    return sorted(
        path
        for path in paths
        if (repo_root / path).is_file()
    )


def build_canon_manifest(
    config: Mapping[str, Any],
    repo_root: Path,
) -> dict[str, Any]:
    files = [
        {
            "path": relative,
            "sha256": sha256_file(repo_root / relative),
            "bytes": (repo_root / relative).stat().st_size,
        }
        for relative in canonical_paths(config, repo_root)
    ]
    return {
        "schema_version": CANON_SCHEMA_VERSION,
        "project_id": config["project_id"],
        "repository_id": config["repository_id"],
        "files": files,
    }


def render_canon_manifest(manifest: Mapping[str, Any]) -> str:
    return json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def verify_canon_manifest(
    manifest_path: Path,
    repo_root: Path,
    expected_manifest: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    if not manifest_path.is_file():
        return {
            "matched": False,
            "missing": [manifest_path.relative_to(repo_root).as_posix()],
            "mismatched": [],
            "checked": 0,
        }
    manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    if manifest.get("schema_version") != CANON_SCHEMA_VERSION:
        raise ValueError("unsupported Better Tomorrow canon manifest")
    missing: list[str] = []
    mismatched: list[str] = []
    for item in manifest.get("files", []):
        path = repo_root / item["path"]
        if not path.is_file():
            missing.append(item["path"])
        elif sha256_file(path) != item["sha256"]:
            mismatched.append(item["path"])
    if expected_manifest is not None and manifest != expected_manifest:
        mismatched.append("$manifest")
    return {
        "matched": not missing and not mismatched,
        "missing": sorted(missing),
        "mismatched": sorted(mismatched),
        "checked": len(manifest.get("files", [])),
    }


def write_canon_manifest(
    config: Mapping[str, Any],
    repo_root: Path,
    destination: Path,
    *,
    dry_run: bool = False,
) -> dict[str, Any]:
    rendered = render_canon_manifest(build_canon_manifest(config, repo_root))
    current = (
        destination.read_text(encoding="utf-8-sig")
        if destination.is_file()
        else None
    )
    changed = rendered != current
    if changed and not dry_run:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(rendered, encoding="utf-8", newline="\n")
    return {
        "dry_run": dry_run,
        "changed": changed,
        "action": (
            "would_write"
            if dry_run and changed
            else "write"
            if changed
            else "unchanged"
        ),
        "path": destination.relative_to(repo_root).as_posix(),
    }


def export_canon(
    manifest_path: Path,
    repo_root: Path,
    destination: Path,
    *,
    dry_run: bool = False,
) -> dict[str, Any]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    if manifest.get("schema_version") != CANON_SCHEMA_VERSION:
        raise ValueError("unsupported Better Tomorrow canon manifest")
    actions: list[dict[str, Any]] = []
    for item in manifest["files"]:
        source = repo_root / item["path"]
        target = destination / item["path"]
        changed = not target.is_file() or sha256_file(target) != item["sha256"]
        actions.append(
            {
                "path": item["path"],
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
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
    return {
        "schema_version": "bt.akdb_canon_export_result.v1",
        "dry_run": dry_run,
        "destination": str(destination.resolve()),
        "actions": actions,
    }


def tree_digest(root: Path, paths: Iterable[str]) -> str:
    digest = hashlib.sha256()
    for relative in sorted(paths):
        path = root / relative
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()
