#!/usr/bin/env python3
"""Scaffold mechanism catalogs, evidence matrices, UML decisions/, TRACEABILITY for SAD restructure waves."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ARCH = REPO_ROOT / "docs" / "architecture"
UML = REPO_ROOT / "UML"

COMPONENT_SPECS: dict[str, dict] = {
    "backend": {
        "prefix": "BE",
        "full": True,
        "mechanisms": [
            ("M01", "Session surface quarantine", "Backend proxies play; no competing commit logic.", "D1"),
            ("M02", "Player session bundle", "Runtime readiness bundle for player HTTP surface.", "D2"),
            ("M03", "Story API proxy", "Forwards story operations to world-engine.", "D3"),
            ("M04", "ADR-0041 readiness consumer", "Veto-only runtime readiness overlay when flagged.", "D4"),
            ("M05", "WebSocket ticket bridge", "Shared-secret tickets for live play.", "D5"),
            ("M06", "Content publish boundary", "Sole publish path for canon content.", "D6"),
            ("M07", "Game service orchestration", "Coordinates bootstrap and play sessions.", "D7"),
            ("M08", "Diagnostics proxy", "Operator diagnostics without engine duplication.", "D8"),
        ],
    },
    "story-runtime-core": {
        "prefix": "SR",
        "full": True,
        "mechanisms": [
            ("M01", "Shared runtime types", "Cross-package runtime dataclasses and enums.", "D1"),
            ("M02", "Turn envelope", "Canonical turn lifecycle envelope fields.", "D2"),
            ("M03", "Aspect ledger contracts", "Runtime aspect ledger schema surfaces.", "D3"),
            ("M04", "Commit semantics helpers", "Live success and degradation markers.", "D4"),
            ("M05", "Session authority types", "Session identity and authority markers.", "D5"),
            ("M06", "Pi contract vocabulary", "Semantic names for capability contracts.", "D6"),
            ("M07", "Opening readiness", "Opening economy readiness evaluation types.", "D7"),
            ("M08", "Environment state contracts", "Actor location and scene projections.", "D8"),
        ],
    },
    "mcp-server": {
        "prefix": "MCP",
        "full": True,
        "mechanisms": [
            ("M01", "Canonical MCP surface", "Stable MCP tool routing for agents.", "D1"),
            ("M02", "Quality lab tools", "Read-only diagnostics MCP entry points.", "D2"),
            ("M03", "Langfuse evidence tools", "Trace and score inspection without mutation.", "D3"),
            ("M04", "Rate limit inventory", "Central route and rate-limit registry.", "D4"),
            ("M05", "Schema validation", "MCP request/response schema enforcement.", "D5"),
            ("M06", "Agent-ready routing", "Task-oriented MCP routes for operators.", "D6"),
            ("M07", "Redaction boundary", "No secrets in MCP payloads.", "D7"),
            ("M08", "Tool provenance", "Tool metadata and version surfacing.", "D8"),
        ],
    },
    "frontend": {
        "prefix": "FE",
        "full": False,
        "mechanisms": [
            ("M01", "Play WebSocket client", "Live run/story client loops.", "D1"),
            ("M02", "Typewriter cinematic", "Typewriter rendering direction.", "D2"),
            ("M03", "Block stream orchestrator", "Phase-2 event stream rendering.", "D3"),
            ("M04", "Session bootstrap UI", "Lobby and session start flows.", "D4"),
            ("M05", "Degraded mode display", "Honest live_success degradation UX.", "D5"),
        ],
    },
    "content-authority": {
        "prefix": "CA",
        "full": False,
        "mechanisms": [
            ("M01", "Content compile authority", "Compiler owns content shape validation.", "D1"),
            ("M02", "Locale boundary", "Content locale vs runtime language separation.", "D2"),
            ("M03", "Runtime locale removal", "No runtime content-locale lookups.", "D3"),
            ("M04", "Module packaging", "Story module packaging contracts.", "D4"),
            ("M05", "Publish handoff", "Handoff to backend publish routes only.", "D5"),
        ],
    },
    "administration-tool": {
        "prefix": "AT",
        "full": False,
        "mechanisms": [
            ("M01", "Operator manage surface", "Internal admin UI boundaries.", "D1"),
            ("M02", "Governance console", "Read-only governance projections display.", "D2"),
            ("M03", "Runtime config truth", "Feature flag and config inspection.", "D3"),
            ("M04", "Content tooling", "Non-publish content inspection.", "D4"),
            ("M05", "Diagnostics views", "Linked diagnostics without mutation.", "D5"),
        ],
    },
}

PROJECT_SPECS: dict[str, dict] = {
    "governance": {
        "prefix": "GOV",
        "mechanisms": [
            ("M01", "SAD-only decisions", "Normative decisions live in SAD §9 only.", "D5"),
            ("M02", "Revision state machine", "Revision review uses explicit states.", "D6"),
            ("M03", "Revision conflicts", "Conflicts are governance objects.", "D7"),
            ("M04", "Evaluation promotion gate", "Evaluation gates promotion.", "D8"),
            ("M05", "Event-driven workflows", "Governance workflows are event-driven.", "D9"),
            ("M06", "Decision boundary record", "Minimum schema for boundary recording.", "D10"),
            ("M07", "Risk framing", "Decision framework and kill criteria.", "D11"),
            ("M08", "Environment config", "Environment configuration governance.", "D12"),
        ],
    },
    "quality-gates": {
        "prefix": "QG",
        "mechanisms": [
            ("M01", "Canonical test runner", "tests/run_tests.py is sole runner.", "D1"),
            ("M02", "Suite presets", "MVP and suite flags for scoped verification.", "D2"),
            ("M03", "Python 3.14 standard", "Unified interpreter standard.", "D3"),
            ("M04", "Architecture doc gate", "SAD/UML documentation gate.", "D4"),
            ("M05", "MVP4 test gate plan", "Five core contract gates for MVP4.", "MVP4-TEST-GATE-PLAN"),
        ],
    },
    "documentation-supply-chain": {
        "prefix": "DSC",
        "mechanisms": [
            ("M01", "Internal architecture corpus", "docs/architecture ownership rules.", "D1"),
            ("M02", "SAD-only supply chain", "ADR directory retired; SAD is normative.", "D2"),
            ("M03", "Link audit", "Architecture link audit in CI.", "D3"),
            ("M04", "Evidence reports", "Migration evidence under evidence/.", "D4"),
        ],
    },
    "observability-traceability": {
        "prefix": "OBS",
        "mechanisms": [
            ("M01", "Turn trace correlation", "Request/turn correlation middleware.", "D1"),
            ("M02", "Langfuse provider", "Canonical AI/runtime observability.", "D6"),
            ("M03", "Redaction policy", "Trace redaction and correlation policy.", "D7"),
            ("M04", "Diagnostics HTTP", "Operator diagnostics surfaces.", "D5"),
        ],
    },
    "security-governance": {
        "prefix": "SEC",
        "mechanisms": [
            ("M01", "Browser mutation boundaries", "Security governance for browser mutations.", "D1"),
            ("M02", "Storage encryption", "Storage layer encryption governance.", "D2"),
            ("M03", "Admin control plane", "Admin control plane boundaries.", "D3"),
            ("M04", "At-rest encryption evidence", "Encryption evidence boundary.", "D4"),
            ("M05", "Provider credentials", "Provider credential governance.", "D5"),
        ],
    },
    "ecosystem-topology": {
        "prefix": "ECO",
        "mechanisms": [
            ("M01", "Service map", "World of Shadows deployable topology.", "D1"),
            ("M02", "docker-up bootstrap", "Complete local bootstrap via docker-up.py.", "D2"),
            ("M03", "Turn execution cross-cut", "Canonical turn execution across services.", "D3"),
        ],
    },
    "mvp-live-runtime-completion": {
        "prefix": "MVP",
        "mechanisms": [
            ("M01", "MVP expansion rule", "When not to expand the platform.", "ADR-0022"),
            ("M02", "MVP4 live setup", "MVP4 live runtime setup requirements.", "ADR-0032"),
            ("M03", "MVP ADR corpus", "Twenty-four MVP decision records consolidated.", "§9"),
        ],
    },
}


def write_catalog(base: Path, uml_base: Path, prefix: str, owner: str, mechanisms: list[tuple]) -> None:
    rows = [
        f"# {owner} Mechanism Catalog",
        "",
        f"**Owner:** [{owner} SAD](architecture.md)",
        "**Status:** restructured mechanism catalog",
        "**Last reconciled:** 2026-06-23",
        "",
        "| ID | Mechanism | Definition | Normative sources | UML / evidence | Proof state |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for mid, title, definition, dref in mechanisms:
        rid = f"{prefix}-{mid}"
        anchor_link = "architecture.md#9-architecture-decisions"
        rows.append(
            f"| {rid} | {title} | {definition} | [SAD {dref}]({anchor_link}) | [TRACEABILITY]({uml_base}/TRACEABILITY.md) | Partial |"
        )
    (base / "mechanism-catalog.md").write_text("\n".join(rows) + "\n", encoding="utf-8")


def write_matrix(base: Path, prefix: str, mechanisms: list[tuple]) -> None:
    rows = [
        f"# {base.name} Evidence Matrix",
        "",
        f"**Owner:** [{base.name} SAD](architecture.md) · [Mechanism catalog](mechanism-catalog.md)",
        "**Last reconciled:** 2026-06-23",
        "",
        "| Mechanism ID | Claim | Source | Test / gate | Proof state |",
        "| --- | --- | --- | --- | --- |",
    ]
    for mid, title, _defn, _dref in mechanisms[:5]:
        rows.append(f"| {prefix}-{mid} | {title} | see SAD §9 | `tests/gates/` | Partial |")
    (base / "evidence-matrix.md").write_text("\n".join(rows) + "\n", encoding="utf-8")


def write_traceability(uml_base: Path, mechanisms: list[tuple], prefix: str) -> None:
    rows = [
        f"# {uml_base.name} TRACEABILITY",
        "",
        "| Diagram | Decision | Claim | Source | Test / gate |",
        "| --- | --- | --- | --- | --- |",
    ]
    for i, (mid, title, _d, dref) in enumerate(mechanisms[:5]):
        dec = dref if dref.startswith("D") else "§9"
        rows.append(
            f"| c4-context | {dec} | {title} | see component SAD | `tests/gates/` |"
        )
    (uml_base / "TRACEABILITY.md").write_text("\n".join(rows) + "\n", encoding="utf-8")
    dec_dir = uml_base / "decisions"
    dec_dir.mkdir(parents=True, exist_ok=True)
    for _mid, title, definition, dref in mechanisms[:3]:
        slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:40]
        frag = dref.lower().replace(" ", "-")
        (dec_dir / f"{frag}-{slug}.md").write_text(
            f"# {dref}: {title}\n\n{definition}\n\nSee owning SAD §9.\n",
            encoding="utf-8",
        )




def scaffold(*, apply: bool) -> None:
    for slug, spec in COMPONENT_SPECS.items():
        base = ARCH / "components" / slug
        uml_base = UML / "Components" / slug
        if not base.is_dir():
            continue
        if apply:
            uml_rel = "../../../../UML/Components/" + slug
            write_catalog(base, Path(uml_rel), spec["prefix"], slug, spec["mechanisms"])
            if spec["full"]:
                write_matrix(base, spec["prefix"], spec["mechanisms"])
            uml_base.mkdir(parents=True, exist_ok=True)
            write_traceability(uml_base, spec["mechanisms"], spec["prefix"])
            print(f"component {slug}")

    for slug, spec in PROJECT_SPECS.items():
        base = ARCH / "project" / slug
        uml_base = UML / "Project" / slug
        if not base.is_dir():
            continue
        if apply:
            uml_rel = "../../../../UML/Project/" + slug
            write_catalog(base, Path(uml_rel), spec["prefix"], slug, spec["mechanisms"])
            write_matrix(base, spec["prefix"], spec["mechanisms"])
            uml_base.mkdir(parents=True, exist_ok=True)
            write_traceability(uml_base, spec["mechanisms"], spec["prefix"])
            print(f"project {slug}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    if not args.apply:
        print("dry-run; use --apply")
        return 0
    scaffold(apply=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
