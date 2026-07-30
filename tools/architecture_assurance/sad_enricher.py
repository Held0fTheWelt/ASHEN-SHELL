"""Deepen Better Tomorrow SAD viewpoints from validated semantic evidence."""

from __future__ import annotations

from collections.abc import Mapping
import json
import os
from pathlib import Path
import re
from typing import Any

from .drift_claims import load_claim_catalog
from .manifest_builder import load_config
from .semantic_models import load_model_catalog, validate_model_catalog


SCHEMA_VERSION = "bt.sad_semantic_enrichment.v1"
_SECTIONS = (3, 5, 6, 7, 8, 9, 11)


def _table(value: Any) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ").strip()


def _link(from_path: Path, repo_relative: str, repo_root: Path) -> str:
    target = repo_root / repo_relative
    return Path(os.path.relpath(target, from_path.parent)).as_posix()


def _source(
    sad_path: Path,
    anchor: str,
    repo_root: Path,
) -> str:
    return f"[`{anchor}`]({_link(sad_path, anchor, repo_root)})"


def _view_link(
    sad_path: Path,
    view: Mapping[str, Any],
    repo_root: Path,
) -> str:
    companion = str(Path(str(view["path"])).with_suffix(".md").as_posix())
    return f"[{view['title']}]({_link(sad_path, companion, repo_root)})"


def _marker(section: int, content: str) -> str:
    return (
        f"<!-- BEGIN BT-SEMANTIC-DEPTH:{section} -->\n"
        f"{content.rstrip()}\n"
        f"<!-- END BT-SEMANTIC-DEPTH:{section} -->"
    )


def _upsert_section(text: str, section: int, content: str) -> str:
    block_pattern = re.compile(
        rf"\n?<!-- BEGIN BT-SEMANTIC-DEPTH:{section} -->.*?"
        rf"<!-- END BT-SEMANTIC-DEPTH:{section} -->\n?",
        re.DOTALL,
    )
    text = block_pattern.sub("\n", text)
    heading = re.search(rf"^## {section}\..*$", text, re.MULTILINE)
    if heading is None:
        raise ValueError(f"SAD lacks arc42 section {section}")
    next_heading = re.search(
        rf"^## {section + 1}\..*$",
        text[heading.end() :],
        re.MULTILINE,
    )
    insertion = (
        len(text)
        if next_heading is None
        else heading.end() + next_heading.start()
    )
    before = text[:insertion].rstrip()
    after = text[insertion:].lstrip("\n")
    return before + "\n\n" + _marker(section, content) + "\n\n" + after


def _context_block(
    model: Mapping[str, Any],
    sad_path: Path,
    repo_root: Path,
) -> str:
    context_views = [
        view for view in model["views"] if view["kind"] == "context"
    ]
    rows = [
        "### Evidence-grounded scope and authority",
        "",
        str(model["summary"]),
        "",
        f"**Authority rule:** {model['authority']}",
        "",
        "**Git/archaeology scope:** "
        + ", ".join(f"`{root}`" for root in model["history_roots"]),
        "",
        "| Context concern | Model | Boundary statement |",
        "| --- | --- | --- |",
    ]
    for view in context_views:
        rows.append(
            f"| {_table(view['concern'])} | "
            f"{_view_link(sad_path, view, repo_root)} | "
            f"{_table(model['authority'])} |"
        )
    if not context_views:
        rows.append(
            "| No separate context model | Covered by the parent topology | "
            "No independent system boundary is claimed. |"
        )
    rows.extend(
        [
            "",
            "Historical MVP and work-order material is classified evidence, "
            "not an authority source. Current code and accepted decisions win; "
            "conflicts remain explicit until a target decision is accepted.",
        ]
    )
    return "\n".join(rows)


def _building_block(
    model: Mapping[str, Any],
    sad_path: Path,
    repo_root: Path,
) -> str:
    rows = [
        "### Source-bound building-block catalog",
        "",
        "Each block has one stated responsibility, an interaction or ownership "
        "contract, and a current source anchor. The list is individualized for "
        "this scope; it is not derived from a fixed diagram count.",
        "",
        "| Block | Kind | Responsibility | Contract | Source |",
        "| --- | --- | --- | --- | --- |",
    ]
    for element_id, element in sorted(
        model["elements"].items(),
        key=lambda item: (
            str(item[1].get("type", "")),
            str(item[1].get("name", "")),
        ),
    ):
        rows.append(
            f"| {_table(element['name'])} (`{element_id}`) | "
            f"`{element.get('type', 'component')}` | "
            f"{_table(element['responsibility'])} | "
            f"{_table(element['contract'])} | "
            f"{_source(sad_path, str(element['anchor']), repo_root)} |"
        )
    return "\n".join(rows)


