"""Fixtures for model_governance tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.content.module_loader import load_module


@pytest.fixture
def content_modules_root() -> Path:
    """Path to content/modules directory at project root."""
    backend_dir = Path(__file__).parent.parent.parent
    project_root = backend_dir.parent
    return project_root / "content" / "modules"


@pytest.fixture
def god_of_carnage_module_root(content_modules_root: Path) -> Path:
    """Path to god_of_carnage module directory."""
    return content_modules_root / "god_of_carnage"


@pytest.fixture
def god_of_carnage_module(content_modules_root: Path):
    """Load the god_of_carnage ContentModule."""
    return load_module("god_of_carnage", root_path=content_modules_root)


@pytest.fixture
def test_modules_root(tmp_path: Path) -> Path:
    """Temporary directory for test modules."""
    return tmp_path / "test_modules"


@pytest.fixture
def valid_module_root(test_modules_root: Path) -> Path:
    """Create a valid test module structure."""
    module_root = test_modules_root / "test_valid_module"
    module_root.mkdir(parents=True, exist_ok=True)
    module_yaml = module_root / "module.yaml"
    module_yaml.write_text(
        """module_id: test_valid_module
title: Test Valid Module
version: 0.1.0
contract_version: 1.0.0
"""
    )
    return module_root
