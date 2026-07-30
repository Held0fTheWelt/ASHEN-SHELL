"""Five-axis Better Tomorrow architecture-depth audit and non-regression gate."""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping
import json
from pathlib import Path
import re
from typing import Any

from .canon import build_canon_manifest, verify_canon_manifest
from .discovery import discover_subsystem
from .manifest_builder import load_config
from .sad_parser import parse_sad
from .schemas import (
    GATE_RESULT_SCHEMA_VERSION,
    GATE_SCHEMA_VERSION,
    REPORT_SCHEMA_VERSION,
    SchemaValidationError,
    validate_manifest,
)


_ELEMENT = re.compile(
    r"(?im)^\s*(?:Person|System|Container|Component|"
    r"rectangle|component|class|interface|database|participant|actor|node)"
    r"(?:_Ext|Db|Queue)?\s*(?:\(|\b)"
)
_LEGIBILITY_BANDS = {
    "context": (2, 12),
    "container": (3, 20),
    "component": (4, 30),
    "class": (3, 40),
    "runtime": (3, 40),
    "data": (3, 40),
    "deployment": (2, 30),
}
_ACCEPTED = ("accepted", "partially implemented", "implemented")


def _view_status(view: Mapping[str, Any], repo_root: Path) -> dict[str, Any]:
    path = repo_root / str(view["path"])
    if not path.is_file():
        return {"status": "missing", "elements": 0, "path": view["path"]}
    text = path.read_text(encoding="utf-8-sig")
    elements = len(_ELEMENT.findall(text))
    minimum, maximum = _LEGIBILITY_BANDS.get(str(view["level"]), (3, 30))
    if elements < minimum:
        status = "sketch"
    elif elements > maximum:
        status = "hairball"
    elif "[[" not in text:
        status = "sketch"
    elif not any(token in text.lower() for token in ("responsibility", "contract", "owns")):
        status = "sketch"
    else:
        status = "model"
    return {"status": status, "elements": elements, "path": view["path"]}


def _anchor_signature(unit: Mapping[str, Any]) -> tuple[Any, ...]:
    anchor = unit["anchor"]
    return (
        unit["id"],
        anchor.get("kind"),
        anchor.get("file"),
        anchor.get("line"),
        anchor.get("symbol"),
        anchor.get("route"),
        anchor.get("object"),
    )


def _drift(
    manifest: Mapping[str, Any],
    subsystem: Mapping[str, Any],
    repo_root: Path,
) -> dict[str, Any]:
    fresh_units, parse_errors = discover_subsystem(subsystem, repo_root)
    expected = {
        str(unit["id"]): _anchor_signature(unit)
        for unit in manifest.get("discovered_units", [])
    }
    actual = {
        str(unit["id"]): _anchor_signature(unit) for unit in fresh_units
    }
    findings: list[dict[str, Any]] = []
    for unit_id in sorted(set(expected) - set(actual)):
        findings.append(
            {"rule_id": "BT-DRIFT-MISSING", "unit": unit_id, "message": "bound unit disappeared"}
        )
    for unit_id in sorted(set(actual) - set(expected)):
        findings.append(
            {"rule_id": "BT-DRIFT-ORPHAN", "unit": unit_id, "message": "new unit is not in the manifest"}
        )
    for unit_id in sorted(set(expected) & set(actual)):
        if expected[unit_id] != actual[unit_id]:
            findings.append(
                {"rule_id": "BT-DRIFT-ANCHOR", "unit": unit_id, "message": "source anchor changed"}
            )
    for error in parse_errors:
        findings.append(
            {
                "rule_id": "BT-DISCOVERY-PARSE",
                "unit": error["file"],
                "message": error["error"],
            }
        )
    return {
        "expected": len(expected),
        "actual": len(actual),
        "matched": len(set(expected) & set(actual))
        - sum(1 for finding in findings if finding["rule_id"] == "BT-DRIFT-ANCHOR"),
        "findings": findings,
        "consistent": not findings,
    }


