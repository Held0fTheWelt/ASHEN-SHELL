from __future__ import annotations

from pathlib import Path

from tools.architecture_assurance.canon import (
    export_canon,
    tree_digest,
    write_canon_manifest,
)


def test_canon_manifest_export_and_dry_run_are_idempotent(tmp_path: Path) -> None:
    source = tmp_path / "docs" / "architecture.md"
    source.parent.mkdir(parents=True)
    source.write_bytes(b"# Architecture\r\n")
    config = {
        "project_id": "better-tomorrow",
        "repository_id": "fixture",
        "canonical_files": ["docs/architecture.md"],
        "subsystems": [],
    }
    manifest = tmp_path / "canon.json"
    first = write_canon_manifest(config, tmp_path, manifest)
    assert first["action"] == "write"
    assert write_canon_manifest(config, tmp_path, manifest)["action"] == "unchanged"

    dry_destination = tmp_path / "dry-export"
    dry = export_canon(manifest, tmp_path, dry_destination, dry_run=True)
    assert dry["actions"] == [
        {"path": "docs/architecture.md", "action": "would_write"}
    ]
    assert not dry_destination.exists()

    destination = tmp_path / "export"
    first_export = export_canon(manifest, tmp_path, destination)
    second_export = export_canon(manifest, tmp_path, destination)
    assert first_export["actions"][0]["action"] == "write"
    assert second_export["actions"][0]["action"] == "unchanged"
    assert (destination / "docs" / "architecture.md").read_bytes() == (
        b"# Architecture\n"
    )
    assert tree_digest(destination, ["docs/architecture.md"]) == tree_digest(
        tmp_path, ["docs/architecture.md"]
    )


def test_canon_text_hash_is_line_ending_neutral(tmp_path: Path) -> None:
    from tools.architecture_assurance.canon import sha256_file

    lf = tmp_path / "lf.md"
    crlf = tmp_path / "crlf.md"
    lf.write_bytes(b"# A\nB\n")
    crlf.write_bytes(b"# A\r\nB\r\n")

    assert sha256_file(lf) == sha256_file(crlf)
