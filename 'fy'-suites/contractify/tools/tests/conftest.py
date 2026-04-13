"""Hermetic test defaults: Contractify unit tests must not depend on a full World of Shadows checkout.

ZIP extracts and partial trees still run ``pytest`` here when ``repo_root()`` is patched to a
synthetic layout that satisfies ``discovery`` / ``drift_analysis`` / ``hub_cli`` expectations.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Iterator

import pytest


def _write_minimal_openapi(root: Path) -> str:
    body = (
        "openapi: 3.0.0\n"
        "info:\n"
        "  title: ContractifyTestAPI\n"
        "  version: '0.0.1'\n"
        "paths: {}\n"
    )
    p = root / "docs" / "api" / "openapi.yaml"
    p.parent.mkdir(parents=True, exist_ok=True)
    raw = body.encode("utf-8")
    p.write_bytes(raw)
    return hashlib.sha256(p.read_bytes()).hexdigest()


def build_minimal_contractify_test_repo(root: Path) -> Path:
    """Create a tiny repo tree that mirrors the discovery anchors Contractify expects."""
    root = root.resolve()
    (root / "pyproject.toml").write_text(
        '[project]\nname = "world-of-shadows-hub"\nversion = "0.0.0"\n',
        encoding="utf-8",
    )
    sha = _write_minimal_openapi(root)
    (root / "docs" / "dev" / "contracts").mkdir(parents=True, exist_ok=True)
    (root / "docs" / "technical").mkdir(parents=True, exist_ok=True)
    (root / "docs" / "technical" / "shared-runtime.md").write_text("# Shared\n", encoding="utf-8")
    (root / "docs" / "dev" / "contracts" / "normative-contracts-index.md").write_text(
        "# Normative contracts index\n\n**binding scope** test fixture. See also `openapi.yaml`.\n\n"
        "## Duplicate navigation stress (deterministic conflict fixture)\n"
        "| A | [one](../../technical/shared-runtime.md) |\n"
        "| B | [two](../../technical/shared-runtime.md) |\n",
        encoding="utf-8",
    )
    (root / "docs" / "dev" / "README.md").write_text(
        "See [Normative contracts index](contracts/normative-contracts-index.md).\n",
        encoding="utf-8",
    )
    manifest = {
        "generated_at": "2026-01-01T00:00:00+00:00",
        "openapi_path": "docs/api/openapi.yaml",
        "openapi_sha256": sha,
        "backend_api_prefix": "/api/v1",
        "master_collection": "postman/Master.postman_collection.json",
        "suites_dir": "postman/suites",
        "sub_suite_files": [],
    }
    (root / "postman").mkdir(parents=True, exist_ok=True)
    (root / "postman" / "postmanify-manifest.json").write_text(
        json.dumps(manifest, indent=2),
        encoding="utf-8",
    )
    fy = root / "'fy'-suites"
    (fy / "contractify").mkdir(parents=True, exist_ok=True)
    (fy / "contractify" / "README.md").write_text(
        "# Contractify\n\n**Normative** suite charter for tests.\n",
        encoding="utf-8",
    )
    (fy / "contractify" / "reports").mkdir(parents=True, exist_ok=True)
    (fy / "despaghettify").mkdir(parents=True, exist_ok=True)
    (fy / "despaghettify" / "spaghetti-setup.md").write_text(
        "## Normative specification\n\nCanonical contract for tooling.\n",
        encoding="utf-8",
    )
    (fy / "docify").mkdir(parents=True, exist_ok=True)
    (fy / "docify" / "README.md").write_text(
        "Default roots include `'fy'-suites/contractify` for self-governance.\n",
        encoding="utf-8",
    )
    (fy / "docify" / "tools").mkdir(parents=True, exist_ok=True)
    (fy / "docify" / "tools" / "python_documentation_audit.py").write_text(
        "DEFAULT_RELATIVE_ROOTS = (\n    \"'fy'-suites/contractify\",\n)\n",
        encoding="utf-8",
    )
    gov = root / "docs" / "governance"
    gov.mkdir(parents=True, exist_ok=True)
    (gov / "adr-0001-scene-identity.md").write_text(
        "# ADR 1\n\n**Status**: Accepted\n\nDecision about **scene identity** surface.\n",
        encoding="utf-8",
    )
    (gov / "adr-0002-runtime-authority.md").write_text(
        "# ADR 2\n\n**Status**: Accepted\n\n**Runtime authority** overlaps **scene identity** vocabulary.\n",
        encoding="utf-8",
    )
    (root / "docs" / "operations").mkdir(parents=True, exist_ok=True)
    (root / "docs" / "operations" / "OPERATIONAL_GOVERNANCE_RUNTIME.md").write_text(
        "# Ops\n\n**Normative** alignment with governance runtime controls.\n",
        encoding="utf-8",
    )
    (root / "schemas").mkdir(parents=True, exist_ok=True)
    (root / "schemas" / "sample_payload.json").write_text('{"type": "object"}\n', encoding="utf-8")
    return root


_MODULES_WITHOUT_REPO_PATCH = frozenset(
    {
        "contractify.tools.tests.test_models",
        "contractify.tools.tests.test_example_artifacts",
    }
)


@pytest.fixture(autouse=True)
def _hermetic_contractify_repo(request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Iterator[None]:
    """Patch ``repo_root()`` for every test module except pure unit tests."""
    if request.module.__name__ in _MODULES_WITHOUT_REPO_PATCH:
        yield
        return
    fake = build_minimal_contractify_test_repo(tmp_path)
    monkeypatch.setattr("contractify.tools.repo_paths.repo_root", lambda start=None: fake)
    monkeypatch.setattr("contractify.tools.hub_cli.repo_root", lambda start=None: fake)
    yield
