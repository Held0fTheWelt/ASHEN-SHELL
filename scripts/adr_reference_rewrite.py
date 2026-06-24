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

# Sphinx :doc: and markdown paths (optional .md suffix).
ADR_PATH_RE = re.compile(
    r"docs[/\\]ADR[/\\](?:MVP_Live_Runtime_Completion[/\\])?"
    r"(?:adr-(\d{4})(?:[-\w]*)?|adr-mvp(\d+)-(\d+)(?:[-\w]*)?|"
    r"LANGFUSE_OBSERVABILITY|OBSERVABILITY_REDACTION_POLICY|MVP4_TEST_GATE_PLAN)"
    r"(?:\.md)?",
    re.I,
)

REL_ADR_PATH_RE = re.compile(
    r"(?:\.\./)+ADR/(?:MVP_Live_Runtime_Completion/)?"
    r"(?:adr-(\d{4})(?:[-\w]*)?|adr-mvp(\d+)-(\d+)(?:[-\w]*)?|"
    r"LANGFUSE_OBSERVABILITY|OBSERVABILITY_REDACTION_POLICY)"
    r"(?:\.md)?",
    re.I,
)

TEXT_REPLACEMENTS: tuple[tuple[str, str], ...] = (
    (
        "| SAD §9 | `docs/architecture/project/DECISION_REGISTRY.md` | fill during implementation | ex-ADR / MVP id | found/not_present |",
        "| SAD §9 | `docs/architecture/project/DECISION_REGISTRY.md` | fill during implementation | ex-ADR / MVP id | found/not_present |",
    ),
    (
        "unless the matching SAD §9 decision is registered in [`DECISION_REGISTRY.md`](../../architecture/project/DECISION_REGISTRY.md) and matches the implemented repository state.",
        "unless the matching SAD §9 decision is registered in "
        "[`DECISION_REGISTRY.md`](../../architecture/project/DECISION_REGISTRY.md) "
        "and matches the implemented repository state.",
    ),
    (
        "- [x] MVP decisions absorbed in [`mvp-live-runtime-completion` SAD §9](../../architecture/project/mvp-live-runtime-completion/architecture.md#9-architecture-decisions)",
        "- [x] MVP decisions absorbed in "
        "[`mvp-live-runtime-completion` SAD §9](../../architecture/project/mvp-live-runtime-completion/architecture.md#9-architecture-decisions)",
    ),
    (
        "**Normative detail** for each heading below lives in the linked `docs/ADR/adr-*.md` file. "
        "**Catalogue / status table:** [`docs/ADR/README.md`](../../ADR/README.md).",
        "**Normative detail** for each heading below lives in the owning component or project SAD §9. "
        "**Catalogue / status table:** [`DECISION_REGISTRY.md`](../../architecture/project/DECISION_REGISTRY.md).",
    ),
    (
        "`02_architecture_decisions.md` — index of architecture decisions; **normative text** in [`DECISION_REGISTRY.md`](../../architecture/project/DECISION_REGISTRY.md) and owning SAD §9 blocks",
        "`02_architecture_decisions.md` — index of architecture decisions; **normative text** in "
        "[`DECISION_REGISTRY.md`](../../architecture/project/DECISION_REGISTRY.md) and owning SAD §9 blocks",
    ),
    (
        "- [observability SAD D6](../../architecture/project/observability-traceability/architecture.md#d6-langfuse-as-canonical-airuntime-observability-provider)",
        "- [observability SAD D6](../../architecture/project/observability-traceability/architecture.md#d6-langfuse-as-canonical-airuntime-observability-provider)",
    ),
    (
        "- [observability SAD D7](../../architecture/project/observability-traceability/architecture.md#d7-observability-redaction-and-trace-correlation-policy)",
        "- [observability SAD D7](../../architecture/project/observability-traceability/architecture.md#d7-observability-redaction-and-trace-correlation-policy)",
    ),
    (
        "Guides under [`docs/MVPs/MVP_Live_Runtime_Completion/`](../../../MVPs/MVP_Live_Runtime_Completion/README.md); normative MVP decisions in [§9 of this SAD](#9-architecture-decisions) and [`DECISION_REGISTRY.md`](../DECISION_REGISTRY.md).",
        "Guides under [`docs/MVPs/MVP_Live_Runtime_Completion/`](../../../MVPs/MVP_Live_Runtime_Completion/README.md); "
        "normative MVP decisions in [§9 of this SAD](#9-architecture-decisions) and [`DECISION_REGISTRY.md`](../DECISION_REGISTRY.md).",
    ),
    (
        "[mvp-live-runtime-completion SAD §9](mvp-live-runtime-completion/architecture.md#9-architecture-decisions) (archived MVP4 gate plan — see `docs/archive/adr-retired-2026/`)",
        "[mvp-live-runtime-completion SAD §9](mvp-live-runtime-completion/architecture.md#9-architecture-decisions) "
        "(archived MVP4 gate plan — see `docs/archive/adr-retired-2026/`)",
    ),
    (
        "- Supersedes ADR-0021 (stub — see `docs/archive/adr-retired-2026/legacy/`).",
        "- Supersedes ADR-0021 (stub — see `docs/archive/adr-retired-2026/legacy/`).",
    ),
    (
        "- [`DECISION_REGISTRY.md`](../../project/DECISION_REGISTRY.md) — ex-ADR → SAD §9 index",
        "- [`DECISION_REGISTRY.md`](../../project/DECISION_REGISTRY.md) — ex-ADR → SAD §9 index",
    ),
    (
        "- **Architecture decisions live only in SAD §9** (plus UML); retired ADRs live under `docs/archive/adr-retired-2026/`.",
        "- **Architecture decisions live only in SAD §9** (plus UML); retired ADRs live under `docs/archive/adr-retired-2026/`.",
    ),
    (
        "| `docs/archive/adr-retired-2026/` | Historical ADR files (read-only) |",
        "| `docs/archive/adr-retired-2026/` | Historical ADR files (read-only) |",
    ),
)


