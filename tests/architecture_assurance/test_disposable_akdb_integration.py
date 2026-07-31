from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest


ROOT = Path(__file__).resolve().parents[2]
LOCK = json.loads(
    (ROOT / "tools" / "architecture_assurance" / "akdb.lock.json").read_text(
        encoding="utf-8"
    )
)


def _akdb_root() -> Path | None:
    environment_root = (
        Path(os.environ["AKDB_SOURCE_ROOT"])
        if os.environ.get("AKDB_SOURCE_ROOT")
        else None
    )
    candidates = [
        environment_root,
        ROOT / ".external" / "ArchitecturalKnowledgeDB",
        ROOT.parent / "ArchitecturalKnowledgeDB",
        ROOT.parent / "TinyToolDevelopment" / "ArchitecturalKnowledgeDB",
        ROOT.parent.parent / "ArchitecturalKnowledgeDB",
    ]
    return next(
        (
            path.resolve()
            for path in candidates
            if path is not None
            and (path / "architectural_knowledge_db" / "cli.py").is_file()
        ),
        None,
    )


def _tree_state(root: Path) -> dict[str, tuple[int, int]]:
    return {
        path.relative_to(root).as_posix(): (path.stat().st_size, path.stat().st_mtime_ns)
        for path in root.rglob("*")
        if path.is_file() and ".git" not in path.relative_to(root).parts
    }


def _tracked_state(root: Path) -> dict[str, str]:
    tracked = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z"],
        check=True,
        capture_output=True,
    ).stdout.decode("utf-8").split("\0")
    return {
        relative: hashlib.sha256((root / relative).read_bytes()).hexdigest()
        for relative in tracked
        if relative and (root / relative).is_file()
    }


def _persistent_state(root: Path) -> dict[str, tuple[int, int]]:
    state: dict[str, tuple[int, int]] = {}
    for name in (".akdb", "exports", "document-fallback"):
        path = root / name
        if path.is_dir():
            state.update(
                {
                    f"{name}/{relative}": value
                    for relative, value in _tree_state(path).items()
                }
            )
    return state


def _digest(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(path for path in root.rglob("*") if path.is_file()):
        digest.update(path.relative_to(root).as_posix().encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


@pytest.mark.integration
def test_external_akdb_round_trip_is_strictly_disposable(tmp_path: Path) -> None:
    akdb_root = _akdb_root()
    if akdb_root is None:
        pytest.skip("pinned external AKDB checkout is unavailable")

    revision = subprocess.run(
        ["git", "-C", str(akdb_root), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    assert revision == LOCK["commit"]
    before_tree = _tree_state(akdb_root)
    before_tracked = _tracked_state(akdb_root)
    before_persistent = _persistent_state(akdb_root)

    source = tmp_path / "source"
    architecture = source / "docs" / "architecture"
    uml = source / "UML"
    architecture.mkdir(parents=True)
    uml.mkdir(parents=True)
    (architecture / "START-HERE.md").write_text(
        "# Disposable Better Tomorrow fixture\n", encoding="utf-8"
    )
    (uml / "context.puml").write_text(
        "@startuml\nrectangle BetterTomorrow\n@enduml\n", encoding="utf-8"
    )

    data_root = tmp_path / "akdb-data"
    environment = os.environ.copy()
    environment.update(
        {
            "PYTHONPATH": os.pathsep.join(
                [str(akdb_root), environment.get("PYTHONPATH", "")]
            ).rstrip(os.pathsep),
            "AKDB_DATA_ROOT": str(data_root),
            "AKDB_DATABASE_PATH": str(data_root / "integration.sqlite"),
            "AKDB_STORAGE_MODE": "sqlite",
            "AKDB_STORAGE_CASCADE": "0",
            "AKDB_DOCUMENT_BACKUP_ROOT": str(data_root / "document-fallback"),
            "AKDB_AUTO_EXPORT": "0",
            "AKDB_QDRANT_URL": "",
            "AKDB_DB_URL": "",
            "PYTHONDONTWRITEBYTECODE": "1",
            # Explicit disposable write authority (AKDB CLI is read-only by default).
            "AKDB_CLI_WRITE": "1",
            "AKDB_CLI_ACTOR": "human:test-harness",
            "AKDB_CLI_CAPABILITIES": "akdb:cli:write",
            "AKDB_CLI_PROJECTS": "better-tomorrow-it",
        }
    )

    def run(*arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-m", "architectural_knowledge_db.cli", *arguments],
            cwd=source,
            env=environment,
            check=True,
            capture_output=True,
            text=True,
        )

    run("project", "add", "--id", "better-tomorrow-it", "--name", "BT disposable")
    run(
        "database",
        "ingest-documents",
        "--project",
        "better-tomorrow-it",
        "--source-root",
        str(source),
        "--no-scan-git",
    )
    first_export = tmp_path / "export-first"
    second_export = tmp_path / "export-second"
    run(
        "canon",
        "export",
        "--project",
        "better-tomorrow-it",
        "--folder",
        str(first_export),
    )
    run(
        "canon",
        "export",
        "--project",
        "better-tomorrow-it",
        "--folder",
        str(second_export),
    )
    assert _digest(first_export) == _digest(second_export)
    run(
        "canon",
        "verify",
        "--project",
        "better-tomorrow-it",
        "--folder",
        str(source),
    )

    assert (data_root / "integration.sqlite").is_file()
    assert all(path.is_relative_to(tmp_path) for path in data_root.rglob("*"))
    assert _tree_state(akdb_root) == before_tree
    assert _tracked_state(akdb_root) == before_tracked
    assert _persistent_state(akdb_root) == before_persistent
