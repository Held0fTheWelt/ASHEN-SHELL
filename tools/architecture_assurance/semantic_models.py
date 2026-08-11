"""Semantic, source-bound UML models for Better Tomorrow."""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping
import json
import os
from pathlib import Path
import re
from typing import Any


MODEL_CATALOG_SCHEMA_VERSION = "bt.semantic_model_catalog.v1"
MODEL_REQUIREMENT_SCHEMA_VERSION = "bt.semantic_view_requirement.v1"
_SUPPORTED_KINDS = {
    "activity",
    "class",
    "component",
    "container",
    "context",
    "data",
    "deployment",
    "sequence",
    "state",
    "usecase",
}


class SemanticModelError(ValueError):
    """Raised when a semantic model would fabricate or misrepresent a view."""


def load_model_catalog(path: Path) -> dict[str, Any]:
    catalog = json.loads(path.read_text(encoding="utf-8-sig"))
    if catalog.get("schema_version") != MODEL_CATALOG_SCHEMA_VERSION:
        raise SemanticModelError("unsupported Better Tomorrow model catalog")
    if not isinstance(catalog.get("subsystems"), Mapping):
        raise SemanticModelError("model catalog requires subsystem mappings")
    return catalog


def _safe(value: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_]", "_", value)
    return cleaned if cleaned and not cleaned[0].isdigit() else f"M_{cleaned}"


def _escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def _relative_link(anchor: str, destination: Path, repo_root: Path) -> str:
    target = repo_root / anchor
    return Path(os.path.relpath(target, destination.parent)).as_posix()


def _resolved_view(
    subsystem_id: str,
    model: Mapping[str, Any],
    view: Mapping[str, Any],
) -> dict[str, Any]:
    elements = model.get("elements", {})
    relationships = model.get("relationships", {})
    if not isinstance(elements, Mapping) or not isinstance(relationships, Mapping):
        raise SemanticModelError(f"{subsystem_id}: elements/relationships must map ids")
    selected_elements: list[dict[str, Any]] = []
    for element_id in view.get("elements", []):
        if element_id not in elements:
            raise SemanticModelError(
                f"{subsystem_id}:{view.get('id')}: unknown element {element_id}"
            )
        selected_elements.append({"id": element_id, **elements[element_id]})
    selected_relationships: list[dict[str, Any]] = []
    for relationship_id in view.get("relationships", []):
        if relationship_id not in relationships:
            raise SemanticModelError(
                f"{subsystem_id}:{view.get('id')}: unknown relationship "
                f"{relationship_id}"
            )
        selected_relationships.append(
            {"id": relationship_id, **relationships[relationship_id]}
        )
    return {
        **view,
        "elements_resolved": selected_elements,
        "relationships_resolved": selected_relationships,
    }


