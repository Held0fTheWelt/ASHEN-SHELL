"""Command-line entry point for Better Tomorrow architecture assurance."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from .audit import build_report
from .canon import export_canon, write_canon_manifest
from .manifest_builder import generate_manifests, load_config
from .reporters import write_reports
from .view_builder import generate_views


DEFAULT_CONFIG = Path("tools/architecture_assurance/config.json")


def _path(value: str | None, repo_root: Path) -> Path | None:
    if value is None:
        return None
    path = Path(value)
    return path if path.is_absolute() else repo_root / path


def _emit(value: Any) -> None:
    print(json.dumps(value, indent=2, ensure_ascii=False, sort_keys=True))


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="better-tomorrow-architecture",
        description="Source-bound architecture depth checks for Better Tomorrow.",
    )
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--config", default=str(DEFAULT_CONFIG))
    subcommands = parser.add_subparsers(dest="command", required=True)

    generate = subcommands.add_parser("generate")
    generate.add_argument("--dry-run", action="store_true")

    canon_manifest = subcommands.add_parser("canon-manifest")
    canon_manifest.add_argument("--dry-run", action="store_true")

    canon_export = subcommands.add_parser("canon-export")
    canon_export.add_argument("--destination", required=True)
    canon_export.add_argument("--dry-run", action="store_true")

    audit = subcommands.add_parser("audit")
    audit.add_argument("--json")
    audit.add_argument("--junit")
    audit.add_argument("--sarif")
    audit.add_argument("--dry-run", action="store_true")
    audit.add_argument(
        "--informational",
        action="store_true",
        help="Return zero even if the architecture gate fails.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    repo_root = Path(args.repo_root).resolve()
    config_path = _path(args.config, repo_root)
    assert config_path is not None
    config = load_config(config_path)

    if args.command == "generate":
        manifests = generate_manifests(
            config_path, repo_root, dry_run=args.dry_run
        )
        views = generate_views(config_path, repo_root, dry_run=args.dry_run)
        result = {
            "schema_version": "bt.architecture_generation_result.v1",
            "dry_run": args.dry_run,
            "manifests": manifests,
            "views": views,
        }
        _emit(result)
        return 1 if manifests["parse_errors"] else 0

    manifest_path = repo_root / str(config["canon_manifest"])
    if args.command == "canon-manifest":
        result = write_canon_manifest(
            config,
            repo_root,
            manifest_path,
            dry_run=args.dry_run,
        )
        _emit(result)
        return 0
    if args.command == "canon-export":
        result = export_canon(
            manifest_path,
            repo_root,
            _path(args.destination, repo_root) or repo_root,
            dry_run=args.dry_run,
        )
        _emit(result)
        return 0

    report = build_report(config_path, repo_root)
    exports = write_reports(
        report,
        json_path=_path(args.json, repo_root),
        junit_path=_path(args.junit, repo_root),
        sarif_path=_path(args.sarif, repo_root),
        dry_run=args.dry_run,
    )
    _emit(
        {
            "schema_version": "bt.architecture_audit_invocation.v1",
            "dry_run": args.dry_run,
            "status": report["gate"]["status"],
            "rollup": report["corpus_rollup"],
            "failures": report["gate"]["failures"],
            "exports": exports,
        }
    )
    return (
        0
        if report["gate"]["status"] == "PASS" or args.informational
        else 1
    )


if __name__ == "__main__":
    raise SystemExit(main())
