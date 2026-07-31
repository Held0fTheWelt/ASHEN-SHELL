"""Source-bound drift edges and executable architecture invariants.

The drift-claim catalog explains *why* a concern matters.  This module adds the
machine-readable topology needed to fail CI when architecture authority splits
or a required field disappears from a modeled turn-envelope path.
"""

from __future__ import annotations

import ast
from collections import Counter
from collections.abc import Mapping
import json
import os
from pathlib import Path
import re
from typing import Any


SCHEMA_VERSION = "bt.architecture_drift_edge_catalog.v1"
REPORT_SCHEMA_VERSION = "bt.architecture_drift_edge_report.v1"
_ACTIVE_CLAIM_STATUSES = {"conflicting", "open_target"}
_EFFECTS = {
    "authoritative_write",
    "compatibility_delegate",
    "content_projection",
    "evidence_flow",
    "proposal_finalize",
    "proposal_flow",
    "read_only_constraint",
    "visible_projection",
}


def _display_path(path: Path, repo_root: Path) -> str:
    try:
        return path.relative_to(repo_root).as_posix()
    except ValueError:
        return path.as_posix()


def _dotted_name(node: ast.AST) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        prefix = _dotted_name(node.value)
        return f"{prefix}.{node.attr}" if prefix else node.attr
    return None


