from __future__ import annotations

from pathlib import Path

from contractify.tools.adr_governance import discover_adr_governance
from contractify.tools.minimal_repo import build_minimal_contractify_test_repo
import contractify.tools.repo_paths as repo_paths


def test_adr_governance_reports_canonical_inventory_and_targets() -> None:
    root = repo_paths.repo_root()
    payload = discover_adr_governance(root)
    assert payload["canonical_dir"] == "docs/ADR"
    assert payload["stats"]["n_adrs"] >= 3
    assert payload["stats"]["n_legacy_adrs"] == 0
    assert not any(f["kind"] == "legacy_adr_location" for f in payload["findings"])
    for row in payload["records"]:
        assert row["proposed_canonical_path"].startswith("docs/ADR/")
        assert row["proposed_canonical_id"].startswith("ADR.")


def test_adr_governance_detects_canonical_path_collision(tmp_path: Path) -> None:
    root = build_minimal_contractify_test_repo(tmp_path)
    adr = root / "docs" / "ADR"
    (adr / "adr-0001-scene-identity-copy.md").write_text(
        "# ADR-0001: Scene identity\n\n**Status**: Accepted\n\nSame title, same family.\n",
        encoding="utf-8",
    )
    payload = discover_adr_governance(root)
    assert any(f["kind"] in {"duplicate_declared_id", "canonical_path_collision", "similar_title_overlap"} for f in payload["findings"])
