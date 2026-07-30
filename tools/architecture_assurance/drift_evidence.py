"""Reproducible Git and architecture-archaeology evidence for Better Tomorrow."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
import hashlib
import json
from pathlib import Path
import re
import subprocess
from typing import Any

from .semantic_models import load_model_catalog


SCHEMA_VERSION = "bt.architecture_drift_evidence.v1"
_ARCHIVE_NAME = re.compile(r"(?i)^(?:world_of_shadows|wos_)")
_ARCHIVE_EXTENSIONS = {".md", ".patch", ".txt", ".zip"}
_SNAPSHOT_ROOTS = {
    "administration-tool",
    "ai_stack",
    "backend",
    "content",
    "docs",
    "frontend",
    "story_runtime_core",
    "tests",
    "tools/mcp_server",
    "world-engine",
}
_SOURCE_EXTENSIONS = {
    ".css",
    ".html",
    ".js",
    ".json",
    ".md",
    ".py",
    ".toml",
    ".yaml",
    ".yml",
}
_CURATED_ARCHAEOLOGY = (
    "world_of_shadows_narrative_system_audit_2026-04-22.md",
    "WOS_GOC_SELF_CONTAINED_ONE_EXPERIENCE_MVP_V3.md",
    "WOS_COMBINED_FOUNDATION_REPAIR_AND_REPLACEMENT_BUNDLE_TASK.md",
    "WOS_LEGACY_DEBT_AND_TEST_TRUTH_AUDIT_PROMPT.md",
)
_CLAIM_HEADING = re.compile(
    r"^#{2,4}\s+(?P<text>(?:Leak L-|I-|R-|ADR-|Goal |"
    r"Source-of-Truth|Current implementation problem|"
    r"Non-Negotiable Architecture).+)$"
)


def _git(repo_root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", "-C", str(repo_root), *args],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return completed.stdout


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _paths_argument(roots: Iterable[str]) -> list[str]:
    return ["--", *sorted(set(roots))]


def _recent_history(
    repo_root: Path,
    roots: list[str],
    *,
    window: int,
) -> dict[str, Any]:
    raw = _git(
        repo_root,
        "log",
        f"-n{window}",
        "--date=short",
        "--format=@@%H%x09%ad%x09%s",
        "--name-status",
        *_paths_argument(roots),
    )
    commits: list[dict[str, Any]] = []
    current: dict[str, Any] | None = None
    touches = 0
    renames = 0
    for line in raw.splitlines():
        if line.startswith("@@"):
            parts = line[2:].split("\t", 2)
            current = {
                "commit": parts[0],
                "date": parts[1],
                "subject": parts[2] if len(parts) > 2 else "",
                "paths": 0,
                "renames": 0,
            }
            commits.append(current)
            continue
        if not line.strip() or current is None:
            continue
        current["paths"] += 1
        touches += 1
        if line.startswith("R"):
            current["renames"] += 1
            renames += 1
    return {
        "window": window,
        "commit_count": len(commits),
        "path_touches": touches,
        "renames": renames,
        "latest_commits": commits[:10],
    }


def _subsystem_git_evidence(
    repo_root: Path,
    subsystem_id: str,
    model: Mapping[str, Any],
    *,
    window: int,
) -> dict[str, Any]:
    roots = [str(value) for value in model.get("history_roots", [])]
    tracked = [
        line
        for line in _git(
            repo_root,
            "ls-files",
            *_paths_argument(roots),
        ).splitlines()
        if line
    ]
    lifetime = int(
        _git(
            repo_root,
            "rev-list",
            "--count",
            "HEAD",
            *_paths_argument(roots),
        ).strip()
        or "0"
    )
    return {
        "subsystem": subsystem_id,
        "history_roots": roots,
        "tracked_file_count": len(tracked),
        "lifetime_commit_count": lifetime,
        "recent": _recent_history(repo_root, roots, window=window),
    }


def _is_snapshot_source(path: Path, root: Path) -> bool:
    if path.suffix.lower() not in _SOURCE_EXTENSIONS:
        return False
    relative_path = path.relative_to(root)
    if any(
        part in {".fydata", ".pytest_cache", "__pycache__", "node_modules"}
        for part in relative_path.parts
    ):
        return False
    relative = relative_path.as_posix()
    return any(
        relative == prefix or relative.startswith(prefix + "/")
        for prefix in _SNAPSHOT_ROOTS
    )


def _snapshot_comparison(
    repo_root: Path,
    archive_root: Path,
) -> dict[str, Any] | None:
    snapshot = (
        archive_root
        / "world_of_shadows_repaired_package_2026-04-21"
        / "MVP_repaired_2026-04-21"
    )
    if not snapshot.is_dir():
        return None
    historical = {
        path.relative_to(snapshot).as_posix()
        for path in snapshot.rglob("*")
        if path.is_file() and _is_snapshot_source(path, snapshot)
    }
    current = {
        path.relative_to(repo_root).as_posix()
        for path in repo_root.rglob("*")
        if path.is_file()
        and ".git" not in path.parts
        and _is_snapshot_source(path, repo_root)
    }
    historical_only = sorted(historical - current)
    current_only = sorted(current - historical)
    common = historical & current
    return {
        "snapshot_label": snapshot.relative_to(archive_root).as_posix(),
        "historical_source_files": len(historical),
        "current_source_files": len(current),
        "common_paths": len(common),
        "historical_only_paths": len(historical_only),
        "current_only_paths": len(current_only),
        "historical_only_sample": historical_only[:100],
        "current_only_sample": current_only[:100],
    }


def _curated_claims(path: Path) -> list[str]:
    claims: list[str] = []
    for line in path.read_text(
        encoding="utf-8-sig",
        errors="replace",
    ).splitlines():
        match = _CLAIM_HEADING.match(line)
        if match:
            claims.append(match.group("text").strip())
    return claims


def _archive_evidence(
    repo_root: Path,
    archive_root: Path | None,
) -> dict[str, Any]:
    if archive_root is None:
        return {
            "available": False,
            "root_label": None,
            "reason": "no archaeology root supplied",
        }
    root = archive_root.resolve()
    if not root.is_dir():
        return {
            "available": False,
            "root_label": root.name,
            "reason": "archaeology root does not exist",
        }
    artifacts: list[dict[str, Any]] = []
    for path in sorted(root.iterdir(), key=lambda value: value.name.lower()):
        if (
            path.is_file()
            and _ARCHIVE_NAME.match(path.name)
            and path.suffix.lower() in _ARCHIVE_EXTENSIONS
        ):
            artifacts.append(
                {
                    "path": path.name,
                    "size": path.stat().st_size,
                    "sha256": _sha256(path),
                }
            )
    curated: list[dict[str, Any]] = []
    for name in _CURATED_ARCHAEOLOGY:
        path = root / name
        if path.is_file():
            curated.append(
                {
                    "path": name,
                    "size": path.stat().st_size,
                    "sha256": _sha256(path),
                    "claim_headings": _curated_claims(path),
                }
            )
    return {
        "available": True,
        "root_label": root.name,
        "handling": "read-only, non-authoritative architecture archaeology",
        "top_level_artifact_count": len(artifacts),
        "artifacts": artifacts,
        "curated_documents": curated,
        "snapshot_comparison": _snapshot_comparison(repo_root, root),
    }


def build_drift_evidence(
    repo_root: Path,
    model_catalog_path: Path,
    *,
    archive_root: Path | None = None,
    history_window: int = 300,
) -> dict[str, Any]:
    """Build deterministic evidence without mutating repository or archive."""
    catalog = load_model_catalog(model_catalog_path)
    first = _git(
        repo_root,
        "log",
        "--reverse",
        "--format=%H%x09%ad%x09%s",
        "--date=short",
    ).splitlines()[0]
    first_parts = first.split("\t", 2)
    subsystems = [
        _subsystem_git_evidence(
            repo_root,
            subsystem_id,
            model,
            window=history_window,
        )
        for subsystem_id, model in sorted(catalog["subsystems"].items())
    ]
    return {
        "schema_version": SCHEMA_VERSION,
        "source_precedence": [
            "accepted architecture decisions and explicit authority contracts",
            "current executable code and behavioral tests",
            "Git history as evolution evidence",
            "historical MVPs and work orders as non-authoritative intent evidence",
        ],
        "repository": {
            "head": _git(repo_root, "rev-parse", "HEAD").strip(),
            "branch": _git(repo_root, "branch", "--show-current").strip(),
            "commit_count": int(
                _git(repo_root, "rev-list", "--count", "HEAD").strip()
            ),
            "first_commit": {
                "commit": first_parts[0],
                "date": first_parts[1],
                "subject": first_parts[2] if len(first_parts) > 2 else "",
            },
            "history_window": history_window,
        },
        "subsystems": subsystems,
        "architecture_archaeology": _archive_evidence(
            repo_root,
            archive_root,
        ),
    }


def render_drift_evidence(evidence: Mapping[str, Any]) -> str:
    """Render the most decision-relevant drift evidence as Markdown."""
    repository = evidence["repository"]
    rows = [
        "# Better Tomorrow architecture drift baseline",
        "",
        "This baseline correlates current source, Git evolution and a "
        "read-only historical MVP/work-order corpus. Historical material is "
        "evidence of prior intent, not current authority.",
        "",
        "## Repository chronology",
        "",
        f"- Analyzed branch: `{repository['branch']}`",
        f"- Analyzed HEAD: `{repository['head']}`",
        f"- Repository commits: {repository['commit_count']}",
        "- First commit: "
        f"`{repository['first_commit']['commit']}` "
        f"({repository['first_commit']['date']})",
        "",
        "## Git drift by architecture scope",
        "",
        "| Scope | Tracked files | Lifetime commits | Recent touches | "
        "Recent renames |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for item in evidence["subsystems"]:
        rows.append(
            f"| `{item['subsystem']}` | {item['tracked_file_count']} | "
            f"{item['lifetime_commit_count']} | "
            f"{item['recent']['path_touches']} | "
            f"{item['recent']['renames']} |"
        )
    archive = evidence["architecture_archaeology"]
    rows.extend(["", "## Architecture archaeology", ""])
    if not archive["available"]:
        rows.append(f"Archive unavailable: {archive['reason']}.")
    else:
        rows.extend(
            [
                f"- Source label: `{archive['root_label']}`",
                f"- Handling: {archive['handling']}",
                "- Relevant top-level artifacts: "
                f"{archive['top_level_artifact_count']}",
                "- Curated work orders/audits: "
                f"{len(archive['curated_documents'])}",
            ]
        )
        snapshot = archive.get("snapshot_comparison")
        if snapshot:
            rows.extend(
                [
                    "- April snapshot/current common paths: "
                    f"{snapshot['common_paths']}",
                    "- Historical-only paths: "
                    f"{snapshot['historical_only_paths']}",
                    "- Current-only paths: "
                    f"{snapshot['current_only_paths']}",
                ]
            )
        rows.extend(
            [
                "",
                "### Harvested claim headings",
                "",
                "| Historical document | Claim headings |",
                "| --- | ---: |",
            ]
        )
        for document in archive["curated_documents"]:
            rows.append(
                f"| `{document['path']}` | "
                f"{len(document['claim_headings'])} |"
            )
    rows.extend(
        [
            "",
            "## Interpretation rule",
            "",
            "Each harvested historical claim must be classified as confirmed "
            "current, superseded, conflicting, or an open target question. "
            "A filename, task completion statement, or archived green test "
            "run is not sufficient proof.",
            "",
        ]
    )
    return "\n".join(rows)


def write_drift_evidence(
    evidence: Mapping[str, Any],
    json_path: Path,
    markdown_path: Path,
    *,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Write evidence idempotently, or report the intended changes."""
    projections = {
        json_path: json.dumps(
            evidence,
            indent=2,
            ensure_ascii=False,
            sort_keys=True,
        )
        + "\n",
        markdown_path: render_drift_evidence(evidence),
    }
    actions: list[dict[str, str]] = []
    for path, content in projections.items():
        current = (
            path.read_text(encoding="utf-8-sig") if path.is_file() else None
        )
        changed = current != content
        if changed and not dry_run:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8", newline="\n")
        actions.append(
            {
                "path": path.as_posix(),
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
        "schema_version": "bt.architecture_drift_export.v1",
        "dry_run": dry_run,
        "actions": actions,
    }