def _subsystem_report(
    subsystem: Mapping[str, Any],
    repo_root: Path,
) -> dict[str, Any]:
    sad_path = repo_root / str(subsystem["sad_path"])
    sad = parse_sad(sad_path.read_text(encoding="utf-8-sig"))
    manifest_path = sad_path.parent / "architecture.bindings.json"
    findings: list[dict[str, Any]] = []
    try:
        manifest = validate_manifest(
            json.loads(manifest_path.read_text(encoding="utf-8-sig"))
        )
    except (OSError, json.JSONDecodeError, SchemaValidationError) as exc:
        manifest = {
            "building_blocks": [],
            "decisions": [],
            "discovered_units": [],
            "representation_map": {},
            "out_of_scope": {},
            "required_views": [],
            "lanes": [],
        }
        findings.append(
            {
                "rule_id": "BT-MANIFEST-INVALID",
                "unit": subsystem["id"],
                "message": str(exc),
                "path": manifest_path.relative_to(repo_root).as_posix(),
            }
        )

    declarations = [
        *manifest.get("building_blocks", []),
        *manifest.get("decisions", []),
    ]
    bound = sum(
        entry.get("state") == "bound" and bool(entry.get("anchors"))
        for entry in declarations
    )
    accepted = [
        entry
        for entry in declarations
        if str(entry.get("status", "")).lower().startswith(_ACCEPTED)
    ]
    accepted_bound = sum(
        entry.get("state") == "bound" and bool(entry.get("anchors"))
        for entry in accepted
    )
    for entry in accepted:
        if entry.get("state") != "bound" or not entry.get("anchors"):
            findings.append(
                {
                    "rule_id": "BT-BINDING-MISSING",
                    "unit": f"{subsystem['id']}:{entry.get('id')}",
                    "message": "accepted or implemented declaration has no source anchor",
                    "path": subsystem["sad_path"],
                }
            )

    discovered = len(manifest.get("discovered_units", []))
    represented = len(manifest.get("representation_map", {})) + len(
        manifest.get("out_of_scope", {})
    )
    orphan_ids = sorted(
        {
            str(unit["id"]) for unit in manifest.get("discovered_units", [])
        }
        - set(manifest.get("representation_map", {}))
        - set(manifest.get("out_of_scope", {}))
    )
    for unit_id in orphan_ids:
        findings.append(
            {
                "rule_id": "BT-REPRESENTATION-ORPHAN",
                "unit": unit_id,
                "message": "discovered unit is neither represented nor explicitly out-of-scope",
                "path": subsystem["sad_path"],
            }
        )

    views = {
        str(view["id"]): _view_status(view, repo_root)
        for view in manifest.get("required_views", [])
    }
    for view_id, result in views.items():
        if result["status"] != "model":
            findings.append(
                {
                    "rule_id": "BT-VIEW-DEPTH",
                    "unit": f"{subsystem['id']}:{view_id}",
                    "message": f"required view is {result['status']}",
                    "path": result["path"],
                }
            )
    drift = _drift(manifest, subsystem, repo_root)
    findings.extend(
        {
            **finding,
            "path": subsystem["sad_path"],
        }
        for finding in drift["findings"]
    )

    structure_complete = sad.section_numbers == tuple(range(1, 13))
    if not structure_complete:
        findings.append(
            {
                "rule_id": "BT-ARC42-INCOMPLETE",
                "unit": subsystem["id"],
                "message": f"arc42 sections are {sad.section_numbers}, expected 1..12",
                "path": subsystem["sad_path"],
            }
        )
    model_views = sum(result["status"] == "model" for result in views.values())
    return {
        "id": subsystem["id"],
        "scope": subsystem["scope"],
        "critical": bool(subsystem.get("critical")),
        "sad_path": subsystem["sad_path"],
        "structure_complete": structure_complete,
        "declared": len(declarations),
        "bound": bound,
        "binding_coverage": bound / len(declarations) if declarations else 0.0,
        "accepted_declared": len(accepted),
        "accepted_bound": accepted_bound,
        "accepted_binding_coverage": (
            accepted_bound / len(accepted) if accepted else 1.0
        ),
        "discovered": discovered,
        "represented": represented,
        "representation_coverage": represented / discovered if discovered else 1.0,
        "orphan_units": orphan_ids,
        "views": views,
        "view_model_coverage": model_views / len(views) if views else 1.0,
        "lane_reach": bool(manifest.get("lanes")) and discovered > 0,
        "drift": drift,
        "correspondence_consistency": drift["consistent"],
        "findings": findings,
    }


