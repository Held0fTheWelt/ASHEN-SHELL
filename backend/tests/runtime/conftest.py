"""Fixtures for runtime tests."""

import pytest
from pathlib import Path


@pytest.fixture
def content_modules_root():
    """Path to content/modules directory."""
    return Path("content/modules")


@pytest.fixture
def god_of_carnage_module_root(content_modules_root):
    """Path to god_of_carnage module directory."""
    return content_modules_root / "god_of_carnage"


@pytest.fixture
def test_modules_root(tmp_path):
    """Temporary directory for test modules."""
    return tmp_path / "test_modules"


@pytest.fixture
def valid_module_root(test_modules_root):
    """Create a valid test module structure."""
    module_root = test_modules_root / "test_valid_module"
    module_root.mkdir(parents=True, exist_ok=True)

    # Create minimal valid module files
    module_yaml = module_root / "module.yaml"
    module_yaml.write_text(
        """module_id: test_valid_module
title: Test Valid Module
version: 0.1.0
contract_version: 1.0.0
"""
    )

    return module_root