def validate_model_catalog(
    catalog: Mapping[str, Any],
    repo_root: Path,
) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    for subsystem_id, model in catalog["subsystems"].items():
        views = model.get("views", [])
        if not views:
            findings.append(
                {
                    "subsystem": str(subsystem_id),
                    "view": "",
                    "error": "subsystem has no semantic views",
                }
            )
            continue
        seen_paths: set[str] = set()
        for raw_view in views:
            view_id = str(raw_view.get("id", ""))
            kind = str(raw_view.get("kind", ""))
            path = str(raw_view.get("path", ""))
            concern = str(raw_view.get("concern", "")).strip()
            if not view_id or kind not in _SUPPORTED_KINDS or not path or not concern:
                findings.append(
                    {
                        "subsystem": str(subsystem_id),
                        "view": view_id,
                        "error": "view requires id, supported kind, path and concern",
                    }
                )
                continue
            if path in seen_paths:
                findings.append(
                    {
                        "subsystem": str(subsystem_id),
                        "view": view_id,
                        "error": f"duplicate view path: {path}",
                    }
                )
            seen_paths.add(path)
            try:
                view = _resolved_view(str(subsystem_id), model, raw_view)
            except SemanticModelError as exc:
                findings.append(
                    {
                        "subsystem": str(subsystem_id),
                        "view": view_id,
                        "error": str(exc),
                    }
                )
                continue
            element_ids = {
                str(element["id"]) for element in view["elements_resolved"]
            }
            for element in view["elements_resolved"]:
                missing = [
                    key
                    for key in ("name", "responsibility", "contract", "anchor")
                    if not str(element.get(key, "")).strip()
                ]
                if missing:
                    findings.append(
                        {
                            "subsystem": str(subsystem_id),
                            "view": view_id,
                            "error": (
                                f"element {element['id']} lacks "
                                f"{', '.join(missing)}"
                            ),
                        }
                    )
                anchor = repo_root / str(element.get("anchor", ""))
                if str(element.get("anchor", "")).strip() and not anchor.exists():
                    findings.append(
                        {
                            "subsystem": str(subsystem_id),
                            "view": view_id,
                            "error": f"missing source anchor: {element['anchor']}",
                        }
                    )
            for relationship in view["relationships_resolved"]:
                missing = [
                    key
                    for key in ("from", "to", "label", "contract")
                    if not str(relationship.get(key, "")).strip()
                ]
                if missing:
                    findings.append(
                        {
                            "subsystem": str(subsystem_id),
                            "view": view_id,
                            "error": (
                                f"relationship {relationship['id']} lacks "
                                f"{', '.join(missing)}"
                            ),
                        }
                    )
                    continue
                endpoints = {
                    str(relationship["from"]),
                    str(relationship["to"]),
                } - {"initial", "final"}
                if not endpoints.issubset(element_ids):
                    findings.append(
                        {
                            "subsystem": str(subsystem_id),
                            "view": view_id,
                            "error": (
                                f"relationship {relationship['id']} leaves "
                                "the selected view"
                            ),
                        }
                    )
                anchor_value = str(relationship.get("anchor", "")).strip()
                if anchor_value and not (repo_root / anchor_value).exists():
                    findings.append(
                        {
                            "subsystem": str(subsystem_id),
                            "view": view_id,
                            "error": f"missing edge anchor: {anchor_value}",
                        }
                    )
            if kind in {"sequence", "activity"} and element_ids:
                adjacency = {element_id: set() for element_id in element_ids}
                for relationship in view["relationships_resolved"]:
                    source = str(relationship.get("from", ""))
                    target = str(relationship.get("to", ""))
                    if source in adjacency and target in adjacency:
                        adjacency[source].add(target)
                        adjacency[target].add(source)
                reachable: set[str] = set()
                frontier = [next(iter(element_ids))]
                while frontier:
                    current = frontier.pop()
                    if current in reachable:
                        continue
                    reachable.add(current)
                    frontier.extend(adjacency[current] - reachable)
                disconnected = sorted(element_ids - reachable)
                if disconnected:
                    findings.append(
                        {
                            "subsystem": str(subsystem_id),
                            "view": view_id,
                            "error": (
                                "runtime view is not one connected path; "
                                "disconnected elements: " + ", ".join(disconnected)
                            ),
                        }
                    )
            if kind == "sequence":
                orders = [
                    relationship.get("order")
                    for relationship in view["relationships_resolved"]
                ]
                if any(
                    not isinstance(order, int) or order <= 0
                    for order in orders
                ):
                    findings.append(
                        {
                            "subsystem": str(subsystem_id),
                            "view": view_id,
                            "error": (
                                "sequence relationships require explicit "
                                "positive integer order values"
                            ),
                        }
                    )
                elif len(set(orders)) != len(orders):
                    findings.append(
                        {
                            "subsystem": str(subsystem_id),
                            "view": view_id,
                            "error": (
                                "sequence relationship order values must be "
                                "unique within the view"
                            ),
                        }
                    )
    return sorted(
        findings,
        key=lambda item: (item["subsystem"], item["view"], item["error"]),
    )


def view_requirements(
    catalog: Mapping[str, Any],
    subsystem_id: str,
) -> list[dict[str, Any]]:
    model = catalog["subsystems"].get(subsystem_id)
    if not isinstance(model, Mapping):
        raise SemanticModelError(f"missing semantic model for {subsystem_id}")
    requirements: list[dict[str, Any]] = []
    for raw_view in model.get("views", []):
        view = _resolved_view(subsystem_id, model, raw_view)
        anchors = sorted(
            {
                str(element["anchor"])
                for element in view["elements_resolved"]
            }
            | {
                str(relationship["anchor"])
                for relationship in view["relationships_resolved"]
                if relationship.get("anchor")
            }
        )
        requirements.append(
            {
                "schema_version": MODEL_REQUIREMENT_SCHEMA_VERSION,
                "id": view["id"],
                "level": view["kind"],
                "kind": view["kind"],
                "path": view["path"],
                "concern": view["concern"],
                "element_count": len(view["elements_resolved"]),
                "relationship_count": len(view["relationships_resolved"]),
                "anchors": anchors,
                "decisions": list(view.get("decisions", [])),
            }
        )
    return requirements


