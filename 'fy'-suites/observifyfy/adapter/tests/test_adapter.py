from __future__ import annotations

from pathlib import Path

from observifyfy.adapter.service import ObservifyfyAdapter


def test_observifyfy_adapter_init_and_audit(tmp_path: Path) -> None:
    (tmp_path / "README.md").write_text("x\n", encoding="utf-8")
    (tmp_path / "pyproject.toml").write_text("[project]\nname=\"x\"\n", encoding="utf-8")
    (tmp_path / "fy_governance_enforcement.yaml").write_text("ok: true\n", encoding="utf-8")
    (tmp_path / ".fydata").mkdir()
    for name in ["requirements.txt", "requirements-dev.txt", "requirements-test.txt"]:
        (tmp_path / name).write_text("# stub\n", encoding="utf-8")
    suite = tmp_path / "observifyfy"
    for rel in ["adapter", "tools", "reports", "state", "templates"]:
        (suite / rel).mkdir(parents=True, exist_ok=True)
    (suite / "README.md").write_text("# observifyfy\n", encoding="utf-8")
    (suite / "adapter" / "service.py").write_text("class Service: pass\n", encoding="utf-8")
    (suite / "adapter" / "cli.py").write_text("def main():\n    return 0\n", encoding="utf-8")
    adapter = ObservifyfyAdapter(tmp_path)
    init_payload = adapter.init(str(tmp_path))
    assert init_payload["ok"] is True
    audit_payload = adapter.audit(str(tmp_path))
    assert audit_payload["ok"] is True
