"""Deterministic JSON, JUnit and SARIF writers for architecture assurance."""

from __future__ import annotations

from collections.abc import Mapping
import json
from pathlib import Path
from typing import Any
import xml.etree.ElementTree as ET


def _write_if_changed(path: Path, content: str, *, dry_run: bool) -> dict[str, Any]:
    current = path.read_text(encoding="utf-8-sig") if path.is_file() else None
    changed = current != content
    if changed and not dry_run:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")
    return {
        "path": str(path),
        "changed": changed,
        "action": (
            "would_write"
            if dry_run and changed
            else "write"
            if changed
            else "unchanged"
        ),
    }


def render_json(report: Mapping[str, Any]) -> str:
    return json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def _all_findings(report: Mapping[str, Any]) -> list[dict[str, Any]]:
    findings = [dict(item) for item in report.get("findings", [])]
    findings.extend(dict(item) for item in report.get("gate", {}).get("failures", []))
    unique: dict[tuple[str, str, str, str], dict[str, Any]] = {}
    for finding in findings:
        key = (
            str(finding.get("rule_id", "BT-ARCHITECTURE")),
            str(finding.get("unit", "")),
            str(finding.get("message", "")),
            str(finding.get("path", "")),
        )
        unique[key] = finding
    return [unique[key] for key in sorted(unique)]


def render_junit(report: Mapping[str, Any]) -> str:
    subsystems = list(report.get("subsystems", []))
    canon = report.get("canon", {})
    gate = report.get("gate", {})
    cases = len(subsystems) + 2
    failures = sum(bool(item.get("findings")) for item in subsystems) + (
        0 if canon.get("matched") else 1
    ) + (0 if gate.get("status") == "PASS" else 1)
    suite = ET.Element(
        "testsuite",
        {
            "name": "better-tomorrow-architecture-assurance",
            "tests": str(cases),
            "failures": str(failures),
            "errors": "0",
        },
    )
    for subsystem in subsystems:
        case = ET.SubElement(
            suite,
            "testcase",
            {
                "classname": "architecture.depth",
                "name": str(subsystem["id"]),
            },
        )
        subsystem_findings = list(subsystem.get("findings", []))
        if subsystem_findings:
            failure = ET.SubElement(
                case,
                "failure",
                {
                    "type": str(subsystem_findings[0].get("rule_id", "BT-ARCHITECTURE")),
                    "message": f"{len(subsystem_findings)} architecture finding(s)",
                },
            )
            failure.text = "\n".join(
                f"{item.get('rule_id')}: {item.get('unit')}: {item.get('message')}"
                for item in subsystem_findings
            )
        output = ET.SubElement(case, "system-out")
        output.text = json.dumps(
            {
                "declared": subsystem.get("declared"),
                "bound": subsystem.get("bound"),
                "discovered": subsystem.get("discovered"),
                "represented": subsystem.get("represented"),
                "view_model_coverage": subsystem.get("view_model_coverage"),
            },
            sort_keys=True,
        )
    canon_case = ET.SubElement(
        suite,
        "testcase",
        {"classname": "architecture.canon", "name": "canon-projection"},
    )
    if not canon.get("matched"):
        failure = ET.SubElement(
            canon_case,
            "failure",
            {"type": "BT-CANON-DRIFT", "message": "canon projection drift"},
        )
        failure.text = json.dumps(canon, sort_keys=True)
    gate_case = ET.SubElement(
        suite,
        "testcase",
        {"classname": "architecture.gate", "name": "pinned-depth-floor"},
    )
    if gate.get("status") != "PASS":
        failure = ET.SubElement(
            gate_case,
            "failure",
            {"type": "BT-DEPTH-GATE", "message": "architecture depth gate failed"},
        )
        failure.text = json.dumps(gate.get("failures", []), sort_keys=True)
    ET.indent(suite, space="  ")
    return '<?xml version="1.0" encoding="utf-8"?>\n' + ET.tostring(
        suite, encoding="unicode", short_empty_elements=True
    ) + "\n"


def render_sarif(report: Mapping[str, Any]) -> str:
    findings = _all_findings(report)
    rule_ids = sorted(
        {str(item.get("rule_id", "BT-ARCHITECTURE")) for item in findings}
    )
    rules = [
        {
            "id": rule_id,
            "name": rule_id.replace("-", " ").title(),
            "shortDescription": {"text": rule_id},
            "defaultConfiguration": {"level": "error"},
        }
        for rule_id in rule_ids
    ]
    results: list[dict[str, Any]] = []
    for item in findings:
        result: dict[str, Any] = {
            "ruleId": str(item.get("rule_id", "BT-ARCHITECTURE")),
            "level": "error",
            "message": {
                "text": f"{item.get('unit', '')}: {item.get('message', '')}".strip(": ")
            },
        }
        if item.get("path"):
            result["locations"] = [
                {
                    "physicalLocation": {
                        "artifactLocation": {
                            "uri": str(item["path"]).replace("\\", "/"),
                            "uriBaseId": "%SRCROOT%",
                        }
                    }
                }
            ]
        results.append(result)
    sarif = {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "Better Tomorrow Architecture Assurance",
                        "semanticVersion": "1.0.0",
                        "informationUri": "https://github.com/Held0fTheWelt/WorldOfShadows",
                        "rules": rules,
                    }
                },
                "originalUriBaseIds": {
                    "%SRCROOT%": {"uri": "file:///"}
                },
                "results": results,
            }
        ],
    }
    return json.dumps(sarif, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def write_reports(
    report: Mapping[str, Any],
    *,
    json_path: Path | None = None,
    junit_path: Path | None = None,
    sarif_path: Path | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    writers = (
        ("json", json_path, render_json),
        ("junit", junit_path, render_junit),
        ("sarif", sarif_path, render_sarif),
    )
    actions: dict[str, Any] = {}
    for name, path, renderer in writers:
        if path is not None:
            actions[name] = _write_if_changed(path, renderer(report), dry_run=dry_run)
    return {
        "schema_version": "bt.architecture_report_export_result.v1",
        "dry_run": dry_run,
        "actions": actions,
    }
