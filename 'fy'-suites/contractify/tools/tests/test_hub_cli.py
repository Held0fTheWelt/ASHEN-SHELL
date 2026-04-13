import json

import contractify.tools.repo_paths as repo_paths
from contractify.tools.hub_cli import main


def test_discover_writes_json() -> None:
    root = repo_paths.repo_root()
    out_path = root / "'fy'-suites" / "contractify" / "reports" / "_pytest_contractify_discover.json"
    out_arg = out_path.relative_to(root).as_posix()
    try:
        code = main(["discover", "--out", out_arg, "--quiet", "--max-contracts", "15"])
        assert code == 0
        data = json.loads(out_path.read_text(encoding="utf-8"))
        assert "contracts" in data
        assert len(data["contracts"]) >= 1
    finally:
        if out_path.is_file():
            out_path.unlink()
