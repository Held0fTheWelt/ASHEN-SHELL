"""Version and status extraction — deterministic string scans only."""
from __future__ import annotations

from pathlib import Path

import contractify.tools.repo_paths as repo_paths
from contractify.tools.versioning import adr_declared_status, openapi_declared_version, read_openapi_version_from_file


def test_openapi_version_from_fixture_repo() -> None:
    root = repo_paths.repo_root()
    p = root / "docs" / "api" / "openapi.yaml"
    assert read_openapi_version_from_file(p) == "0.0.1"


def test_openapi_declared_version_parses_info_block() -> None:
    text = "openapi: 3.0.3\ninfo:\n  title: T\n  version: 2.4.0\npaths: {}\n"
    assert openapi_declared_version(text) == "2.4.0"


def test_adr_status_parses_markdown() -> None:
    head = "# ADR\n\n**Status**: Deprecated\n\nBody.\n"
    assert adr_declared_status(head) == "deprecated"