def _element_label(
    element: Mapping[str, Any],
    destination: Path,
    repo_root: Path,
) -> str:
    source = _relative_link(str(element["anchor"]), destination, repo_root)
    parts = [
        str(element["name"]),
        f"Responsibility: {element['responsibility']}",
        f"Contract: {element['contract']}",
        f"[[{source} source]]",
    ]
    drilldown = str(element.get("drilldown", "")).strip()
    if drilldown:
        parts.append(
            f"[[{_relative_link(drilldown, destination, repo_root)} drill-down]]"
        )
    return "\\n".join(_escape(part) for part in parts)


def _render_element(
    element: Mapping[str, Any],
    destination: Path,
    repo_root: Path,
    *,
    sequence: bool = False,
    view_kind: str = "",
) -> str:
    alias = _safe(str(element["id"]))
    label = _element_label(element, destination, repo_root)
    element_type = str(element.get("type", "component")).lower()
    if sequence:
        keyword = "actor" if element_type == "actor" else "participant"
        return f'{keyword} "{label}" as {alias}'
    if view_kind == "activity":
        element_type = "activity"
    elif view_kind in {"class", "data"} and element_type != "actor":
        element_type = "class"
    elif view_kind == "state":
        element_type = "state"
    elif view_kind == "usecase" and element_type != "actor":
        element_type = "usecase"
    keyword = {
        "actor": "actor",
        "activity": "activity",
        "artifact": "artifact",
        "class": "class",
        "component": "component",
        "container": "rectangle",
        "database": "database",
        "interface": "interface",
        "node": "node",
        "queue": "queue",
        "state": "state",
        "system": "rectangle",
        "usecase": "usecase",
    }.get(element_type, "rectangle")
    if keyword == "class":
        members = [str(member) for member in element.get("members", [])]
        body = "\n".join(f"  {_escape(member)}" for member in members)
        return f'class "{label}" as {alias} {{\n{body}\n}}'
    return f'{keyword} "{label}" as {alias}'


def _endpoint(value: str) -> str:
    if value in {"initial", "final"}:
        return "[*]"
    return _safe(value)


def _relationship_label(
    relationship: Mapping[str, Any],
    destination: Path,
    repo_root: Path,
    *,
    include_anchor: bool = True,
) -> str:
    parts = [
        str(relationship["label"]),
        f"contract: {relationship['contract']}",
    ]
    anchor = str(relationship.get("anchor", "")).strip()
    if anchor and include_anchor:
        parts.append(
            f"[[{_relative_link(anchor, destination, repo_root)} source]]"
        )
    return "\\n".join(_escape(part) for part in parts)


