from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str], cwd: Path, env: dict[str, str], acceptable: set[int] | None = None) -> int:
    acceptable = acceptable or {0}
    print("$", " ".join(cmd))
    proc = subprocess.run(cmd, cwd=str(cwd), env=env)
    if proc.returncode in acceptable:
        return 0
    return proc.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a conservative FY governance cycle for the current package.")
    parser.add_argument("--repo-root", default=".", help="Package root")
    parser.add_argument("--out-dir", default="validation/fy_reports", help="Output directory")
    args = parser.parse_args()

    root = Path(args.repo_root).resolve()
    out_dir = (root / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    suites_parent = root / "'fy'-suites"
    env = os.environ.copy()
    env["PYTHONPATH"] = str(suites_parent) + os.pathsep + env.get("PYTHONPATH", "")
    env["DESPAG_REPO_ROOT"] = str(root)

    commands: list[tuple[list[str], set[int]]] = [
        ([sys.executable, "-m", "contractify.tools", "audit", "--json", "--out", str(out_dir / "contractify_audit.json")], {0}),
        ([sys.executable, "-m", "docify.tools", "audit", "--json", "--exit-zero", "--out", str(out_dir / "docify_audit.json")], {0, 2}),
        ([sys.executable, "-m", "despaghettify.tools", "setup-audit", "--setup-md", str(root / "'fy'-suites/despaghettify/spaghetti-setup.md"), "--setup-json", str(root / "'fy'-suites/despaghettify/spaghetti-setup.json"), "--json"], {0}),
    ]

    worst = 0
    for cmd, acceptable in commands:
        code = run(cmd, cwd=root, env=env, acceptable=acceptable)
        worst = max(worst, code)
    return worst


if __name__ == "__main__":
    raise SystemExit(main())
