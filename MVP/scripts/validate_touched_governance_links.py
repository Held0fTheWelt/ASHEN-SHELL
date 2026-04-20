from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

LINK_RE = re.compile(r"\]\(([^)]+)\)")

DEFAULT_PATHS = [
    "MVP_V24_PACKAGE_NOTE.md",
    "MVP_V24_START_HERE.md",
    "docs/README.md",
    "docs/INDEX.md",
    "docs/ADR/README.md",
    "docs/start-here/README.md",
    "docs/technical/README.md",
    "docs/dev/README.md",
    "docs/dev/contributing.md",
    "docs/dev/contracts/normative-contracts-index.md",
    "docs/operations/OPERATIONAL_GOVERNANCE_RUNTIME.md",
    "docs/ADR/adr-0001-runtime-authority-in-world-engine.md",
    "docs/ADR/adr-0002-backend-session-surface-quarantine.md",
    "docs/ADR/adr-0003-scene-identity-canonical-surface.md",
    "governance/V24_SOURCE_PRESERVATION_LEDGER.md",
    "'fy'-suites/README.md",
    "'fy'-suites/contractify/README.md",
    "'fy'-suites/despaghettify/README.md",
    "'fy'-suites/despaghettify/despaghettification_implementation_input.md",
    "'fy'-suites/docify/README.md",
    "'fy'-suites/despaghettify/state/WORKSTREAM_INDEX.md",
    "'fy'-suites/despaghettify/state/WORKSTREAM_GOVERNANCE_ATTACHMENT_STATE.md",
    "validation/V24_GOVERNANCE_ATTACHMENT_REPORT.md",
    "validation/V24_GOVERNANCE_ATTACHMENT_IMPLEMENTATION_REPORT.md",
]

def iter_links(path: Path, root: Path):
    text = path.read_text(encoding="utf-8", errors="replace")
    for m in LINK_RE.finditer(text):
        raw = m.group(1).strip()
        if not raw or raw.startswith(("#", "http://", "https://", "mailto:", "data:", "vscode:")):
            continue
        yield raw

def resolve(path: Path, target: str, root: Path) -> Path | None:
    clean = target.split("#", 1)[0].strip()
    if not clean:
        return None
    candidate = (path.parent / clean).resolve()
    try:
        candidate.relative_to(root.resolve())
    except ValueError:
        return None
    return candidate

def main() -> int:
    parser = argparse.ArgumentParser(description="Validate markdown links for the touched governance/doc surface.")
    parser.add_argument("--repo-root", default=".", help="Repository root")
    parser.add_argument("--json-out", default="validation/V24_TOUCHED_GOVERNANCE_LINK_CHECK.json")
    parser.add_argument("--md-out", default="validation/V24_TOUCHED_GOVERNANCE_LINK_CHECK.md")
    args = parser.parse_args()

    root = Path(args.repo_root).resolve()
    checked = []
    missing = []
    for rel in DEFAULT_PATHS:
        path = root / rel
        if not path.is_file():
            missing.append({"source": rel, "target": "<self>", "resolved": rel, "reason": "checked file missing"})
            continue
        checked.append(rel)
        for raw in iter_links(path, root):
            resolved = resolve(path, raw, root)
            if resolved is None:
                continue
            if not resolved.exists():
                missing.append({
                    "source": rel,
                    "target": raw,
                    "resolved": resolved.relative_to(root).as_posix(),
                    "reason": "missing target",
                })

    report = {
        "repo_root": str(root),
        "checked_files": checked,
        "checked_file_count": len(checked),
        "missing_count": len(missing),
        "missing": missing,
        "status": "PASS" if not missing else "FAIL",
    }
    json_path = root / args.json_out
    md_path = root / args.md_out
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    lines = [
        "# Touched governance/doc link check",
        "",
        f"- checked files: **{len(checked)}**",
        f"- missing links: **{len(missing)}**",
        f"- status: **{report['status']}**",
        "",
    ]
    if missing:
        lines.extend(["## Missing links", ""])
        for item in missing:
            lines.append(f"- `{item['source']}` → `{item['target']}` (`{item['resolved']}`)")
    else:
        lines.extend([
            "All checked touched governance/doc files resolved their repository-relative markdown links.",
        ])
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return 0 if not missing else 1

if __name__ == "__main__":
    raise SystemExit(main())
