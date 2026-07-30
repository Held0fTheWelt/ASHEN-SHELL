from __future__ import annotations

import json
from pathlib import Path
import xml.etree.ElementTree as ET

from tools.architecture_assurance.reporters import (
    render_sarif,
    write_reports,
)


def _report(*, finding: bool = False) -> dict:
    findings = (
        [
            {
                "rule_id": "BT-EXAMPLE",
                "unit": "sample:D1",
                "message": "example finding",
                "path": "docs/architecture/sample.md",
            }
        ]
        if finding
        else []
    )
    return {
        "project_id": "better-tomorrow",
        "subsystems": [
            {
                "id": "sample",
                "declared": 1,
                "bound": 1,
                "discovered": 1,
                "represented": 1,
                "view_model_coverage": 1.0,
                "findings": findings,
            }
        ],
        "corpus_rollup": {"subsystems": 1},
        "canon": {"matched": not finding},
        "findings": findings,
        "gate": {"status": "FAIL" if finding else "PASS", "failures": []},
    }


def test_json_junit_and_sarif_are_valid_and_idempotent(tmp_path: Path) -> None:
    json_path = tmp_path / "audit.json"
    junit_path = tmp_path / "audit.xml"
    sarif_path = tmp_path / "audit.sarif"
    first = write_reports(
        _report(),
        json_path=json_path,
        junit_path=junit_path,
        sarif_path=sarif_path,
    )
    assert {item["action"] for item in first["actions"].values()} == {"write"}
    second = write_reports(
        _report(),
        json_path=json_path,
        junit_path=junit_path,
        sarif_path=sarif_path,
    )
    assert {item["action"] for item in second["actions"].values()} == {"unchanged"}
    assert json.loads(json_path.read_text(encoding="utf-8"))["project_id"] == "better-tomorrow"
    ET.parse(junit_path)
    sarif = json.loads(sarif_path.read_text(encoding="utf-8"))
    assert sarif["version"] == "2.1.0"
    failing_junit = tmp_path / "failing.xml"
    write_reports(_report(finding=True), junit_path=failing_junit)
    failing_suite = ET.parse(failing_junit).getroot()
    assert int(failing_suite.attrib["failures"]) >= 1
    assert failing_suite.find("./testcase[@name='pinned-depth-floor']/failure") is not None


def test_dry_run_reports_intent_without_writing(tmp_path: Path) -> None:
    target = tmp_path / "audit.sarif"
    result = write_reports(
        _report(finding=True),
        sarif_path=target,
        dry_run=True,
    )
    assert result["actions"]["sarif"]["action"] == "would_write"
    assert not target.exists()
    assert "BT-EXAMPLE" in render_sarif(_report(finding=True))