def registry_map() -> dict[str, str]:
    """Map lowercase adr filename stem patterns to SAD doc path (sphinx :doc: style, no .md)."""
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
        rel_path = m.group(1).replace("\\", "/")
        if rel_path.startswith("../components/"):
            sad_rel = "docs/architecture/components/" + rel_path.removeprefix("../components/")
        elif rel_path.startswith("../project/"):
            sad_rel = "docs/architecture/project/" + rel_path.removeprefix("../project/")
        elif rel_path.startswith("mvp-live-runtime-completion/"):
            sad_rel = "docs/architecture/project/" + rel_path
        elif rel_path.startswith("docs/"):
            sad_rel = rel_path
        else:
            sad_rel = "docs/architecture/project/" + rel_path.lstrip("./")
        # Sphinx :doc: paths omit .md
        target = sad_rel.removesuffix(".md")
        if aid.startswith("ADR-"):
            num = aid.split("-", 1)[1]
            mapping[f"adr-{num}"] = target
        elif aid.startswith("MVP"):
            mvp_num = aid[3:].split("-", 1)
            if len(mvp_num) == 2 and mvp_num[1].isdigit():
                mapping[f"adr-mvp{mvp_num[0]}-{int(mvp_num[1])}"] = target
            elif aid == "MVP4-TEST-GATE-PLAN":
                mapping["mvp4_test_gate_plan"] = target
        elif aid == "LANGFUSE-OBSERVABILITY":
            mapping["langfuse_observability"] = target
        elif aid == "OBSERVABILITY-REDACTION-POLICY":
            mapping["observability_redaction_policy"] = target
    return mapping


def _lookup_key(low: str) -> str | None:
    if "langfuse_observability" in low:
        return "langfuse_observability"
    if "observability_redaction_policy" in low:
        return "observability_redaction_policy"
    if "mvp4_test_gate_plan" in low:
        return "mvp4_test_gate_plan"
    mvp = re.search(r"adr-mvp(\d+)-(\d+)", low)
    if mvp:
        return f"adr-mvp{mvp.group(1)}-{int(mvp.group(2))}"
    num = re.search(r"adr-(\d{4})", low)
    if num:
        return f"adr-{num.group(1)}"
    return None


def rewrite_adr_path(match: re.Match[str], mapping: dict[str, str]) -> str:
    low = match.group(0).lower().replace("\\", "/")
    key = _lookup_key(low)
    if key and key in mapping:
        return mapping[key]
    return match.group(0)


def rewrite_text(text: str, mapping: dict[str, str]) -> str:
    for old, new in TEXT_REPLACEMENTS:
        text = text.replace(old, new)
    text = ADR_PATH_RE.sub(lambda m: rewrite_adr_path(m, mapping), text)
    text = REL_ADR_PATH_RE.sub(lambda m: rewrite_adr_path(m, mapping), text)
    return text


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
        if "docs/ADR/" not in original and "docs\\ADR\\" not in original and "/ADR/" not in original:
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
