#!/usr/bin/env python3
"""Inventory architecture sources and propose SAD mapping for WoS documentation migration."""

from __future__ import annotations

import csv
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

SOURCE_GLOBS: list[tuple[str, str]] = [
    ("docs/architecture", "legacy-stub-or-contract"),
    ("docs/technical/architecture", "technical-architecture"),
    ("docs/technical/runtime", "runtime-contract"),
    ("docs/contracts", "root-contract"),
    ("docs/ADR", "adr"),
]

PROPOSED_SAD: dict[str, str] = {
    "world_engine": "components/world-engine",
    "runtime-authority": "components/world-engine",
    "session_runtime": "components/world-engine",
    "turn_execution": "components/world-engine",
    "backend": "components/backend",
    "service-boundaries": "project/ecosystem-topology",
    "mvp_definition": "project/mvp-live-runtime-completion",
    "ai_story": "components/ai-stack",
    "ai-stack": "components/ai-stack",
    "rag": "components/ai-stack",
    "langgraph": "components/ai-stack",
    "mcp": "components/mcp-server",
    "god_of_carnage": "components/content-authority",
    "content": "components/content-authority",
    "frontend": "components/frontend",
    "player-shell": "components/frontend",
    "admin": "components/administration-tool",
    "observability": "project/observability-traceability",
    "langfuse": "project/observability-traceability",
    "security": "project/security-governance",
    "gate": "project/quality-gates",
}


def _guess_sad(path: Path) -> str:
    text = str(path).lower()
    for key, sad in PROPOSED_SAD.items():
        if key in text:
            return sad
    if "adr-" in text:
        return "project/governance (exception link)"
    return "TBD"


def main() -> int:
    out = REPO_ROOT / "docs" / "architecture" / "evidence" / "migration_inventory.csv"
    rows: list[dict[str, str]] = []
    for rel_root, category in SOURCE_GLOBS:
        root = REPO_ROOT / rel_root
        if not root.exists():
            rows.append(
                {
                    "source_path": rel_root,
                    "category": category,
                    "proposed_sad": "MISSING_PATH",
                    "action": "verify",
                }
            )
            continue
        for path in sorted(root.rglob("*.md")):
            rel = path.relative_to(REPO_ROOT).as_posix()
            if path.name == "README.md" and "ADR" in rel:
                continue
            rows.append(
                {
                    "source_path": rel,
                    "category": category,
                    "proposed_sad": _guess_sad(path),
                    "action": "absorb-or-stub",
                }
            )
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()) if rows else [])
        if rows:
            writer.writeheader()
            writer.writerows(rows)
    print(f"Wrote {len(rows)} rows to {out.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
