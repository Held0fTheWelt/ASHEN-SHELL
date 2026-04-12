"""Tests for spaghetti_setup_audit (canonical md vs json mirror)."""
from __future__ import annotations

import unittest
from pathlib import Path


class SpaghettiSetupAuditTests(unittest.TestCase):
    def test_parse_current_repo_setup_md(self) -> None:
        from despaghettify.tools.spaghetti_setup_audit import compute_m7_ref, parse_spaghetti_setup_md

        root = Path(__file__).resolve().parents[3]
        md_path = root / "despaghettify" / "spaghetti-setup.md"
        p = parse_spaghetti_setup_md(md_path.read_text(encoding="utf-8"))
        self.assertEqual(p["trigger_bars"]["C1"], 5.0)
        self.assertEqual(p["weights"]["C1"], 0.2)
        self.assertAlmostEqual(p["m7_ref"], 14.1, places=3)
        self.assertAlmostEqual(compute_m7_ref(p["trigger_bars"], p["weights"]), 14.1, places=3)

    def test_audit_json_matches_md(self) -> None:
        from despaghettify.tools.spaghetti_setup_audit import audit_setup

        root = Path(__file__).resolve().parents[3]
        rep = audit_setup(
            md_path=root / "despaghettify" / "spaghetti-setup.md",
            json_path=root / "despaghettify" / "spaghetti-setup.json",
            check_json_path=None,
        )
        self.assertTrue(rep["json_mirror_ok"], rep["drift_issues"])


if __name__ == "__main__":
    unittest.main()
