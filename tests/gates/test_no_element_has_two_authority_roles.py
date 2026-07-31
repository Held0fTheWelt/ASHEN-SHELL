"""Wave 8: no model element may carry two disjoint authority roles on one anchor."""

from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CATALOG = REPO_ROOT / "tools" / "architecture_assurance" / "model_catalog.json"

DISJOINT_AUTHORITY_PAIRS: tuple[tuple[str, str], ...] = (
    ("validation", "commit"),
    ("session", "proposal"),
    ("store", "persistence"),
    ("store", "store_node"),
    ("persistence", "store_node"),
)


def _collect_offenders(catalog: dict) -> set[str]:
    offenders: set[str] = set()
    for subsystem_id, subsystem in catalog.get("subsystems", {}).items():
        elements = subsystem.get("elements") or {}
        if not isinstance(elements, dict):
            continue
        by_anchor: dict[str, set[str]] = {}
        for element_id, element in elements.items():
            if not isinstance(element, dict):
                continue
            anchor = str(element.get("anchor") or "").strip()
            if not anchor:
                continue
            by_anchor.setdefault(anchor, set()).add(str(element_id))
        for anchor, ids in by_anchor.items():
            for left, right in DISJOINT_AUTHORITY_PAIRS:
                if left in ids and right in ids:
                    offenders.add(
                        f"{subsystem_id}:{anchor} holds both '{left}' and '{right}'"
                    )
    return offenders


def test_no_element_has_two_authority_roles() -> None:
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    offenders = _collect_offenders(catalog)
    assert not offenders, "dual-authority aliases remain:\n" + "\n".join(sorted(offenders))