def _render_activity_body(
    view: Mapping[str, Any],
    destination: Path,
    repo_root: Path,
) -> list[str]:
    """Render a source-bound UML activity graph using PlantUML legacy syntax."""

    elements = {
        str(element["id"]): element
        for element in view["elements_resolved"]
    }
    element_order = [
        str(element["id"]) for element in view["elements_resolved"]
    ]
    relationships = sorted(
        view["relationships_resolved"],
        key=lambda item: (int(item.get("order", 0)), str(item["id"])),
    )
    incoming = Counter(
        str(relationship["to"])
        for relationship in relationships
        if str(relationship["to"]) in elements
    )
    outgoing = Counter(
        str(relationship["from"])
        for relationship in relationships
        if str(relationship["from"]) in elements
    )
    roots = [
        element_id
        for element_id in element_order
        if incoming[element_id] == 0
    ]
    if not roots and element_order:
        roots = [element_order[0]]

    lines: list[str] = []
    defined: set[str] = set()
    for element_id in roots:
        label = _element_label(elements[element_id], destination, repo_root)
        lines.append(f'(*) --> "{label}" as {_safe(element_id)}')
        defined.add(element_id)

    pending = list(relationships)
    while pending:
        progressed = False
        for relationship in list(pending):
            source_id = str(relationship["from"])
            target_id = str(relationship["to"])
            if source_id not in {"initial", "final"} and source_id not in defined:
                continue
            source = "(*)" if source_id in {"initial", "final"} else _safe(source_id)
            if target_id in {"initial", "final"}:
                target = "(*)"
            elif target_id in defined:
                target = _safe(target_id)
            else:
                target_label = _element_label(
                    elements[target_id],
                    destination,
                    repo_root,
                )
                target = f'"{target_label}" as {_safe(target_id)}'
                defined.add(target_id)
            label = _relationship_label(
                relationship,
                destination,
                repo_root,
                include_anchor=False,
            )
            lines.append(f"{source} -->[{label}] {target}")
            anchor = str(relationship.get("anchor", "")).strip()
            if anchor:
                source_link = _relative_link(anchor, destination, repo_root)
                lines.extend(
                    [
                        "note on link",
                        f"[[{_escape(source_link)} relationship source]]",
                        "end note",
                    ]
                )
            pending.remove(relationship)
            progressed = True
        if not progressed:
            unresolved = pending.pop(0)
            source_id = str(unresolved["from"])
            if source_id in elements and source_id not in defined:
                source_label = _element_label(
                    elements[source_id],
                    destination,
                    repo_root,
                )
                lines.append(
                    f'(*) --> "{source_label}" as {_safe(source_id)}'
                )
                defined.add(source_id)
                pending.insert(0, unresolved)

    for element_id in element_order:
        if element_id not in defined:
            label = _element_label(elements[element_id], destination, repo_root)
            lines.append(f'(*) --> "{label}" as {_safe(element_id)}')
            defined.add(element_id)
        if outgoing[element_id] == 0:
            lines.append(f"{_safe(element_id)} --> (*)")
    return lines


def render_semantic_view(
    subsystem_id: str,
    model: Mapping[str, Any],
    raw_view: Mapping[str, Any],
    repo_root: Path,
) -> str:
    view = _resolved_view(subsystem_id, model, raw_view)
    destination = repo_root / str(view["path"])
    kind = str(view["kind"])
    sequence = kind == "sequence"
    lines = [
        "@startuml",
        f"' bt-view-kind: {kind}",
        f"' bt-view-id: {subsystem_id}:{view['id']}",
        f"title {_escape(str(view['title']))}",
        "left to right direction" if not sequence else "",
        "skinparam shadowing false",
        "skinparam wrapWidth 220",
        "skinparam maxMessageSize 180",
        "",
    ]
    lines.extend(
        f"' bt-element-id: {_safe(str(element['id']))}"
        for element in view["elements_resolved"]
    )
    lines.append("")
    if kind == "activity":
        lines.extend(_render_activity_body(view, destination, repo_root))
    else:
        lines.extend(
            _render_element(
                element,
                destination,
                repo_root,
                sequence=sequence,
                view_kind=kind,
            )
            for element in view["elements_resolved"]
        )
    lines.append("")
    if kind != "activity":
        relationships = sorted(
            view["relationships_resolved"],
            key=lambda item: (int(item.get("order", 0)), str(item["id"])),
        )
        arrow = "->" if sequence else "-->"
        if kind in {"component", "container", "context", "data", "class"}:
            arrow = "..>"
        for relationship in relationships:
            source = _endpoint(str(relationship["from"]))
            target = _endpoint(str(relationship["to"]))
            style = str(relationship.get("style", arrow))
            label = _relationship_label(relationship, destination, repo_root)
            lines.append(f'{source} {style} {target} : "{label}"')
    lines.extend(
        [
            "",
            "legend bottom",
            f"Viewpoint: {_escape(kind)}",
            f"Concern: {_escape(str(view['concern']))}",
            "Elements expose responsibility, contract and source anchor.",
            "Edges name the interaction or dependency contract.",
            "endlegend",
            "@enduml",
            "",
        ]
    )
    return "\n".join(line for line in lines if line is not None)


