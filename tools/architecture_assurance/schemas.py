"""Versioned schemas and validators for Better Tomorrow architecture evidence."""

from __future__ import annotations

from collections.abc import Mapping
from copy import deepcopy
from typing import Any


ANCHOR_SCHEMA_VERSION = "bt.source_anchor.v1"
BINDINGS_SCHEMA_VERSION = "bt.architecture_bindings.v1"
REPORT_SCHEMA_VERSION = "bt.architecture_depth_coverage.v1"
GATE_SCHEMA_VERSION = "bt.architecture_depth_gate.v1"
GATE_RESULT_SCHEMA_VERSION = "bt.architecture_depth_gate_result.v1"

ANCHOR_KINDS = {
    "python",
    "schema",
    "api",
    "content",
    "web",
    "deployment",
    "test",
    "file",
}
ENTRY_STATES = {"bound", "claimed_only", "orphan"}


class SchemaValidationError(ValueError):
    """Raised when a Better Tomorrow assurance artifact is invalid."""


def _text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def validate_anchor(anchor: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(anchor, Mapping):
        raise SchemaValidationError("source anchor must be an object")
    if anchor.get("schema_version") != ANCHOR_SCHEMA_VERSION:
        raise SchemaValidationError(
            f"anchor schema_version must be {ANCHOR_SCHEMA_VERSION}"
        )
    kind = anchor.get("kind")
    if kind not in ANCHOR_KINDS:
        raise SchemaValidationError(f"unknown source anchor kind: {kind!r}")
    if not _text(anchor.get("file")):
        raise SchemaValidationError("source anchor file must be non-empty")
    line = anchor.get("line")
    if not isinstance(line, int) or isinstance(line, bool) or line < 1:
        raise SchemaValidationError("source anchor line must be a positive integer")
    if kind == "api" and not (
        _text(anchor.get("route")) or _text(anchor.get("symbol"))
    ):
        raise SchemaValidationError("api anchor requires route or symbol")
    if kind == "schema" and not (
        _text(anchor.get("object")) or _text(anchor.get("symbol"))
    ):
        raise SchemaValidationError("schema anchor requires object or symbol")
    if kind == "content" and not (
        _text(anchor.get("object")) or _text(anchor.get("symbol"))
    ):
        raise SchemaValidationError("content anchor requires object or symbol")
    return deepcopy(dict(anchor))


def _validate_entries(manifest: Mapping[str, Any], key: str) -> None:
    entries = manifest.get(key)
    if not isinstance(entries, list):
        raise SchemaValidationError(f"{key} must be a list")
    seen: set[str] = set()
    for entry in entries:
        if not isinstance(entry, Mapping):
            raise SchemaValidationError(f"{key} entries must be objects")
        entry_id = entry.get("id")
        if not _text(entry_id):
            raise SchemaValidationError(f"{key} entry id must be non-empty")
        if entry_id in seen:
            raise SchemaValidationError(f"duplicate {key} entry id: {entry_id}")
        seen.add(str(entry_id))
        state = entry.get("state")
        if state not in ENTRY_STATES:
            raise SchemaValidationError(
                f"{key} entry {entry_id} has invalid state {state!r}"
            )
        anchors = entry.get("anchors")
        if not isinstance(anchors, list):
            raise SchemaValidationError(
                f"{key} entry {entry_id} anchors must be a list"
            )
        if state == "bound" and not anchors:
            raise SchemaValidationError(
                f"bound entry {entry_id} requires at least one anchor"
            )
        if state == "claimed_only" and anchors:
            raise SchemaValidationError(
                f"claimed_only entry {entry_id} cannot carry anchors"
            )
        for anchor in anchors:
            validate_anchor(anchor)


def validate_manifest(manifest: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(manifest, Mapping):
        raise SchemaValidationError("bindings manifest must be an object")
    if manifest.get("schema_version") != BINDINGS_SCHEMA_VERSION:
        raise SchemaValidationError(
            f"manifest schema_version must be {BINDINGS_SCHEMA_VERSION}"
        )
    for key in ("subsystem", "sad_path"):
        if not _text(manifest.get(key)):
            raise SchemaValidationError(f"{key} must be non-empty")
    lanes = manifest.get("lanes")
    if not isinstance(lanes, list) or not lanes or not all(_text(x) for x in lanes):
        raise SchemaValidationError("lanes must be a non-empty string list")
    _validate_entries(manifest, "building_blocks")
    _validate_entries(manifest, "decisions")

    units = manifest.get("discovered_units", [])
    if not isinstance(units, list):
        raise SchemaValidationError("discovered_units must be a list")
    unit_ids: set[str] = set()
    for unit in units:
        if not isinstance(unit, Mapping) or not _text(unit.get("id")):
            raise SchemaValidationError("discovered units require a non-empty id")
        unit_id = str(unit["id"])
        if unit_id in unit_ids:
            raise SchemaValidationError(f"duplicate discovered unit: {unit_id}")
        unit_ids.add(unit_id)
        validate_anchor(unit["anchor"])

    representation = manifest.get("representation_map", {})
    if not isinstance(representation, Mapping):
        raise SchemaValidationError("representation_map must be an object")
    unknown_units = sorted(set(representation) - unit_ids)
    if unknown_units:
        raise SchemaValidationError(
            "representation_map references unknown units: "
            + ", ".join(unknown_units)
        )

    out_of_scope = manifest.get("out_of_scope", {})
    if not isinstance(out_of_scope, Mapping):
        raise SchemaValidationError("out_of_scope must be an object")
    for unit_id, reason in out_of_scope.items():
        if unit_id not in unit_ids or not _text(reason):
            raise SchemaValidationError(
                "out_of_scope entries require a known unit and non-empty reason"
            )
    overlapping = sorted(set(representation) & set(out_of_scope))
    if overlapping:
        raise SchemaValidationError(
            "units cannot be represented and out-of-scope: "
            + ", ".join(overlapping)
        )

    required_views = manifest.get("required_views", [])
    if not isinstance(required_views, list):
        raise SchemaValidationError("required_views must be a list")
    for view in required_views:
        if not isinstance(view, Mapping) or not all(
            _text(view.get(key)) for key in ("id", "level", "path")
        ):
            raise SchemaValidationError(
                "required views require non-empty id, level, and path"
            )
    return deepcopy(dict(manifest))
