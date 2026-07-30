"""Release gate for Better Tomorrow's own architecture assurance set."""

from pathlib import Path

from tools.architecture_assurance.audit import build_report


ROOT = Path(__file__).resolve().parents[2]


def test_better_tomorrow_architecture_assurance_gate() -> None:
    report = build_report(
        ROOT / "tools" / "architecture_assurance" / "config.json",
        ROOT,
    )
    assert report["gate"]["status"] == "PASS", report["gate"]["failures"]