def render_view_companion(
    subsystem_id: str,
    model: Mapping[str, Any],
    raw_view: Mapping[str, Any],
) -> str:
    view = _resolved_view(subsystem_id, model, raw_view)
    puml_name = Path(str(view["path"])).name
    rows = [
        "# " + str(view["title"]),
        "",
        f"**Viewpoint:** `{view['kind']}`",
        f"**Concern:** {view['concern']}",
        "",
        f"[PlantUML source]({puml_name})",
        "",
        "## Modeled elements",
        "",
        "| Element | Responsibility | Contract | Source |",
        "| --- | --- | --- | --- |",
    ]
    for element in view["elements_resolved"]:
        rows.append(
            "| {name} | {responsibility} | {contract} | "
            "[`{anchor}`]({source}) |".format(
                name=element["name"],
                responsibility=element["responsibility"],
                contract=element["contract"],
                anchor=element["anchor"],
                source=Path(
                    os.path.relpath(
                        Path(str(element["anchor"])),
                        Path(str(view["path"])).parent,
                    )
                ).as_posix(),
            )
        )
    rows.extend(
        [
            "",
            "## Modeled relationships",
            "",
            "| From | To | Semantics | Contract | Source |",
            "| --- | --- | --- | --- | --- |",
        ]
    )
    element_names = {
        str(element["id"]): str(element["name"])
        for element in view["elements_resolved"]
    }
    element_names.update({"initial": "Initial", "final": "Final"})
    for relationship in view["relationships_resolved"]:
        anchor = str(relationship.get("anchor", "")).strip()
        if anchor:
            source = Path(
                os.path.relpath(
                    Path(anchor),
                    Path(str(view["path"])).parent,
                )
            ).as_posix()
            source_cell = f"[`{anchor}`]({source})"
        else:
            source_cell = "catalog contract"
        rows.append(
            f"| {element_names[str(relationship['from'])]} | "
            f"{element_names[str(relationship['to'])]} | "
            f"{relationship['label']} | {relationship['contract']} | "
            f"{source_cell} |"
        )
    rows.extend(
        [
            "",
            "Generated deterministically from Better Tomorrow's semantic model "
            "catalog; edit the catalog, not this projection.",
            "",
        ]
    )
    return "\n".join(rows)


def render_package_readme(
    subsystem_id: str,
    model: Mapping[str, Any],
) -> str:
    package_path = Path(str(model["package_path"]))
    rows = [
        f"# {model['name']} architecture models",
        "",
        str(model["summary"]),
        "",
        f"**Architecture authority:** {model['authority']}",
        "",
        "## Viewpoint map",
        "",
        "| Concern | Viewpoint | Model | Decisions |",
        "| --- | --- | --- | --- |",
    ]
    for view in model["views"]:
        relative = Path(str(view["path"])).relative_to(package_path).with_suffix(
            ".md"
        )
        decisions = ", ".join(view.get("decisions", [])) or "—"
        rows.append(
            f"| {view['concern']} | `{view['kind']}` | "
            f"[{view['title']}]({relative.as_posix()}) | {decisions} |"
        )
    rows.extend(
        [
            "",
            "## Drift focus",
            "",
            str(model["drift_focus"]),
            "",
            "[Decision/view/source traceability](TRACEABILITY.md)",
            "",
        ]
    )
    return "\n".join(rows)


def render_traceability(
    subsystem_id: str,
    model: Mapping[str, Any],
) -> str:
    package_path = Path(str(model["package_path"]))
    rows = [
        f"# {model['name']} UML traceability",
        "",
        "| View | Kind | Decisions | Source anchors |",
        "| --- | --- | --- | --- |",
    ]
    for raw_view in model["views"]:
        view = _resolved_view(subsystem_id, model, raw_view)
        relative = Path(str(view["path"])).relative_to(package_path).with_suffix(
            ".md"
        )
        anchors = sorted(
            {str(element["anchor"]) for element in view["elements_resolved"]}
            | {
                str(relationship["anchor"])
                for relationship in view["relationships_resolved"]
                if relationship.get("anchor")
            }
        )
        anchor_links = ", ".join(f"`{anchor}`" for anchor in anchors)
        decisions = ", ".join(view.get("decisions", [])) or "—"
        rows.append(
            f"| [{view['title']}]({relative.as_posix()}) | "
            f"`{view['kind']}` | {decisions} | {anchor_links} |"
        )
    rows.extend(
        [
            "",
            "The table is a generated correspondence view. Source paths are "
            "validated before projection.",
            "",
        ]
    )
    return "\n".join(rows)
