"""Wave 2 write-surface resource model tests."""
from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from tools.architecture_assurance.drift_edges import (
    load_drift_edge_catalog,
    validate_authoritative_write_surfaces,
)


ROOT = Path(__file__).resolve().parents[2]
EDGE_CATALOG = ROOT / "tools" / "architecture_assurance" / "drift_edge_catalog.json"


def _findings(catalog: dict) -> list[dict]:
    return validate_authoritative_write_surfaces(
        catalog,
        repo_root=ROOT,
        catalog_path=EDGE_CATALOG.relative_to(ROOT).as_posix(),
    )


def test_six_persistence_resources_are_declared() -> None:
    catalog = load_drift_edge_catalog(EDGE_CATALOG)
    resources = {surface["resource"] for surface in catalog["write_surfaces"]}
    assert resources == {
        "live_story_session",
        "live_run_instance",
        "branching_tree",
        "branch_timeline",
        "callback_web",
        "consequence_cascade",
    }
    assert _findings(catalog) == []


def test_route_cannot_write_store_directly(tmp_path: Path) -> None:
    src = tmp_path / "src"
    src.mkdir()
    (src / "manager.py").write_text(
        "class M:\n"
        "    def attach_runtime_profile_handoff(self, instance, handoff):\n"
        "        self.store.save(instance)\n",
        encoding="utf-8",
    )
    (src / "route.py").write_text(
        "def create_run(manager, instance):\n"
        "    manager.store.save(instance)\n",
        encoding="utf-8",
    )
    catalog = {
        "authority_invariants": [{"resource": "live_run_instance"}],
        "write_surfaces": [
            {
                "id": "live-run",
                "resource": "live_run_instance",
                "call": "self.store.save",
                "store_attrs": ["store"],
                "scan_roots": ["src"],
                "allowed_callsites": [
                    {"path": "src/manager.py", "symbol": "attach_runtime_profile_handoff"}
                ],
                "minimum_calls": 1,
                "maximum_calls": 2,
            }
        ],
    }
    findings = validate_authoritative_write_surfaces(
        catalog, repo_root=tmp_path, catalog_path="drift.json"
    )
    assert any(
        f["rule_id"] == "BT-AUTHORITY-WRITE-CALLSITE" and f["path"] == "src/route.py"
        for f in findings
    )


def test_alias_write_is_detected(tmp_path: Path) -> None:
    src = tmp_path / "src"
    src.mkdir()
    (src / "allowed.py").write_text(
        "class Manager:\n"
        "    def _persist_session(self, session):\n"
        "        self._session_store.save(session.id, {})\n",
        encoding="utf-8",
    )
    (src / "alias.py").write_text(
        "class Bypass:\n"
        "    def sneak(self, session):\n"
        "        s = self._session_store\n"
        "        s.save(session.id, {})\n",
        encoding="utf-8",
    )
    catalog = {
        "authority_invariants": [{"resource": "live_story_session"}],
        "write_surfaces": [
            {
                "id": "session-save",
                "resource": "live_story_session",
                "call": "self._session_store.save",
                "store_attrs": ["_session_store"],
                "scan_roots": ["src"],
                "allowed_callsites": [
                    {"path": "src/allowed.py", "symbol": "_persist_session"}
                ],
                "minimum_calls": 1,
                "maximum_calls": 2,
            }
        ],
    }
    findings = validate_authoritative_write_surfaces(
        catalog, repo_root=tmp_path, catalog_path="drift.json"
    )
    assert any(
        f["rule_id"] == "BT-AUTHORITY-WRITE-CALLSITE" and f["path"] == "src/alias.py"
        for f in findings
    )


def test_second_writer_breaks_gate() -> None:
    catalog = deepcopy(load_drift_edge_catalog(EDGE_CATALOG))
    run_surface = next(s for s in catalog["write_surfaces"] if s["resource"] == "live_run_instance")
    run_surface["maximum_calls"] = 1
    findings = _findings(catalog)
    assert any(
        f["rule_id"] == "BT-AUTHORITY-WRITE-CONFLICT" and f["unit"] == run_surface["id"]
        for f in findings
    )
