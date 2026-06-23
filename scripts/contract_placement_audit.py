#!/usr/bin/env python3
"""Audit contract placement under docs/architecture/.

Canonical contracts live under docs/architecture/contracts/ (and boundaries/).
The architecture root must not contain legacy contract stubs or mvp_definition redirects.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ARCH_ROOT = REPO_ROOT / "docs" / "architecture"
CONTRACTS_ROOT = ARCH_ROOT / "contracts"
RUNTIME_CONTRACTS = CONTRACTS_ROOT / "runtime"

ALLOWED_ROOT_MARKDOWN = frozenset(
    {
        "README.md",
        "START-HERE.md",
        "QUALITY-STANDARD.md",
        "DOC-HEALTH.md",
    }
)

STRAY_ROOT_BASENAMES = frozenset(
    {
        "mvp_definition.md",
        "session_runtime_contract.md",
        "ai_story_contract.md",
        "god_of_carnage_module_contract.md",
        "god_of_carnage_current_contract.md",
        "observability_traceability_contract.md",
        "runtime_profile_vs_content_contract.md",
        "current_service_boundaries.md",
    }
)

STRAY_NAME_RE = re.compile(r"contract", re.I)


def find_stray_root_markdown() -> list[Path]:
    stray: list[Path] = []
    for path in sorted(ARCH_ROOT.glob("*.md")):
        name = path.name
        if name in ALLOWED_ROOT_MARKDOWN:
            continue
        if name in STRAY_ROOT_BASENAMES or STRAY_NAME_RE.search(name):
            stray.append(path)
    return stray


def runtime_contract_files() -> list[str]:
    names: list[str] = []
    for path in sorted(RUNTIME_CONTRACTS.rglob("*.md")):
        if path.name == "README.md":
            continue
        names.append(path.relative_to(RUNTIME_CONTRACTS).as_posix())
    return names


def normative_index_runtime_paths(index_text: str) -> list[str]:
    found: list[str] = []
    pattern = re.compile(
        r"(?:docs/architecture/contracts/runtime/|architecture/contracts/runtime/)([^\s`)#]+)"
    )
    for match in pattern.finditer(index_text):
        found.append(match.group(1))
    return sorted(set(found))


def audit() -> list[str]:
    errors: list[str] = []
    stray = find_stray_root_markdown()
    for path in stray:
        errors.append(
            f"stray architecture root markdown: {path.relative_to(REPO_ROOT).as_posix()} "
            f"(move to docs/architecture/contracts/ or absorb into SAD)"
        )

    index_path = REPO_ROOT / "docs" / "dev" / "contracts" / "normative-contracts-index.md"
    if index_path.is_file():
        index_text = index_path.read_text(encoding="utf-8")
        on_disk = set(runtime_contract_files())
        in_index = set(normative_index_runtime_paths(index_text))
        missing_in_index = sorted(on_disk - in_index)
        missing_on_disk = sorted(in_index - on_disk)
        if missing_in_index:
            errors.append(
                "normative-contracts-index missing runtime files: " + ", ".join(missing_in_index)
            )
        if missing_on_disk:
            errors.append(
                "normative-contracts-index references missing runtime files: "
                + ", ".join(missing_on_disk)
            )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit contract placement under docs/architecture/.")
    parser.add_argument("--check", action="store_true", help="Exit 1 if placement violations exist.")
    parser.add_argument("--list-stray", action="store_true", help="Print stray root markdown paths.")
    args = parser.parse_args()

    stray = find_stray_root_markdown()
    if args.list_stray:
        for path in stray:
            print(path.relative_to(REPO_ROOT).as_posix())
        return 0

    errors = audit()
    if errors:
        for err in errors:
            print(err, file=sys.stderr)
        return 1 if args.check else 0
    print("OK: contract placement clean")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