def _enclosing_symbol(
    node: ast.AST,
    parents: Mapping[ast.AST, ast.AST],
) -> str:
    current = node
    while current in parents:
        current = parents[current]
        if isinstance(current, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return current.name
    return "<module>"


def _store_attr_names(surface: Mapping[str, Any], call: str) -> set[str]:
    """Derive store attribute names used for alias detection."""
    attrs: set[str] = set()
    raw = surface.get("store_attrs")
    if isinstance(raw, list):
        attrs.update(str(item) for item in raw if str(item).strip())
    # From dotted call like self._session_store.save → _session_store
    parts = [part for part in call.split(".") if part]
    if len(parts) >= 2 and parts[-1] == "save":
        attrs.add(parts[-2])
    return {name for name in attrs if name}


def _collect_store_aliases(
    tree: ast.AST,
    *,
    store_attrs: set[str],
) -> dict[str, set[str]]:
    """Map local names to store attribute names within each enclosing function."""
    parents = {
        child: parent
        for parent in ast.walk(tree)
        for child in ast.iter_child_nodes(parent)
    }
    aliases: dict[str, set[str]] = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        target = node.targets[0]
        if not isinstance(target, ast.Name):
            continue
        value_name = _dotted_name(node.value)
        if not value_name:
            continue
        for attr in store_attrs:
            if value_name == attr or value_name.endswith(f".{attr}"):
                symbol = _enclosing_symbol(node, parents)
                aliases.setdefault(f"{symbol}:{target.id}", set()).add(attr)
    return aliases


def _is_surface_save_call(
    node: ast.Call,
    *,
    call: str,
    call_names: set[str],
    store_attrs: set[str],
    aliases: Mapping[str, set[str]],
    parents: Mapping[ast.AST, ast.AST],
) -> bool:
    dotted = _dotted_name(node.func)
    if dotted and dotted in call_names:
        return True
    # Bare function sink (e.g. _persist_session_to_database(...)).
    if (
        isinstance(node.func, ast.Name)
        and node.func.id in call_names
        and "." not in call
    ):
        return True
    # Alias: s = self._session_store; s.save(...)
    if (
        isinstance(node.func, ast.Attribute)
        and node.func.attr == "save"
        and isinstance(node.func.value, ast.Name)
    ):
        symbol = _enclosing_symbol(node, parents)
        key = f"{symbol}:{node.func.value.id}"
        if key in aliases and aliases[key] & store_attrs:
            return True
    # Generic *.store.save under route/adapter ban when configured via call suffix.
    if call.endswith(".store.save") and dotted and dotted.endswith(".store.save"):
        return True
    return False


def validate_authoritative_write_surfaces(
    catalog: Mapping[str, Any],
    *,
    repo_root: Path,
    catalog_path: str,
) -> list[dict[str, Any]]:
    """Resolve real Python sink callsites against their declared authority.

    Drift edges prevent a second *declared* writer.  This scan closes the more
    dangerous bypass where source code starts calling the known session-store
    sink without adding the corresponding architecture edge.

    Wave 2: matches primary call forms, optional aliases, and local store
    aliases (``s = self._session_store; s.save(...)``).
    """

    findings: list[dict[str, Any]] = []
    surfaces = catalog.get("write_surfaces")
    if not isinstance(surfaces, list) or not surfaces:
        return [
            _finding(
                "BT-DRIFT-EDGE-SCHEMA",
                "write_surfaces",
                "at least one source write-surface invariant is required",
                path=catalog_path,
            )
        ]
    authority_resources = {
        str(invariant.get("resource", ""))
        for invariant in catalog.get("authority_invariants", [])
        if isinstance(invariant, Mapping)
    }
    for surface in surfaces:
        if not isinstance(surface, Mapping):
            continue
        surface_id = str(surface.get("id", "write-surface"))
        resource = str(surface.get("resource", ""))
        call = str(surface.get("call", ""))
        roots = surface.get("scan_roots")
        allowed = surface.get("allowed_callsites")
        if (
            resource not in authority_resources
            or not call
            or not isinstance(roots, list)
            or not roots
            or not isinstance(allowed, list)
            or not allowed
        ):
            findings.append(
                _finding(
                    "BT-DRIFT-EDGE-SCHEMA",
                    surface_id,
                    "write surface requires a known resource, call, scan roots "
                    "and allowed callsites",
                    path=catalog_path,
                )
            )
            continue
        call_names = {call}
        raw_aliases = surface.get("call_aliases")
        if isinstance(raw_aliases, list):
            call_names.update(str(item) for item in raw_aliases if str(item).strip())
        store_attrs = _store_attr_names(surface, call)
        allowed_callsites = {
            (str(item.get("path", "")), str(item.get("symbol", "")))
            for item in allowed
            if isinstance(item, Mapping)
        }
        callsites: list[dict[str, Any]] = []
        scanned_paths: set[str] = set()
        for raw_root in roots:
            root = repo_root / str(raw_root)
            if not root.exists():
                findings.append(
                    _finding(
                        "BT-AUTHORITY-WRITE-SCAN",
                        surface_id,
                        f"write-surface scan root is missing: {raw_root}",
                        path=str(raw_root),
                    )
                )
                continue
            candidates = [root] if root.is_file() else sorted(root.rglob("*.py"))
            for path in candidates:
                relative = _display_path(path, repo_root)
                if relative in scanned_paths:
                    continue
                scanned_paths.add(relative)
                try:
                    tree = ast.parse(
                        path.read_text(encoding="utf-8-sig"),
                        filename=relative,
                    )
                except (OSError, SyntaxError, UnicodeError) as exc:
                    findings.append(
                        _finding(
                            "BT-AUTHORITY-WRITE-SCAN",
                            surface_id,
                            f"cannot inspect write surface: {exc}",
                            path=relative,
                        )
                    )
                    continue
                parents = {
                    child: parent
                    for parent in ast.walk(tree)
                    for child in ast.iter_child_nodes(parent)
                }
                aliases = _collect_store_aliases(tree, store_attrs=store_attrs)
                for node in ast.walk(tree):
                    if not isinstance(node, ast.Call):
                        continue
                    if not _is_surface_save_call(
                        node,
                        call=call,
                        call_names=call_names,
                        store_attrs=store_attrs,
                        aliases=aliases,
                        parents=parents,
                    ):
                        continue
                    callsites.append(
                        {
                            "path": relative,
                            "symbol": _enclosing_symbol(node, parents),
                            "line": int(getattr(node, "lineno", 1)),
                        }
                    )
        # Deduplicate identical path/symbol/line rows.
        unique_rows = {
            (row["path"], row["symbol"], row["line"]): row for row in callsites
        }
        callsites = list(unique_rows.values())
        minimum = int(surface.get("minimum_calls", 1))
        maximum = int(surface.get("maximum_calls", len(allowed_callsites) or 1))
        if len(callsites) < minimum:
            findings.append(
                _finding(
                    "BT-AUTHORITY-WRITE-MISSING",
                    surface_id,
                    f"source sink {call!r} has {len(callsites)} callsites; "
                    f"minimum is {minimum}",
                    path=catalog_path,
                )
            )
        if len(callsites) > maximum:
            findings.append(
                _finding(
                    "BT-AUTHORITY-WRITE-CONFLICT",
                    surface_id,
                    f"source sink {call!r} has {len(callsites)} callsites; "
                    f"maximum is {maximum}",
                    path=catalog_path,
                )
            )
        for callsite in callsites:
            signature = (str(callsite["path"]), str(callsite["symbol"]))
            if signature not in allowed_callsites:
                findings.append(
                    _finding(
                        "BT-AUTHORITY-WRITE-CALLSITE",
                        surface_id,
                        f"unauthorized live-session sink call in "
                        f"{callsite['symbol']} at line {callsite['line']}",
                        path=str(callsite["path"]),
                    )
                )
    return findings


def load_drift_edge_catalog(path: Path) -> dict[str, Any]:
    catalog = json.loads(path.read_text(encoding="utf-8-sig"))
    if catalog.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("unsupported architecture drift-edge catalog")
    return catalog


def _finding(
    rule_id: str,
    unit: str,
    message: str,
    *,
    path: str,
) -> dict[str, Any]:
    return {
        "rule_id": rule_id,
        "unit": unit,
        "message": message,
        "path": path,
    }


def _model_ref(
    value: Any,
    model_catalog: Mapping[str, Any],
) -> tuple[str, str] | None:
    if not isinstance(value, str) or ":" not in value:
        return None
    subsystem_id, element_id = value.split(":", 1)
    subsystem = model_catalog.get("subsystems", {}).get(subsystem_id)
    if not isinstance(subsystem, Mapping):
        return None
    elements = subsystem.get("elements", {})
    if not isinstance(elements, Mapping) or element_id not in elements:
        return None
    return subsystem_id, element_id


def _view_bound(
    model_ref: tuple[str, str],
    model_catalog: Mapping[str, Any],
) -> bool:
    subsystem_id, element_id = model_ref
    subsystem = model_catalog["subsystems"][subsystem_id]
    return any(
        element_id in view.get("elements", [])
        for view in subsystem.get("views", [])
    )


def _validate_projection(
    catalog: Mapping[str, Any],
    catalog_path: str,
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    projection = catalog.get("projection")
    if not isinstance(projection, Mapping):
        return [
            _finding(
                "BT-DRIFT-EDGE-SCHEMA",
                "projection",
                "projection must be an object",
                path=catalog_path,
            )
        ]
    for key, suffix in (("puml_path", ".puml"), ("markdown_path", ".md")):
        value = projection.get(key)
        if not isinstance(value, str) or not value.endswith(suffix):
            findings.append(
                _finding(
                    "BT-DRIFT-EDGE-SCHEMA",
                    f"projection:{key}",
                    f"{key} must be a repository-relative {suffix} path",
                    path=catalog_path,
                )
            )
    return findings


def _validate_edges(
    catalog: Mapping[str, Any],
    *,
    model_catalog: Mapping[str, Any],
    claim_catalog: Mapping[str, Any],
    repo_root: Path,
    catalog_path: str,
) -> tuple[dict[str, Mapping[str, Any]], list[dict[str, Any]]]:
    findings: list[dict[str, Any]] = []
    edges_by_id: dict[str, Mapping[str, Any]] = {}
    known_claims = {
        str(claim["id"]): str(claim["status"])
        for claim in claim_catalog.get("claims", [])
    }
    covered_claims: set[str] = set()
    raw_edges = catalog.get("edges")
    if not isinstance(raw_edges, list):
        return {}, [
            _finding(
                "BT-DRIFT-EDGE-SCHEMA",
                "edges",
                "edges must be a list",
                path=catalog_path,
            )
        ]
    for index, edge in enumerate(raw_edges):
        if not isinstance(edge, Mapping):
            findings.append(
                _finding(
                    "BT-DRIFT-EDGE-SCHEMA",
                    f"edge:{index}",
                    "edge must be an object",
                    path=catalog_path,
                )
            )
            continue
        edge_id = str(edge.get("id", "")).strip()
        if not edge_id or edge_id in edges_by_id:
            findings.append(
                _finding(
                    "BT-DRIFT-EDGE-SCHEMA",
                    edge_id or f"edge:{index}",
                    "edge id is missing or duplicated",
                    path=catalog_path,
                )
            )
            continue
        edges_by_id[edge_id] = edge
        effect = edge.get("effect")
        if effect not in _EFFECTS:
            findings.append(
                _finding(
                    "BT-DRIFT-EDGE-SCHEMA",
                    edge_id,
                    f"unsupported edge effect {effect!r}",
                    path=catalog_path,
                )
            )
        for endpoint in ("from", "to"):
            ref = _model_ref(edge.get(endpoint), model_catalog)
            if ref is None:
                findings.append(
                    _finding(
                        "BT-DRIFT-EDGE-REFERENCE",
                        edge_id,
                        f"{endpoint} does not resolve to a semantic-model element",
                        path=catalog_path,
                    )
                )
            elif not _view_bound(ref, model_catalog):
                findings.append(
                    _finding(
                        "BT-DRIFT-EDGE-REFERENCE",
                        edge_id,
                        f"{endpoint} element {edge[endpoint]} is absent from all UML views",
                        path=catalog_path,
                    )
                )
        anchor = edge.get("anchor")
        if not isinstance(anchor, str) or not (repo_root / anchor).is_file():
            findings.append(
                _finding(
                    "BT-DRIFT-EDGE-ANCHOR",
                    edge_id,
                    "edge requires an existing repository source anchor",
                    path=str(anchor or catalog_path),
                )
            )
        claims = edge.get("claim_ids")
        if not isinstance(claims, list) or not claims:
            findings.append(
                _finding(
                    "BT-DRIFT-EDGE-SCHEMA",
                    edge_id,
                    "edge requires at least one drift claim id",
                    path=catalog_path,
                )
            )
        else:
            for claim_id in claims:
                if claim_id not in known_claims:
                    findings.append(
                        _finding(
                            "BT-DRIFT-EDGE-REFERENCE",
                            edge_id,
                            f"unknown drift claim {claim_id!r}",
                            path=catalog_path,
                        )
                    )
                else:
                    covered_claims.add(str(claim_id))
        carries = edge.get("carries", [])
        if (
            not isinstance(carries, list)
            or any(not isinstance(field, str) or not field.strip() for field in carries)
            or len(carries) != len(set(carries))
        ):
            findings.append(
                _finding(
                    "BT-DRIFT-EDGE-SCHEMA",
                    edge_id,
                    "carries must be a unique list of non-empty field names",
                    path=catalog_path,
                )
            )
        if effect == "authoritative_write" and not isinstance(
            edge.get("write_resource"), str
        ):
            findings.append(
                _finding(
                    "BT-DRIFT-EDGE-SCHEMA",
                    edge_id,
                    "authoritative_write requires write_resource",
                    path=catalog_path,
                )
            )
    required_claims = {
        claim_id
        for claim_id, status in known_claims.items()
        if status in _ACTIVE_CLAIM_STATUSES
    }
    for claim_id in sorted(required_claims - covered_claims):
        findings.append(
            _finding(
                "BT-DRIFT-EDGE-COVERAGE",
                claim_id,
                "active drift claim has no machine-readable edge",
                path=catalog_path,
            )
        )
    return edges_by_id, findings


def _validate_authority(
    catalog: Mapping[str, Any],
    edges_by_id: Mapping[str, Mapping[str, Any]],
    catalog_path: str,
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    invariants = catalog.get("authority_invariants")
    if not isinstance(invariants, list) or not invariants:
        return [
            _finding(
                "BT-DRIFT-EDGE-SCHEMA",
                "authority_invariants",
                "at least one authority invariant is required",
                path=catalog_path,
            )
        ]
    for invariant in invariants:
        if not isinstance(invariant, Mapping):
            continue
        invariant_id = str(invariant.get("id", "authority"))
        resource = str(invariant.get("resource", ""))
        writers = [
            edge
            for edge in edges_by_id.values()
            if edge.get("effect") == "authoritative_write"
            and edge.get("write_resource") == resource
        ]
        if not writers:
            findings.append(
                _finding(
                    "BT-AUTHORITY-WRITE-MISSING",
                    invariant_id,
                    f"resource {resource!r} has no authoritative write edge",
                    path=catalog_path,
                )
            )
            continue
        if len(writers) > 1:
            edge_ids = ", ".join(sorted(str(edge["id"]) for edge in writers))
            findings.append(
                _finding(
                    "BT-AUTHORITY-WRITE-CONFLICT",
                    invariant_id,
                    f"resource {resource!r} has competing write paths: {edge_ids}",
                    path=catalog_path,
                )
            )
        expected_writer = invariant.get("expected_writer")
        expected_sink = invariant.get("expected_sink")
        for edge in writers:
            if edge.get("from") != expected_writer or edge.get("to") != expected_sink:
                findings.append(
                    _finding(
                        "BT-AUTHORITY-WRITER",
                        str(edge["id"]),
                        "authoritative writer/sink differs from the declared owner",
                        path=str(edge.get("anchor") or catalog_path),
                    )
                )
            if edge.get("from") in invariant.get("forbidden_writers", []):
                findings.append(
                    _finding(
                        "BT-AUTHORITY-WRITE-CONFLICT",
                        str(edge["id"]),
                        f"forbidden writer {edge['from']} targets {resource}",
                        path=str(edge.get("anchor") or catalog_path),
                    )
                )
    return findings


def _validate_field_proofs(
    *,
    invariant_id: str,
    field: Mapping[str, Any],
    repo_root: Path,
    catalog_path: str,
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    field_name = str(field.get("name", ""))
    proofs = field.get("source_proofs")
    if not isinstance(proofs, list) or len(proofs) < 2:
        return [
            _finding(
                "BT-ENVELOPE-FIELD-PROOF",
                f"{invariant_id}:{field_name}",
                "field requires at least two source proofs across its flow",
                path=catalog_path,
            )
        ]
    for proof in proofs:
        if not isinstance(proof, Mapping):
            continue
        raw_path = str(proof.get("path", ""))
        token = str(proof.get("token", ""))
        path = repo_root / raw_path
        if not raw_path or not path.is_file():
            findings.append(
                _finding(
                    "BT-ENVELOPE-FIELD-PROOF",
                    f"{invariant_id}:{field_name}",
                    "field proof path is missing",
                    path=raw_path or catalog_path,
                )
            )
            continue
        if not token or token not in path.read_text(encoding="utf-8-sig"):
            findings.append(
                _finding(
                    "BT-ENVELOPE-FIELD-PROOF",
                    f"{invariant_id}:{field_name}",
                    f"proof token {token!r} is absent",
                    path=raw_path,
                )
            )
    return findings


def _validate_envelopes(
    catalog: Mapping[str, Any],
    edges_by_id: Mapping[str, Mapping[str, Any]],
    *,
    repo_root: Path,
    catalog_path: str,
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    invariants = catalog.get("envelope_invariants")
    if not isinstance(invariants, list) or not invariants:
        return [
            _finding(
                "BT-DRIFT-EDGE-SCHEMA",
                "envelope_invariants",
                "at least one envelope invariant is required",
                path=catalog_path,
            )
        ]
    for invariant in invariants:
        if not isinstance(invariant, Mapping):
            continue
        invariant_id = str(invariant.get("id", "envelope"))
        path_ids = invariant.get("path")
        if (
            not isinstance(path_ids, list)
            or not path_ids
            or len(path_ids) != len(set(path_ids))
        ):
            findings.append(
                _finding(
                    "BT-DRIFT-EDGE-SCHEMA",
                    invariant_id,
                    "envelope path must be a non-empty unique edge list",
                    path=catalog_path,
                )
            )
            continue
        missing = [edge_id for edge_id in path_ids if edge_id not in edges_by_id]
        if missing:
            findings.append(
                _finding(
                    "BT-DRIFT-EDGE-REFERENCE",
                    invariant_id,
                    "envelope references unknown edges: " + ", ".join(missing),
                    path=catalog_path,
                )
            )
            continue
        path_edges = [edges_by_id[edge_id] for edge_id in path_ids]
        for left, right in zip(path_edges, path_edges[1:]):
            if left.get("to") != right.get("from"):
                findings.append(
                    _finding(
                        "BT-ENVELOPE-DISCONNECTED",
                        invariant_id,
                        f"{left['id']} ends at {left.get('to')}, "
                        f"but {right['id']} starts at {right.get('from')}",
                        path=catalog_path,
                    )
                )
        positions = {edge_id: index for index, edge_id in enumerate(path_ids)}
        fields = invariant.get("fields")
        if not isinstance(fields, list) or not fields:
            findings.append(
                _finding(
                    "BT-DRIFT-EDGE-SCHEMA",
                    invariant_id,
                    "envelope requires fields",
                    path=catalog_path,
                )
            )
            continue
        for field in fields:
            if not isinstance(field, Mapping):
                continue
            field_name = str(field.get("name", "")).strip()
            introduced = field.get("introduced_at")
            through = field.get("required_through")
            if (
                not field_name
                or introduced not in positions
                or through not in positions
                or positions[introduced] > positions[through]
            ):
                findings.append(
                    _finding(
                        "BT-DRIFT-EDGE-SCHEMA",
                        f"{invariant_id}:{field_name or 'field'}",
                        "field range must resolve in forward envelope order",
                        path=catalog_path,
                    )
                )
                continue
            for edge_id in path_ids[
                positions[introduced] : positions[through] + 1
            ]:
                edge = edges_by_id[edge_id]
                if field_name not in edge.get("carries", []):
                    findings.append(
                        _finding(
                            "BT-ENVELOPE-FIELD-LOSS",
                            f"{invariant_id}:{field_name}",
                            f"{edge_id} drops required field {field_name!r}",
                            path=str(edge.get("anchor") or catalog_path),
                        )
                    )
            findings.extend(
                _validate_field_proofs(
                    invariant_id=invariant_id,
                    field=field,
                    repo_root=repo_root,
                    catalog_path=catalog_path,
                )
            )
    return findings


def validate_drift_edge_catalog(
    catalog: Mapping[str, Any],
    *,
    model_catalog: Mapping[str, Any],
    claim_catalog: Mapping[str, Any],
    repo_root: Path,
    catalog_path: str,
) -> list[dict[str, Any]]:
    findings = _validate_projection(catalog, catalog_path)
    edges_by_id, edge_findings = _validate_edges(
        catalog,
        model_catalog=model_catalog,
        claim_catalog=claim_catalog,
        repo_root=repo_root,
        catalog_path=catalog_path,
    )
    findings.extend(edge_findings)
    findings.extend(_validate_authority(catalog, edges_by_id, catalog_path))
    findings.extend(
        validate_authoritative_write_surfaces(
            catalog,
            repo_root=repo_root,
            catalog_path=catalog_path,
        )
    )
    findings.extend(
        _validate_envelopes(
            catalog,
            edges_by_id,
            repo_root=repo_root,
            catalog_path=catalog_path,
        )
    )
    return sorted(
        findings,
        key=lambda item: (
            str(item["rule_id"]),
            str(item["unit"]),
            str(item["message"]),
        ),
    )


def _alias(model_ref: str) -> str:
    return "n_" + re.sub(r"[^A-Za-z0-9_]", "_", model_ref)


def _element(
    model_ref: str,
    model_catalog: Mapping[str, Any],
) -> Mapping[str, Any]:
    subsystem_id, element_id = model_ref.split(":", 1)
    return model_catalog["subsystems"][subsystem_id]["elements"][element_id]


def render_drift_edge_puml(
    catalog: Mapping[str, Any],
    model_catalog: Mapping[str, Any],
) -> str:
    edges = list(catalog["edges"])
    node_refs = sorted(
        {
            str(edge[endpoint])
            for edge in edges
            for endpoint in ("from", "to")
        }
    )
    lines = [
        "@startuml",
        "' bt-view-kind: drift-topology",
        "' bt-view-id: project:runtime-authority-and-envelope",
        "title Better Tomorrow - Runtime authority and envelope drift edges",
        "left to right direction",
        "skinparam shadowing false",
        "skinparam wrapWidth 220",
        "",
    ]
    for model_ref in node_refs:
        element = _element(model_ref, model_catalog)
        label = (
            f"{element['name']}\\n[{model_ref}]\\n"
            f"Responsibility: {element['responsibility']}"
        ).replace('"', '\\"')
        lines.append(f'component "{label}" as {_alias(model_ref)}')
    lines.append("")
    styles = {
        "authoritative_write": "-[#red,bold]->",
        "compatibility_delegate": "-[#orange,dashed]->",
        "content_projection": "-[#darkgreen]->",
        "evidence_flow": "-[#gray]->",
        "proposal_finalize": "-[#purple,dashed]->",
        "proposal_flow": "-[#blue]->",
        "read_only_constraint": "-[#darkgreen,dashed]->",
        "visible_projection": "-[#teal]->",
    }
    for edge in edges:
        carries = ", ".join(edge.get("carries", [])) or "no envelope fields"
        label = (
            f"{edge['id']}\\n{edge['label']}\\n"
            f"effect: {edge['effect']}\\ncontract: {edge['contract']}\\n"
            f"carries: {carries}"
        ).replace('"', '\\"')
        lines.append(
            f"{_alias(str(edge['from']))} {styles[str(edge['effect'])]} "
            f'{_alias(str(edge["to"]))} : "{label}"'
        )
    authority_by_resource = {
        str(invariant["resource"]): invariant
        for invariant in catalog.get("authority_invariants", [])
    }
    for surface in catalog.get("write_surfaces", []):
        invariant = authority_by_resource.get(str(surface.get("resource", "")))
        if not invariant:
            continue
        allowed = ", ".join(
            f"{item['path']}::{item['symbol']}"
            for item in surface.get("allowed_callsites", [])
        )
        lines.extend(
            [
                f"note bottom of {_alias(str(invariant['expected_sink']))}",
                f"Source sink guard: {surface['call']}",
                f"Allowed callsite: {allowed}",
                "end note",
            ]
        )
    lines.extend(
        [
            "",
            "legend bottom",
            "Red bold: the sole authoritative live-session write",
            "Orange dashed: compatibility delegation without write authority",
            "Blue/purple: proposal flow and proposal-only finalization",
            "Green: immutable content projection or read-only constraint",
            "Teal: committed player-visible projection",
            "Gray: evidence and quality flow",
            "endlegend",
            "@enduml",
            "",
        ]
    )
    return "\n".join(lines)


def _relative_link(source: str, destination: Path) -> str:
    return Path(
        os.path.relpath(Path(source), destination.parent)
    ).as_posix()


def render_drift_edge_markdown(catalog: Mapping[str, Any]) -> str:
    destination = Path(str(catalog["projection"]["markdown_path"]))
    rows = [
        "# Better Tomorrow runtime authority and envelope drift edges",
        "",
        "This projection is generated from the machine-readable drift-edge "
        "catalog. Edit the catalog, never this file.",
        "",
        "[PlantUML source](runtime-authority-and-envelope.puml)",
        "",
        "## Drift edges",
        "",
        "| Edge | From | To | Effect | Claims | Carried fields | Source |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for edge in catalog["edges"]:
        fields = ", ".join(f"`{field}`" for field in edge.get("carries", [])) or "—"
        claims = ", ".join(f"`{claim}`" for claim in edge["claim_ids"])
        source = _relative_link(str(edge["anchor"]), destination)
        rows.append(
            f"| `{edge['id']}` | `{edge['from']}` | `{edge['to']}` | "
            f"`{edge['effect']}` | {claims} | {fields} | "
            f"[`{edge['anchor']}`]({source}) |"
        )
    rows.extend(["", "## Authority invariants", ""])
    for invariant in catalog["authority_invariants"]:
        rows.append(
            f"- `{invariant['id']}`: `{invariant['expected_writer']}` is the "
            f"only writer of `{invariant['resource']}` and writes through "
            f"`{invariant['expected_sink']}`."
        )
    rows.extend(["", "## Source write-surface guards", ""])
    rows.append("| Guard | Resource | Sink call | Allowed callsites |")
    rows.append("| --- | --- | --- | --- |")
    for surface in catalog.get("write_surfaces", []):
        allowed = "<br>".join(
            f"`{item['path']}::{item['symbol']}`"
            for item in surface.get("allowed_callsites", [])
        )
        rows.append(
            f"| `{surface['id']}` | `{surface['resource']}` | "
            f"`{surface['call']}` | {allowed} |"
        )
    rows.extend(["", "## Envelope invariants", ""])
    for invariant in catalog["envelope_invariants"]:
        rows.append(f"### `{invariant['id']}`")
        rows.append("")
        rows.append("Path: " + " → ".join(f"`{edge}`" for edge in invariant["path"]))
        rows.append("")
        rows.append("| Field | Introduced | Required through |")
        rows.append("| --- | --- | --- |")
        for field in invariant["fields"]:
            rows.append(
                f"| `{field['name']}` | `{field['introduced_at']}` | "
                f"`{field['required_through']}` |"
            )
        rows.append("")
    return "\n".join(rows)


def _write_if_changed(
    path: Path,
    content: str,
    *,
    repo_root: Path,
    dry_run: bool,
) -> dict[str, Any]:
    current = path.read_text(encoding="utf-8-sig") if path.is_file() else None
    changed = current != content
    if changed and not dry_run:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")
    return {
        "path": path.relative_to(repo_root).as_posix(),
        "action": (
            "would_write"
            if dry_run and changed
            else "write"
            if changed
            else "unchanged"
        ),
    }


def generate_drift_edge_projection(
    catalog_path: Path,
    model_catalog_path: Path,
    claim_catalog_path: Path,
    repo_root: Path,
    *,
    dry_run: bool = False,
) -> dict[str, Any]:
    catalog = load_drift_edge_catalog(catalog_path)
    model_catalog = json.loads(model_catalog_path.read_text(encoding="utf-8-sig"))
    claim_catalog = json.loads(claim_catalog_path.read_text(encoding="utf-8-sig"))
    relative_catalog = _display_path(catalog_path, repo_root)
    findings = validate_drift_edge_catalog(
        catalog,
        model_catalog=model_catalog,
        claim_catalog=claim_catalog,
        repo_root=repo_root,
        catalog_path=relative_catalog,
    )
    if findings:
        raise ValueError(
            "invalid architecture drift edges:\n"
            + "\n".join(
                f"{item['rule_id']} {item['unit']}: {item['message']}"
                for item in findings
            )
        )
    projection = catalog["projection"]
    actions = [
        _write_if_changed(
            repo_root / str(projection["puml_path"]),
            render_drift_edge_puml(catalog, model_catalog),
            repo_root=repo_root,
            dry_run=dry_run,
        ),
        _write_if_changed(
            repo_root / str(projection["markdown_path"]),
            render_drift_edge_markdown(catalog),
            repo_root=repo_root,
            dry_run=dry_run,
        ),
    ]
    return {
        "schema_version": "bt.architecture_drift_edge_projection.v1",
        "dry_run": dry_run,
        "edges": len(catalog["edges"]),
        "actions": actions,
    }


def build_drift_edge_report(
    catalog_path: Path,
    model_catalog: Mapping[str, Any],
    claim_catalog: Mapping[str, Any],
    repo_root: Path,
) -> dict[str, Any]:
    relative_catalog = _display_path(catalog_path, repo_root)
    catalog = load_drift_edge_catalog(catalog_path)
    findings = validate_drift_edge_catalog(
        catalog,
        model_catalog=model_catalog,
        claim_catalog=claim_catalog,
        repo_root=repo_root,
        catalog_path=relative_catalog,
    )
    projection = catalog.get("projection", {})
    if not findings and isinstance(projection, Mapping):
        expected = (
            (
                str(projection.get("puml_path", "")),
                render_drift_edge_puml(catalog, model_catalog),
            ),
            (
                str(projection.get("markdown_path", "")),
                render_drift_edge_markdown(catalog),
            ),
        )
        for raw_path, content in expected:
            path = repo_root / raw_path
            if not raw_path or not path.is_file():
                findings.append(
                    _finding(
                        "BT-DRIFT-EDGE-PROJECTION",
                        raw_path or "projection",
                        "generated drift-edge projection is missing",
                        path=raw_path or relative_catalog,
                    )
                )
            elif path.read_text(encoding="utf-8-sig") != content:
                findings.append(
                    _finding(
                        "BT-DRIFT-EDGE-PROJECTION",
                        raw_path,
                        "generated drift-edge projection is stale",
                        path=raw_path,
                    )
                )
    effects = Counter(
        str(edge.get("effect", "unknown"))
        for edge in catalog.get("edges", [])
        if isinstance(edge, Mapping)
    )
    covered_claims = {
        str(claim_id)
        for edge in catalog.get("edges", [])
        if isinstance(edge, Mapping)
        for claim_id in edge.get("claim_ids", [])
    }
    return {
        "schema_version": REPORT_SCHEMA_VERSION,
        "status": "PASS" if not findings else "FAIL",
        "catalog": relative_catalog,
        "edges": len(catalog.get("edges", [])),
        "effect_counts": dict(sorted(effects.items())),
        "covered_claims": sorted(covered_claims),
        "authority_invariants": len(catalog.get("authority_invariants", [])),
        "write_surfaces": len(catalog.get("write_surfaces", [])),
        "envelope_invariants": len(catalog.get("envelope_invariants", [])),
        "findings": sorted(
            findings,
            key=lambda item: (
                str(item["rule_id"]),
                str(item["unit"]),
                str(item["message"]),
            ),
        ),
    }
