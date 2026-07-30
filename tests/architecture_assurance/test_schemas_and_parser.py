from __future__ import annotations

from pathlib import Path
import subprocess

import pytest

from tools.architecture_assurance.discovery import resolve_declared_path
from tools.architecture_assurance.sad_parser import parse_sad
from tools.architecture_assurance.schemas import (
    ANCHOR_SCHEMA_VERSION,
    BINDINGS_SCHEMA_VERSION,
    SchemaValidationError,
    validate_manifest,
)


def _manifest(entry: dict) -> dict:
    return {
        "schema_version": BINDINGS_SCHEMA_VERSION,
        "subsystem": "sample",
        "sad_path": "docs/architecture/sample/architecture.md",
        "lanes": ["python"],
        "building_blocks": [entry],
        "decisions": [],
        "discovered_units": [],
        "representation_map": {},
        "out_of_scope": {},
        "required_views": [],
    }


def test_bound_claim_requires_a_real_anchor() -> None:
    with pytest.raises(SchemaValidationError, match="requires at least one anchor"):
        validate_manifest(
            _manifest(
                {
                    "id": "B-runtime",
                    "title": "Runtime",
                    "status": "Implemented",
                    "state": "bound",
                    "anchors": [],
                }
            )
        )


def test_claimed_only_cannot_smuggle_an_anchor() -> None:
    with pytest.raises(SchemaValidationError, match="cannot carry anchors"):
        validate_manifest(
            _manifest(
                {
                    "id": "B-runtime",
                    "title": "Runtime",
                    "status": "Implemented",
                    "state": "claimed_only",
                    "anchors": [
                        {
                            "schema_version": ANCHOR_SCHEMA_VERSION,
                            "kind": "python",
                            "file": "runtime.py",
                            "line": 1,
                        }
                    ],
                }
            )
        )


def test_every_better_tomorrow_sad_has_arc42_sections_1_through_12() -> None:
    root = Path(__file__).resolve().parents[2]
    paths = sorted(root.glob("docs/architecture/**/architecture.md"))
    assert len(paths) == 16
    for path in paths:
        sad = parse_sad(path.read_text(encoding="utf-8-sig"))
        assert sad.section_numbers == tuple(range(1, 13)), path


def test_directory_anchor_ignores_test_runner_state(tmp_path: Path) -> None:
    source = tmp_path / "service"
    cache = source / ".pytest_cache"
    cache.mkdir(parents=True)
    (cache / "README.md").write_text("ephemeral\n", encoding="utf-8")
    (source / "__init__.py").write_text("SERVICE = True\n", encoding="utf-8")

    path, declared = resolve_declared_path("service/", tmp_path, [])

    assert path == (source / "__init__.py").resolve()
    assert declared == "service/"


def test_declared_path_resolution_excludes_git_ignored_evidence(
    tmp_path: Path,
) -> None:
    subprocess.run(
        ["git", "init", "--quiet"],
        cwd=tmp_path,
        check=True,
        capture_output=True,
    )
    (tmp_path / ".gitignore").write_text(
        ".env\n.claude/\nbackend/instance/\n",
        encoding="utf-8",
    )
    (tmp_path / ".env").write_text("SECRET=local\n", encoding="utf-8")
    (tmp_path / ".env.example").write_text("SECRET=\n", encoding="utf-8")
    real_gate = tmp_path / "tests" / "test_real_gate.py"
    real_gate.parent.mkdir()
    real_gate.write_text("def test_real(): pass\n", encoding="utf-8")
    shadow_gate = (
        tmp_path
        / ".claude"
        / "worktrees"
        / "coverage"
        / "tests"
        / "test_shadow_gate.py"
    )
    shadow_gate.parent.mkdir(parents=True)
    shadow_gate.write_text("def test_shadow(): pass\n", encoding="utf-8")

    ignored_path, _ = resolve_declared_path(".env", tmp_path, [])
    example_path, _ = resolve_declared_path(".env.example", tmp_path, [])
    wildcard_path, _ = resolve_declared_path("**/test_*gate.py", tmp_path, [])

    assert ignored_path is None
    assert example_path == (tmp_path / ".env.example").resolve()
    assert wildcard_path == real_gate.resolve()
