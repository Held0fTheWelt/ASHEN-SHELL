#!/usr/bin/env python3
"""Rebuild DECISION_REGISTRY from archive manifest + known MVP anchors."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST = REPO_ROOT / "docs" / "archive" / "adr-retired-2026" / "manifest.json"
REGISTRY = REPO_ROOT / "docs" / "architecture" / "project" / "DECISION_REGISTRY.md"

MVP_SAD_PATH = REPO_ROOT / "docs" / "architecture" / "project" / "mvp-live-runtime-completion" / "architecture.md"

MVP_SAD_FALLBACK = "[mvp-live-runtime-completion §9](mvp-live-runtime-completion/architecture.md#9-architecture-decisions)"

ANCHOR_OVERRIDES: dict[str, str] = {
    "ADR-0041": "[ai-stack D12](../components/ai-stack/architecture.md#d12-controlled-runtime-capability-authority)",
    "ADR-0058": "[ai-stack D16](../components/ai-stack/architecture.md#d16-director-driven-pulse-and-block-stream-bus)",
    "ADR-0059": "[ai-stack D16](../components/ai-stack/architecture.md#d16-director-driven-pulse-and-block-stream-bus)",
    "ADR-0061": "[ai-stack D15](../components/ai-stack/architecture.md#d15-director-pause-mode-for-gathering-interruption)",
    "ADR-0063": "[world-engine D6](../components/world-engine/architecture.md#d6-w5-actor-tracking)",
    "ADR-0065": "[world-engine D15](../components/world-engine/architecture.md#d15-w5-narrator-strict-mode-becomes-the-default-actor-situation-surface)",
    "ADR-0066": "[world-engine D16](../components/world-engine/architecture.md#d16-retire-legacy-narrator-consequence-area-fields-after-w5-location-framing)",
    "ADR-0067": "[world-engine D15](../components/world-engine/architecture.md#d15-w5-narrator-strict-mode-becomes-the-default-actor-situation-surface)",
    "ADR-0068": "[world-engine D15](../components/world-engine/architecture.md#d15-w5-narrator-strict-mode-becomes-the-default-actor-situation-surface)",
    "ADR-0069": "[world-engine D6](../components/world-engine/architecture.md#d6-w5-actor-tracking)",
    "ADR-0070": "[world-engine D6](../components/world-engine/architecture.md#d6-w5-actor-tracking)",
    "ADR-0071": "[world-engine D16](../components/world-engine/architecture.md#d16-retire-legacy-narrator-consequence-area-fields-after-w5-location-framing)",
    "LANGFUSE-OBSERVABILITY": "[observability D6](../project/observability-traceability/architecture.md#d6-langfuse-as-canonical-airuntime-observability-provider)",
    "OBSERVABILITY-REDACTION-POLICY": "[observability D7](../project/observability-traceability/architecture.md#d7-observability-redaction-and-trace-correlation-policy)",
}

FRAGMENT_FIXES: dict[str, str] = {
    "d6-w5-actor-tracking-and-player-view": "d6-w5-actor-tracking",
    "d15-w5-actor-tracking-follow-up": "d15-w5-narrator-strict-mode-becomes-the-default-actor-situation-surface",
    "d16-retire-legacy-narrator-consequence-area-fields": "d16-retire-legacy-narrator-consequence-area-fields-after-w5-location-framing",
    "d6-langfuse-canonical-observability-provider": "d6-langfuse-as-canonical-airuntime-observability-provider",
    "d7-observability-redaction-policy": "d7-observability-redaction-and-trace-correlation-policy",
}


def heading_slug(heading: str) -> str:
    """GitHub-style anchor from a §9 ### heading line (without leading hashes)."""
    slug = heading.strip().lower()
    slug = re.sub(r"[^\w\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug)
    return slug


def load_mvp_anchor_map() -> dict[str, str]:
    """Map MVP1-001 … MVP5-003 to per-decision §9 anchors in the MVP SAD."""
    if not MVP_SAD_PATH.is_file():
        return {}
    text = MVP_SAD_PATH.read_text(encoding="utf-8")
    if "## 9. Architecture Decisions" not in text:
        return {}
    section = text.split("## 9. Architecture Decisions", 1)[1].split("## 10.", 1)[0]
    out: dict[str, str] = {}
    for m in re.finditer(r"^### (MVP\d+-\d+): (.+)$", section, re.M):
        mvp_id = m.group(1).upper()
        title = m.group(2).strip()
        frag = heading_slug(f"{mvp_id} {title}")
        label = f"{mvp_id} {title}"
        out[mvp_id] = f"[{label}](mvp-live-runtime-completion/architecture.md#{frag})"
    return out


def mvp_anchor(aid: str, mvp_map: dict[str, str]) -> str:
    return mvp_map.get(aid, MVP_SAD_FALLBACK)


def normalize_anchor(anchor: str) -> str:
    if not anchor.startswith("["):
        return anchor
    for old, new in FRAGMENT_FIXES.items():
        if f"#{old}" in anchor and f"#{new}" not in anchor:
            anchor = anchor.replace(f"#{old}", f"#{new}")
    return simplify_anchor(anchor)


def simplify_anchor(anchor: str) -> str:
    """Link to SAD §9 when manifest fragment slugs are stale."""
    m = re.match(r"(\[[^\]]+\]\([^)#]+)", anchor)
    if m:
        return f"{m.group(1)}#9-architecture-decisions)"
    return anchor

ADR_ID_RE = re.compile(r"adr-(\d{4})|adr-mvp(\d+)-(\d+)", re.I)


def adr_id_from_path(path: str) -> str | None:
    name = Path(path).stem
    mapping = {
        "LANGFUSE_OBSERVABILITY": "LANGFUSE-OBSERVABILITY",
        "OBSERVABILITY_REDACTION_POLICY": "OBSERVABILITY-REDACTION-POLICY",
        "MVP4_TEST_GATE_PLAN": "MVP4-TEST-GATE-PLAN",
        "adr-0037-content-locale-story-runtime": "ADR-0037-CONTENT",
    }
    if name in mapping:
        return mapping[name]
    mvp = re.match(r"adr-mvp(\d+)-(\d+)", name, re.I)
    if mvp:
        return f"MVP{mvp.group(1)}-{mvp.group(2).zfill(3)}"
    m = re.match(r"adr-(\d{4})", name)
    if m:
        return f"ADR-{m.group(1)}"
    return None


def load_manifest_map() -> dict[str, dict]:
    entries = json.loads(MANIFEST.read_text(encoding="utf-8"))
    out: dict[str, dict] = {}
    for e in entries:
        aid = adr_id_from_path(e["path"])
        if not aid:
            continue
        prev = out.get(aid)
        if prev is None or "(open exception)" in prev.get("sad_anchor", ""):
            out[aid] = e
    return out


def uml_from_anchor(anchor: str) -> str:
    if "components/" in anchor:
        m = re.search(r"components/([^/]+)/architecture\.md#(d\d+[-\w]*)", anchor)
        if m:
            comp, frag = m.group(1), m.group(2)
            return f"[{frag}](../../../../UML/Components/{comp}/decisions/{frag}.md)"
    if "project/" in anchor:
        m = re.search(r"project/([^/]+)/architecture\.md#([\w-]+)", anchor)
        if m:
            proj, frag = m.group(1), m.group(2)
            return f"[{frag}](../../../../UML/Project/{proj}/decisions/{frag}.md)"
    return "—"


def status_from_anchor(anchor: str) -> str:
    if "open exception" in anchor.lower():
        return "Not Finished"
    if "mvp-live-runtime" in anchor:
        return "Accepted"
    return "Accepted"


def ordered_ids(manifest_map: dict[str, dict]) -> list[str]:
    adrs = sorted(k for k in manifest_map if k.startswith("ADR-"))
    others = sorted(k for k in manifest_map if not k.startswith("ADR-"))
    return adrs + others


def build_registry(manifest_map: dict[str, dict]) -> str:
    mvp_map = load_mvp_anchor_map()
    lines = [
        "# Decision registry (ex-ADR → SAD)",
        "",
        "Maps every retired ADR file to its **normative SAD §9 anchor**.",
        "Normative text lives in SAD §9 + UML; ADR files are read-only under",
        "`docs/archive/adr-retired-2026/`.",
        "",
        "Governance: [governance SAD D5](governance/architecture.md#d5-sad-only-decision-retirement).",
        "",
        "| ex-ADR-ID | Status | SAD anchor | UML | Gate | Archive SHA | Waiver |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for aid in ordered_ids(manifest_map):
        if aid == "ADR-0021":
            continue  # deprecated duplicate; see governance D4
        e = manifest_map[aid]
        anchor_raw = ANCHOR_OVERRIDES.get(aid, e.get("sad_anchor", ""))
        if aid.startswith("MVP"):
            anchor = mvp_anchor(aid, mvp_map)
        elif anchor_raw.startswith("["):
            anchor = normalize_anchor(anchor_raw)
        elif anchor_raw.startswith("(open"):
            anchor = normalize_anchor(anchor_raw.replace("(open exception) ", ""))
        else:
            anchor = "—"
        status = status_from_anchor(anchor_raw)
        uml = "—"
        sha = e.get("sha256", "")[:12]
        waiver = "yes" if aid in ("LANGFUSE-OBSERVABILITY", "OBSERVABILITY-REDACTION-POLICY", "MVP4-TEST-GATE-PLAN") else ""
        if anchor == "—":
            status = ""
        lines.append(f"| {aid} | {status} | {anchor} | {uml} | — | {sha} | {waiver} |")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    manifest_map = load_manifest_map()
    content = build_registry(manifest_map)
    if args.apply:
        REGISTRY.write_text(content, encoding="utf-8")
        print(f"wrote {len(manifest_map)} rows to {REGISTRY.relative_to(REPO_ROOT)}")
    else:
        print(content[:2000])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
