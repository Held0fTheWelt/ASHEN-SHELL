from __future__ import annotations

from pathlib import Path

from tools.architecture_assurance.audit import build_report
from tools.architecture_assurance.manifest_builder import generate_manifests
from tools.architecture_assurance.view_builder import generate_views


ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "tools" / "architecture_assurance" / "config.json"


def test_generated_artifacts_are_current_without_writes() -> None:
    manifests = generate_manifests(CONFIG, ROOT, dry_run=True)
    views = generate_views(CONFIG, ROOT, dry_run=True)
    assert not manifests["parse_errors"]
    assert {item["action"] for item in manifests["actions"]} == {"unchanged"}
    assert {item["action"] for item in views["actions"]} == {"unchanged"}


def test_better_tomorrow_architecture_depth_gate_passes() -> None:
    report = build_report(CONFIG, ROOT)
    assert report["gate"]["status"] == "PASS", report["gate"]["failures"]
    assert report["corpus_rollup"]["subsystems"] == 17
    assert report["corpus_rollup"]["view_counts"] == {"model": 94}
    assert report["architecture_posture"]["status"] == "KNOWN_VIOLATIONS"
    rollup = report["corpus_rollup"]
    assert rollup["represented"] == rollup["classified"] == rollup["discovered"]
    assert rollup["representation_coverage"] == 1.0
    assert rollup["classification_coverage"] == 1.0
    assert rollup["outside_representation"] == {}
