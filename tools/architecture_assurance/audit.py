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
from .drift_claims import load_claim_catalog, validate_claim_catalog
from .drift_edges import build_drift_edge_report
from .manifest_builder import load_config
from .sad_parser import parse_sad
from .semantic_models import load_model_catalog, validate_model_catalog
from .schemas import (
    GATE_RESULT_SCHEMA_VERSION,
    GATE_SCHEMA_VERSION,
    REPORT_SCHEMA_VERSION,
    SchemaValidationError,
    validate_manifest,
)


_ELEMENT = re.compile(
    r'(?im)^\s*(?:rectangle|component|class|interface|database|'
    r'participant|actor|node|activity|artifact|queue|state|usecase)\s+"'
)
_KIND_NOTATION = {
    "class": "class",
    "component": "component",
    "container": "rectangle",
    "context": "rectangle",
    "data": "class",
    "deployment": "node",
    "sequence": "participant",
    "state": "state",
    "usecase": "usecase",
}
_ACCEPTED = ("accepted", "partially implemented", "implemented")


def _view_status(view: Mapping[str, Any], repo_root: Path) -> dict[str, Any]:
    path = repo_root / str(view["path"])
    if not path.is_file():
        return {
            "status": "missing",
            "elements": 0,
            "relationships": 0,
            "reasons": ["model file is missing"],
            "path": view["path"],
        }
    text = path.read_text(encoding="utf-8-sig")
    marker_elements = len(
        re.findall(r"(?im)^\s*'\s*bt-element-id:\s*\S+", text)
    )
    elements = marker_elements or len(_ELEMENT.findall(text))
    relationships = text.count("contract:")
    expected_elements = int(view.get("element_count", 0))
    expected_relationships = int(view.get("relationship_count", 0))
    kind = str(view.get("kind") or view.get("level"))
    reasons: list[str] = []
    if f"' bt-view-kind: {kind}" not in text:
        reasons.append("semantic viewpoint marker is missing or wrong")
    if expected_elements and elements != expected_elements:
        reasons.append(
            f"modeled elements {elements} != declared {expected_elements}"
        )
    if relationships != expected_relationships:
        reasons.append(
            "semantic relationships "
            f"{relationships} != declared {expected_relationships}"
        )
    if text.count("Responsibility:") < expected_elements:
        reasons.append("one or more elements lack an explicit responsibility")
    if text.count("Contract:") < expected_elements:
        reasons.append("one or more elements lack an explicit contract")
    if text.count("[[") < expected_elements:
        reasons.append("one or more elements lack a navigable source anchor")
    if kind == "activity" and ("(*)" not in text or "-->" not in text):
        reasons.append("view does not use activity start/flow notation")
    notation = _KIND_NOTATION.get(kind)
    if notation and not re.search(
        rf"(?im)^\s*{re.escape(notation)}\b",
        text,
    ):
        if not (
            kind == "sequence"
            and re.search(r"(?im)^\s*actor\b", text)
            and " -> " in text
        ):
            reasons.append(f"view does not use {kind} notation")
    if kind == "state" and "[*]" not in text:
        reasons.append("state model has no initial or final transition")
    if kind == "sequence" and " -> " not in text:
        reasons.append("sequence model has no ordered messages")
    if "evidence for boundary" in text.lower():
        reasons.append("generic evidence-star relationship detected")
    relation_lines = [
        line.strip()
        for line in text.splitlines()
        if "contract:" in line
    ]
    if len(relation_lines) > 1 and len(set(relation_lines)) == 1:
        reasons.append("all relationship semantics are identical")
    return {
        "status": "model" if not reasons else "sketch",
        "elements": elements,
        "expected_elements": expected_elements,
        "relationships": relationships,
        "expected_relationships": expected_relationships,
        "kind": kind,
        "concern": view.get("concern", ""),
        "reasons": reasons,
        "path": view["path"],
    }


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
    represented = len(manifest.get("representation_map", {}))
    classifications = Counter(
        str(reason).split(":", 1)[0]
        for reason in manifest.get("out_of_scope", {}).values()
    )
    classified_outside = sum(classifications.values())
    classified = represented + classified_outside
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
                    "message": (
                        f"required view is {result['status']}: "
                        + "; ".join(result.get("reasons", []))
                    ),
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
        "classified": classified,
        "classification_coverage": classified / discovered if discovered else 1.0,
        "outside_representation": dict(sorted(classifications.items())),
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
    classified = sum(item["classified"] for item in subsystems)
    outside_representation = Counter(
        {
            category: sum(
                item["outside_representation"].get(category, 0)
                for item in subsystems
            )
            for category in {
                category
                for item in subsystems
                for category in item["outside_representation"]
            }
        }
    )
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
        "classified": classified,
        "classification_coverage": classified / discovered if discovered else 1.0,
        "outside_representation": dict(sorted(outside_representation.items())),
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
    global_findings: list[dict[str, Any]] = []
    model_catalog = load_model_catalog(
        repo_root / str(config["model_catalog"])
    )
    for finding in validate_model_catalog(model_catalog, repo_root):
        global_findings.append(
            {
                "rule_id": "BT-SEMANTIC-CATALOG",
                "unit": (
                    f"{finding['subsystem']}:{finding['view']}"
                ),
                "message": finding["error"],
                "path": config["model_catalog"],
            }
        )
    claim_catalog = load_claim_catalog(
        repo_root / str(config["drift_claim_catalog"])
    )
    for message in validate_claim_catalog(claim_catalog, repo_root):
        global_findings.append(
            {
                "rule_id": "BT-DRIFT-CLAIM",
                "unit": config["project_id"],
                "message": message,
                "path": config["drift_claim_catalog"],
            }
        )
    drift_edges = build_drift_edge_report(
        repo_root / str(config["drift_edge_catalog"]),
        model_catalog,
        claim_catalog,
        repo_root,
    )
    global_findings.extend(drift_edges["findings"])
    view_profiles = {
        subsystem_id: tuple(
            str(view["kind"]) for view in model["views"]
        )
        for subsystem_id, model in model_catalog["subsystems"].items()
    }
    if len(set(view_profiles.values())) == 1:
        global_findings.append(
            {
                "rule_id": "BT-FIXED-VIEW-PROFILE",
                "unit": config["project_id"],
                "message": "all subsystems use one fixed viewpoint profile",
                "path": config["model_catalog"],
            }
        )
    for subsystem_id, model in model_catalog["subsystems"].items():
        for view in model["views"]:
            if "/depth/" in str(view["path"]).replace("\\", "/"):
                global_findings.append(
                    {
                        "rule_id": "BT-LEGACY-DEPTH-VIEW",
                        "unit": f"{subsystem_id}:{view['id']}",
                        "message": "legacy fixed-depth projection remains required",
                        "path": view["path"],
                    }
                )
    for required_path, rule_id in (
        (config["drift_evidence_json"], "BT-DRIFT-EVIDENCE"),
        (config["drift_evidence_markdown"], "BT-DRIFT-EVIDENCE"),
        (config["drift_reconciliation"], "BT-DRIFT-RECONCILIATION"),
    ):
        if not (repo_root / str(required_path)).is_file():
            global_findings.append(
                {
                    "rule_id": rule_id,
                    "unit": config["project_id"],
                    "message": "required Git/archaeology evidence is missing",
                    "path": required_path,
                }
            )
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
    findings = global_findings + [
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
        "drift_edges": drift_edges,
        "findings": findings,
    }
    claim_counts = Counter(
        str(claim["status"]) for claim in claim_catalog["claims"]
    )
    report["architecture_posture"] = {
        "status": (
            "KNOWN_VIOLATIONS"
            if claim_counts["conflicting"] or claim_counts["open_target"]
            else "CONFORMING"
        ),
        "claim_status_counts": dict(sorted(claim_counts.items())),
        "register": "docs/architecture/violations/README.md",
        "meaning": (
            "The evidence pipeline is operational; current implementation "
            "still differs from accepted or proposed target architecture."
        ),
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
    if gate_config.get("fail_on_findings"):
        existing = {
            (
                failure["rule_id"],
                failure["unit"],
                failure["message"],
            )
            for failure in failures
        }
        for finding in report.get("findings", []):
            signature = (
                finding["rule_id"],
                finding["unit"],
                finding["message"],
            )
            if signature not in existing:
                failures.append(
                    {
                        "rule_id": finding["rule_id"],
                        "unit": finding["unit"],
                        "message": finding["message"],
                    }
                )
                existing.add(signature)
    return {
        "schema_version": GATE_RESULT_SCHEMA_VERSION,
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
    }
