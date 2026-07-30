"""Validate and project Better Tomorrow architecture-drift reconciliation."""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping
import json
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "bt.architecture_drift_claim_catalog.v1"
_STATUSES = {
    "confirmed_current",
    "superseded",
    "conflicting",
    "open_target",
}


def load_claim_catalog(path: Path) -> dict[str, Any]:
    catalog = json.loads(path.read_text(encoding="utf-8-sig"))
    if catalog.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("unsupported architecture drift claim catalog")
    return catalog


def validate_claim_catalog(
    catalog: Mapping[str, Any],
    repo_root: Path,
) -> list[str]:
    findings: list[str] = []
    seen: set[str] = set()
    for claim in catalog.get("claims", []):
        claim_id = str(claim.get("id", ""))
        if not claim_id or claim_id in seen:
            findings.append(f"duplicate or missing claim id: {claim_id}")
        seen.add(claim_id)
        if claim.get("status") not in _STATUSES:
            findings.append(f"{claim_id}: unsupported status")
        for field in (
            "concern",
            "diagnosis",
            "target",
            "historical_claims",
            "historical_sources",
            "current_evidence",
            "acceptance_evidence",
        ):
            if not claim.get(field):
                findings.append(f"{claim_id}: missing {field}")
        for anchor in claim.get("current_evidence", []):
            if not (repo_root / str(anchor)).exists():
                findings.append(f"{claim_id}: missing current anchor {anchor}")
    return sorted(findings)


def render_claim_reconciliation(catalog: Mapping[str, Any]) -> str:
    counts = Counter(claim["status"] for claim in catalog["claims"])
    rows = [
        "# Better Tomorrow architecture drift reconciliation",
        "",
        "Historical MVPs and work orders are classified against current source "
        "and Git evidence. The target column states the currently most coherent "
        "implementable direction; open or conflicting entries still require "
        "behavioral closure.",
        "",
        "## Status summary",
        "",
        "| Status | Claims | Meaning |",
        "| --- | ---: | --- |",
        f"| Confirmed current | {counts['confirmed_current']} | "
        "Current code and accepted architecture agree. |",
        f"| Superseded | {counts['superseded']} | "
        "Historical evidence remains useful but has no current authority. |",
        f"| Conflicting | {counts['conflicting']} | "
        "Concurrent structures or semantics need an explicit decision. |",
        f"| Open target | {counts['open_target']} | "
        "Repair evidence exists, but production-path proof is incomplete. |",
        "",
        "## Reconciliation map",
        "",
        "| ID | Concern | Status | Diagnosis | Target direction |",
        "| --- | --- | --- | --- | --- |",
    ]
    for claim in catalog["claims"]:
        rows.append(
            f"| `{claim['id']}` | {claim['concern']} | "
            f"`{claim['status']}` | {claim['diagnosis']} | "
            f"{claim['target']} |"
        )
    rows.extend(["", "## Claim details", ""])
    for claim in catalog["claims"]:
        rows.extend(
            [
                f"### {claim['id']} - {claim['concern']}",
                "",
                f"**Status:** `{claim['status']}`",
                "",
                "**Historical assertions**",
                "",
            ]
        )
        rows.extend(f"- {value}" for value in claim["historical_claims"])
        rows.extend(["", "**Current evidence**", ""])
        rows.extend(
            f"- [`{value}`](../../../{value})"
            for value in claim["current_evidence"]
        )
        rows.extend(["", "**Best target direction**", "", claim["target"], ""])
        rows.extend(["**Acceptance evidence**", ""])
        rows.extend(f"- {value}" for value in claim["acceptance_evidence"])
        rows.append("")
    return "\n".join(rows)


def project_claim_reconciliation(
    catalog_path: Path,
    destination: Path,
    repo_root: Path,
    *,
    dry_run: bool = False,
) -> dict[str, Any]:
    catalog = load_claim_catalog(catalog_path)
    findings = validate_claim_catalog(catalog, repo_root)
    if findings:
        raise ValueError("invalid drift claims:\n" + "\n".join(findings))
    content = render_claim_reconciliation(catalog)
    current = (
        destination.read_text(encoding="utf-8-sig")
        if destination.is_file()
        else None
    )
    changed = current != content
    if changed and not dry_run:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(content, encoding="utf-8", newline="\n")
    try:
        display_path = destination.relative_to(repo_root).as_posix()
    except ValueError:
        display_path = destination.as_posix()
    return {
        "schema_version": "bt.architecture_drift_reconciliation_export.v1",
        "dry_run": dry_run,
        "claims": len(catalog["claims"]),
        "status_counts": dict(sorted(Counter(
            claim["status"] for claim in catalog["claims"]
        ).items())),
        "path": display_path,
        "action": (
            "would_write"
            if dry_run and changed
            else "write"
            if changed
            else "unchanged"
        ),
    }
