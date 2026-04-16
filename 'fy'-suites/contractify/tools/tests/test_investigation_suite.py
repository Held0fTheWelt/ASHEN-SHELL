from __future__ import annotations

from pathlib import Path

import contractify.tools.repo_paths as repo_paths
from contractify.tools.investigation_suite import write_adr_investigation_suite


def test_adr_investigation_suite_writes_markdown_and_mermaid() -> None:
    root = repo_paths.repo_root()
    out_dir_rel = "'fy'-suites/contractify/reports/_pytest_adr_investigation"
    out_dir = root / out_dir_rel
    try:
        bundle = write_adr_investigation_suite(root, out_dir_rel=out_dir_rel)
        assert bundle["adr_governance"]["stats"]["n_adrs"] >= 1
        md = out_dir / "ADR_GOVERNANCE_INVESTIGATION.md"
        rel_map = out_dir / "ADR_RELATION_MAP.mmd"
        conflict_map = out_dir / "ADR_CONFLICT_MAP.mmd"
        assert md.is_file()
        assert rel_map.is_file()
        assert conflict_map.is_file()
        assert "## ADR inventory" in md.read_text(encoding="utf-8")
        assert "graph TD" in rel_map.read_text(encoding="utf-8")
        assert "graph TD" in conflict_map.read_text(encoding="utf-8")
    finally:
        if out_dir.exists():
            for child in sorted(out_dir.glob("*"), reverse=True):
                child.unlink()
            out_dir.rmdir()