def _runtime_block(
    model: Mapping[str, Any],
    sad_path: Path,
    repo_root: Path,
) -> str:
    dynamic = [
        view
        for view in model["views"]
        if view["kind"] in {"activity", "sequence", "state", "usecase"}
    ]
    rows = [
        "### Dynamic viewpoint suite",
        "",
        "| Runtime concern | Viewpoint | Model | Modeled interactions |",
        "| --- | --- | --- | ---: |",
    ]
    for view in dynamic:
        rows.append(
            f"| {_table(view['concern'])} | `{view['kind']}` | "
            f"{_view_link(sad_path, view, repo_root)} | "
            f"{len(view['relationships'])} |"
        )
    if not dynamic:
        rows.append(
            "| No independent runtime behavior | `n/a` | Parent runtime view | 0 |"
        )
    rows.extend(
        [
            "",
            "The ordered sequence/activity relationships and state transitions "
            "are validated against the catalog. Generic arrows such as "
            "\"evidence for boundary\" are not accepted as runtime semantics.",
        ]
    )
    return "\n".join(rows)


def _deployment_block(
    model: Mapping[str, Any],
    sad_path: Path,
    repo_root: Path,
) -> str:
    deployment = [
        view for view in model["views"] if view["kind"] == "deployment"
    ]
    rows = [
        "### Deployment and operational boundary evidence",
        "",
    ]
    if deployment:
        rows.extend(
            [
                "| Concern | Model | Nodes / stores |",
                "| --- | --- | --- |",
            ]
        )
        for view in deployment:
            names = [
                model["elements"][element_id]["name"]
                for element_id in view["elements"]
            ]
            rows.append(
                f"| {_table(view['concern'])} | "
                f"{_view_link(sad_path, view, repo_root)} | "
                f"{', '.join(_table(name) for name in names)} |"
            )
    else:
        rows.extend(
            [
                "This scope does not claim an independently deployable runtime. "
                "Its deployment effect is expressed through the owning systems "
                "and the following implementation roots:",
                "",
            ]
        )
        rows.extend(f"- `{root}`" for root in model["history_roots"])
    rows.extend(
        [
            "",
            "A deployment boundary is not inferred from a directory. Process, "
            "store, transport and trust contracts must be named by a deployment "
            "view or delegated to an owning SAD.",
        ]
    )
    return "\n".join(rows)


def _crosscutting_block(
    model: Mapping[str, Any],
    sad_path: Path,
    repo_root: Path,
) -> str:
    selected: set[str] = set()
    for view in model["views"]:
        if view["kind"] in {"component", "container", "data", "class"}:
            selected.update(str(value) for value in view["relationships"])
    rows = [
        "### Explicit interaction and dependency contracts",
        "",
        "| From | To | Semantics | Contract | Evidence |",
        "| --- | --- | --- | --- | --- |",
    ]
    for relation_id in sorted(selected):
        relation = model["relationships"][relation_id]
        source = model["elements"].get(relation["from"], {}).get(
            "name", relation["from"]
        )
        target = model["elements"].get(relation["to"], {}).get(
            "name", relation["to"]
        )
        anchor = str(relation.get("anchor", "")).strip()
        evidence = (
            _source(sad_path, anchor, repo_root)
            if anchor
            else "Contract-only boundary"
        )
        rows.append(
            f"| {_table(source)} | {_table(target)} | "
            f"{_table(relation['label'])} | "
            f"{_table(relation['contract'])} | {evidence} |"
        )
    if not selected:
        rows.append(
            "| Parent scope | This scope | delegated concern | "
            "No independent crosscutting contract | Parent SAD |"
        )
    return "\n".join(rows)


def _decision_view_block(
    model: Mapping[str, Any],
    sad_path: Path,
    repo_root: Path,
) -> str:
    rows = [
        "### Decision-to-view correspondence",
        "",
        "| Decision(s) | Concern | Viewpoint | Model |",
        "| --- | --- | --- | --- |",
    ]
    for view in model["views"]:
        decisions = ", ".join(f"`{value}`" for value in view.get(
            "decisions", []
        )) or "Scope-level"
        rows.append(
            f"| {decisions} | {_table(view['concern'])} | "
            f"`{view['kind']}` | {_view_link(sad_path, view, repo_root)} |"
        )
    rows.extend(
        [
            "",
            "The correspondence is intentionally many-to-many: one decision "
            "may require structural, dynamic, data and deployment evidence, and "
            "one model may make several decisions analyzable together.",
        ]
    )
    return "\n".join(rows)


