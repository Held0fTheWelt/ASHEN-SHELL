#!/usr/bin/env python3
"""Archive docs/ADR/ to docs/archive/adr-retired-2026/ with manifest (Phase 4)."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ADR_ROOT = REPO_ROOT / "docs" / "ADR"
ARCHIVE_ROOT = REPO_ROOT / "docs" / "archive" / "adr-retired-2026"
REGISTRY = REPO_ROOT / "docs" / "architecture" / "project" / "DECISION_REGISTRY.md"

SKIP_FILES = frozenset({"README.md", "adr-template.md"})


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def parse_registry_anchors() -> dict[str, str]:
    anchors: dict[str, str] = {}
    if not REGISTRY.is_file():
        return anchors
    for line in REGISTRY.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|") or "---" in line or "ex-ADR-ID" in line:
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) >= 3:
            anchors[cells[0]] = cells[2]
    return anchors


def adr_id_from_name(name: str) -> str | None:
    stem = Path(name).stem
    if stem == "LANGFUSE_OBSERVABILITY":
        return "LANGFUSE-OBSERVABILITY"
    if stem == "OBSERVABILITY_REDACTION_POLICY":
        return "OBSERVABILITY-REDACTION-POLICY"
    if stem == "MVP4_TEST_GATE_PLAN":
        return "MVP4-TEST-GATE-PLAN"
    mvp = __import__("re").match(r"adr-mvp(\d+)-(\d+)", stem)
    if mvp:
        return f"MVP{mvp.group(1)}-{mvp.group(2).zfill(3)}"
    if stem == "adr-0037-content-locale-story-runtime":
        return "ADR-0037-CONTENT"
    m = __import__("re").match(r"adr-(\d{4})", stem)
    if m:
        return f"ADR-{m.group(1)}"
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Archive ADR tree before retirement delete.")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    if not ADR_ROOT.is_dir():
        print(f"missing {ADR_ROOT}", file=sys.stderr)
        return 1

    anchors = parse_registry_anchors()
    manifest: list[dict[str, str]] = []
    files = sorted(p for p in ADR_ROOT.rglob("*.md") if p.name not in SKIP_FILES)

    for src in files:
        rel = src.relative_to(ADR_ROOT).as_posix()
        aid = adr_id_from_name(src.name)
        entry = {
            "path": rel,
            "sha256": sha256_file(src),
            "sad_anchor": anchors.get(aid or "", ""),
            "archived_at": datetime.now(timezone.utc).isoformat(),
        }
        manifest.append(entry)
        if args.apply:
            dest = ARCHIVE_ROOT / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)

    readme = ARCHIVE_ROOT / "README.md"
    readme_text = (
        "# ADR archive (retired 2026)\n\n"
        "Read-only evidence from `docs/ADR/` before SAD-only retirement.\n"
        "**Normative text** lives in `docs/architecture/**/architecture.md` §9 "
        "and [`DECISION_REGISTRY.md`](../architecture/project/DECISION_REGISTRY.md).\n\n"
        f"Files: {len(manifest)} · see `manifest.json`.\n"
    )

    if args.apply:
        ARCHIVE_ROOT.mkdir(parents=True, exist_ok=True)
        (ARCHIVE_ROOT / "manifest.json").write_text(
            json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
        )
        readme.write_text(readme_text, encoding="utf-8")
        print(f"archived {len(manifest)} files to {ARCHIVE_ROOT.relative_to(REPO_ROOT)}")
    else:
        print(f"dry-run: would archive {len(manifest)} files")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