def _rollup(subsystems: list[dict[str, Any]]) -> dict[str, Any]:
    declared = sum(item["declared"] for item in subsystems)
    bound = sum(item["bound"] for item in subsystems)
    accepted = sum(item["accepted_declared"] for item in subsystems)
    accepted_bound = sum(item["accepted_bound"] for item in subsystems)
    discovered = sum(item["discovered"] for item in subsystems)
    represented = sum(item["represented"] for item in subsystems)
    views = [
        view["status"]
        for item in subsystems
        for view in item["views"].values()
    ]
    view_counts = Counter(views)
    return {
        "subsystems": len(subsystems),
        "critical_subsystems": sum(item["critical"] for item in subsystems),
        "structure_complete": sum(item["structure_complete"] for item in subsystems),
        "declared": declared,
        "bound": bound,
        "binding_coverage": bound / declared if declared else 0.0,
        "accepted_declared": accepted,
        "accepted_bound": accepted_bound,
        "accepted_binding_coverage": accepted_bound / accepted if accepted else 1.0,
        "discovered": discovered,
        "represented": represented,
        "representation_coverage": represented / discovered if discovered else 1.0,
        "views": len(views),
        "view_counts": dict(sorted(view_counts.items())),
        "view_model_coverage": view_counts["model"] / len(views) if views else 1.0,
        "correspondence_consistency": (
            sum(item["correspondence_consistency"] for item in subsystems)
            / len(subsystems)
            if subsystems
            else 0.0
        ),
        "lane_reach": (
            sum(item["lane_reach"] for item in subsystems) / len(subsystems)
            if subsystems
            else 0.0
        ),
    }


def build_report(config_path: Path, repo_root: Path) -> dict[str, Any]:
    config = load_config(config_path)
    subsystems = [
        _subsystem_report(subsystem, repo_root)
        for subsystem in config["subsystems"]
    ]
    canon_path = repo_root / str(config["canon_manifest"])
    canon = verify_canon_manifest(
        canon_path,
        repo_root,
        build_canon_manifest(config, repo_root),
    )
    findings = [
        finding
        for subsystem in subsystems
        for finding in subsystem["findings"]
    ]
    if not canon["matched"]:
        findings.append(
            {
                "rule_id": "BT-CANON-DRIFT",
                "unit": config["project_id"],
                "message": "canon manifest is missing or differs from the repository projection",
                "path": config["canon_manifest"],
            }
        )
    report = {
        "schema_version": REPORT_SCHEMA_VERSION,
        "project_id": config["project_id"],
        "subsystems": subsystems,
        "corpus_rollup": _rollup(subsystems),
        "canon": canon,
        "findings": findings,
    }
    report["gate"] = evaluate_gate(report, config["gate"])
    return report


def evaluate_gate(
    report: Mapping[str, Any],
    gate_config: Mapping[str, Any],
) -> dict[str, Any]:
    if gate_config.get("schema_version") != GATE_SCHEMA_VERSION:
        raise ValueError("unsupported Better Tomorrow gate config")
    failures: list[dict[str, Any]] = []
    minimum_census = gate_config["minimum_census"]
    rollup = report["corpus_rollup"]
    for key, minimum in minimum_census.items():
        actual = int(rollup.get(key, 0))
        if actual < int(minimum):
            failures.append(
                {
                    "rule_id": "BT-CENSUS-REGRESSION",
                    "unit": key,
                    "message": f"{actual} is below pinned minimum {minimum}",
                }
            )
    critical_floor = gate_config["critical_floor"]
    for subsystem in report["subsystems"]:
        if not subsystem["critical"]:
            continue
        for key, minimum in critical_floor.items():
            actual = subsystem.get(key)
            passed = (
                bool(actual) == bool(minimum)
                if isinstance(minimum, bool)
                else float(actual) >= float(minimum)
            )
            if not passed:
                failures.append(
                    {
                        "rule_id": "BT-CRITICAL-FLOOR",
                        "unit": f"{subsystem['id']}:{key}",
                        "message": f"{actual!r} is below required {minimum!r}",
                    }
                )
    if gate_config.get("require_canon") and not report["canon"]["matched"]:
        failures.append(
            {
                "rule_id": "BT-CANON-REQUIRED",
                "unit": report["project_id"],
                "message": "canon projection does not match its manifest",
            }
        )
    return {
        "schema_version": GATE_RESULT_SCHEMA_VERSION,
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
    }