def _matches_roots(anchor: str, roots: list[str]) -> bool:
    return any(
        anchor == root
        or anchor.startswith(root.rstrip("/") + "/")
        or root.startswith(anchor.rstrip("/") + "/")
        for root in roots
    )


def _risk_block(
    subsystem_id: str,
    model: Mapping[str, Any],
    sad_path: Path,
    repo_root: Path,
    git_item: Mapping[str, Any] | None,
    claims: list[Mapping[str, Any]],
) -> str:
    rows = [
        "### Git-grounded drift profile",
        "",
        str(model["drift_focus"]),
        "",
    ]
    if git_item:
        recent = git_item["recent"]
        rows.extend(
            [
                "| Tracked files | Lifetime commits | Recent path touches | "
                "Recent renames |",
                "| ---: | ---: | ---: | ---: |",
                f"| {git_item['tracked_file_count']} | "
                f"{git_item['lifetime_commit_count']} | "
                f"{recent['path_touches']} | {recent['renames']} |",
                "",
            ]
        )
    roots = [str(value) for value in model["history_roots"]]
    related = [
        claim
        for claim in claims
        if any(
            _matches_roots(str(anchor), roots)
            for anchor in claim["current_evidence"]
        )
    ]
    rows.extend(
        [
            "| Drift claim | Status | Concern | Target direction |",
            "| --- | --- | --- | --- |",
        ]
    )
    for claim in related:
        rows.append(
            f"| `{claim['id']}` | `{claim['status']}` | "
            f"{_table(claim['concern'])} | {_table(claim['target'])} |"
        )
    if not related:
        rows.append(
            "| Scope-specific watch | `open_target` | "
            "No global claim currently maps to this root. | "
            "Keep source-bound views and review on structural Git changes. |"
        )
    baseline = _link(
        sad_path,
        "docs/architecture/evidence/architecture-drift-baseline.md",
        repo_root,
    )
    reconciliation = _link(
        sad_path,
        "docs/architecture/evidence/architecture-drift-reconciliation.md",
        repo_root,
    )
    rows.extend(
        [
            "",
            f"[Git/archaeology baseline]({baseline}) · "
            f"[Drift reconciliation and target directions]({reconciliation})",
            "",
            "These entries are review inputs, not automatic design decisions. "
            "Conflicting/open items close only through accepted target decisions "
            "and the listed behavioral evidence.",
        ]
    )
    return "\n".join(rows)


def enrich_sads(
    config_path: Path,
    repo_root: Path,
    *,
    dry_run: bool = False,
) -> dict[str, Any]:
    config = load_config(config_path)
    catalog = load_model_catalog(repo_root / str(config["model_catalog"]))
    findings = validate_model_catalog(catalog, repo_root)
    if findings:
        raise ValueError("semantic model catalog must validate before SAD enrichment")
    claims = load_claim_catalog(repo_root / str(config["drift_claim_catalog"]))[
        "claims"
    ]
    evidence_path = repo_root / str(config["drift_evidence_json"])
    evidence = (
        json.loads(evidence_path.read_text(encoding="utf-8-sig"))
        if evidence_path.is_file()
        else {"subsystems": []}
    )
    git_by_id = {
        item["subsystem"]: item for item in evidence.get("subsystems", [])
    }
    by_id = {
        str(item["id"]): item for item in config["subsystems"]
    }
    actions: list[dict[str, str]] = []
    for subsystem_id, model in catalog["subsystems"].items():
        sad_path = repo_root / str(by_id[subsystem_id]["sad_path"])
        original = sad_path.read_text(encoding="utf-8-sig")
        content = original
        blocks = {
            3: _context_block(model, sad_path, repo_root),
            5: _building_block(model, sad_path, repo_root),
            6: _runtime_block(model, sad_path, repo_root),
            7: _deployment_block(model, sad_path, repo_root),
            8: _crosscutting_block(model, sad_path, repo_root),
            9: _decision_view_block(model, sad_path, repo_root),
            11: _risk_block(
                subsystem_id,
                model,
                sad_path,
                repo_root,
                git_by_id.get(subsystem_id),
                claims,
            ),
        }
        for section in _SECTIONS:
            content = _upsert_section(content, section, blocks[section])
        content = content.rstrip() + "\n"
        changed = content != original
        if changed and not dry_run:
            sad_path.write_text(content, encoding="utf-8", newline="\n")
        actions.append(
            {
                "subsystem": subsystem_id,
                "path": sad_path.relative_to(repo_root).as_posix(),
                "action": (
                    "would_write"
                    if dry_run and changed
                    else "write"
                    if changed
                    else "unchanged"
                ),
            }
        )
    return {
        "schema_version": SCHEMA_VERSION,
        "dry_run": dry_run,
        "sections": list(_SECTIONS),
        "actions": actions,
    }
