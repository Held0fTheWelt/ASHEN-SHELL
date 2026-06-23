#!/usr/bin/env python3
"""Rewrite docs/ADR/ path references to SAD anchors (Phase 6). fy-suites excluded."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
REGISTRY = REPO_ROOT / "docs" / "architecture" / "project" / "DECISION_REGISTRY.md"

SKIP_PREFIXES = (
    "'fy'-suites",
    "docs/archive",
    "node_modules",
    ".git",
)

SCAN_ROOTS = [
    REPO_ROOT / "docs",
    REPO_ROOT / "tests",
    REPO_ROOT / "backend",
    REPO_ROOT / "world-engine",
    REPO_ROOT / "ai_stack",
    REPO_ROOT / "frontend",
    REPO_ROOT / "administration-tool",
    REPO_ROOT / "scripts",
]
EXTRA = [REPO_ROOT / "mkdocs.yml"]

ADR_PATH_RE = re.compile(
    r"docs[/\\]ADR[/\\](?:MVP_Live_Runtime_Completion[/\\])?"
    r"(?:adr-(\d{4})[^)\s\"']*|adr-mvp(\d+)-(\d+)[^)\s\"']*|"
    r"LANGFUSE_OBSERVABILITY|OBSERVABILITY_REDACTION_POLICY)\.md",
    re.I,
)


def registry_map() -> dict[str, str]:
    """Map lowercase adr filename stem patterns to SAD anchor path (no fragment)."""
    mapping: dict[str, str] = {}
    if not REGISTRY.is_file():
        return mapping
    for line in REGISTRY.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|") or "---" in line or "ex-ADR-ID" in line:
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) < 3:
            continue
        aid, anchor = cells[0], cells[2]
        m = re.search(r"\]\(([^)#]+)(#[^)]+)?\)", anchor)
        if not m:
            continue
        sad_rel = m.group(1).replace("../architecture/", "docs/architecture/")
        if not sad_rel.startswith("docs/"):
            sad_rel = "docs/architecture/project/" + sad_rel.lstrip("./")
        fragment = m.group(2) or ""
        target = sad_rel + fragment
        if aid.startswith("ADR-"):
            num = aid.split("-", 1)[1]
            mapping[f"adr-{num}"] = target
        elif aid.startswith("MVP"):
            parts = aid.split("-", 1)
            if parts[1].isdigit():
                mapping[f"adr-mvp{parts[0][3:]}-{int(parts[1])}"] = target
            elif aid == "MVP4-TEST-GATE-PLAN":
                mapping["mvp4_test_gate_plan"] = target
        elif aid == "LANGFUSE-OBSERVABILITY":
            mapping["langfuse_observability"] = target
        elif aid == "OBSERVABILITY-REDACTION-POLICY":
            mapping["observability_redaction_policy"] = target
    return mapping


def rewrite_text(text: str, mapping: dict[str, str]) -> str:
    def repl(m: re.Match[str]) -> str:
        full = m.group(0)
        low = full.lower().replace("\\", "/")
        if "langfuse_observability" in low:
            return mapping.get("langfuse_observability", full)
        if "observability_redaction_policy" in low:
            return mapping.get("observability_redaction_policy", full)
        mvp = re.search(r"adr-mvp(\d+)-(\d+)", low)
        if mvp:
            key = f"adr-mvp{mvp.group(1)}-{int(mvp.group(2))}"
            return mapping.get(key, full)
        num = re.search(r"adr-(\d{4})", low)
        if num:
            key = f"adr-{num.group(1)}"
            return mapping.get(key, full)
        return full

    return ADR_PATH_RE.sub(repl, text)


def iter_files() -> list[Path]:
    paths: list[Path] = list(EXTRA)
    for root in SCAN_ROOTS:
        if root.is_dir():
            paths.extend(root.rglob("*"))
    out: list[Path] = []
    for path in paths:
        if not path.is_file():
            continue
        rel = path.relative_to(REPO_ROOT).as_posix()
        if any(rel.startswith(p) for p in SKIP_PREFIXES):
            continue
        if path.suffix not in {".md", ".py", ".yml", ".yaml", ".ts", ".tsx"}:
            continue
        if path.resolve() == REGISTRY.resolve():
            continue
        out.append(path)
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Rewrite ADR path refs to SAD.")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    mapping = registry_map()
    if not mapping:
        print("empty mapping", file=sys.stderr)
        return 1

    changed_files = 0
    for path in iter_files():
        try:
            original = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if "docs/ADR/" not in original and "docs\\ADR\\" not in original:
            continue
        updated = rewrite_text(original, mapping)
        if updated != original:
            changed_files += 1
            if args.apply:
                path.write_text(updated, encoding="utf-8")
            print(path.relative_to(REPO_ROOT))

    print(f"{'updated' if args.apply else 'would update'} {changed_files} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
