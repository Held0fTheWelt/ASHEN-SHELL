"""
Tests for module_loader.py (ModuleFileLoader and entry point).
"""

import pytest
from pathlib import Path
from app.content.module_loader import (
    ModuleFileLoader,
    ModuleStructureValidator,
    load_module,
)
from app.content.module_exceptions import (
    ModuleLoadError,
    ModuleNotFoundError,
    ModuleFileReadError,
    ModuleParseError,
    ModuleStructureError,
)
from app.content.module_models import ContentModule


class TestModuleFileLoader:
    """Tests for ModuleFileLoader class."""

    def test_load_file_valid_yaml(self, valid_module_root):
        """Load a valid YAML file."""
        loader = ModuleFileLoader()
        module_yaml = valid_module_root / "module.yaml"

        data = loader.load_file(module_yaml)

        assert isinstance(data, dict)
        assert data["module_id"] == "test_module"
        assert data["title"] == "Test Module"

    def test_load_file_nonexistent(self):
        """Loading nonexistent file raises ModuleFileReadError."""
        loader = ModuleFileLoader()

        with pytest.raises(ModuleFileReadError):
            loader.load_file(Path("/nonexistent/file.yaml"))

    def test_load_file_malformed_yaml(self, malformed_yaml_root):
        """Loading malformed YAML raises ModuleParseError."""
        loader = ModuleFileLoader()
        malformed_file = malformed_yaml_root / "module.yaml"

        with pytest.raises(ModuleParseError):
            loader.load_file(malformed_file)

    def test_load_all_module_files_valid(self, valid_module_root):
        """Load all files in a valid module directory."""
        loader = ModuleFileLoader()

        files = loader.load_all_module_files(valid_module_root)

        assert isinstance(files, dict)
        assert "module" in files
        assert "characters" in files
        assert "relationships" in files
        assert files["module"]["module_id"] == "test_module"

    def test_load_all_module_files_nonexistent_dir(self):
        """Loading from nonexistent directory raises ModuleFileReadError."""
        loader = ModuleFileLoader()

        with pytest.raises(ModuleFileReadError):
            loader.load_all_module_files(Path("/nonexistent/dir"))


class TestModuleStructureValidator:
    """Tests for ModuleStructureValidator class."""

    def test_validate_structure_valid(self, valid_module_root):
        """Validate valid module structure."""
        loader = ModuleFileLoader()
        raw_data = loader.load_all_module_files(valid_module_root)

        validator = ModuleStructureValidator()
        module = validator.validate_structure(raw_data)

        assert isinstance(module, ContentModule)
        assert module.metadata.module_id == "test_module"
        assert len(module.characters) == 2

    def test_validate_structure_missing_required_field(self, invalid_module_root):
        """Validate fails when required fields missing."""
        loader = ModuleFileLoader()
        raw_data = loader.load_all_module_files(invalid_module_root)

        validator = ModuleStructureValidator()

        with pytest.raises(ModuleStructureError) as exc_info:
            validator.validate_structure(raw_data)

        # Should contain validation errors
        assert exc_info.value.errors
        assert len(exc_info.value.errors) > 0

    def test_validate_structure_invalid_type(self):
        """Validate fails when field has wrong type."""
        validator = ModuleStructureValidator()
        invalid_data = {
            "module": {
                "module_id": "test",
                "title": "Test",
                "version": "0.1.0",
                "contract_version": "0.2.0",
                "content": {},
                "files": "not_a_list",  # Should be list
            }
        }

        with pytest.raises(ModuleStructureError):
            validator.validate_structure(invalid_data)


class TestLoadModuleEntryPoint:
    """Tests for load_module() entry point."""

    def test_load_module_valid(self, valid_module_root, test_modules_root):
        """Load a valid module by ID."""
        module = load_module("test_module", root_path=test_modules_root)

        assert isinstance(module, ContentModule)
        assert module.metadata.module_id == "test_module"

    def test_load_module_nonexistent(self, test_modules_root):
        """Loading nonexistent module raises ModuleNotFoundError."""
        with pytest.raises(ModuleNotFoundError):
            load_module("nonexistent_module", root_path=test_modules_root)

    def test_load_module_malformed_yaml(self, malformed_yaml_root, test_modules_root):
        """Loading module with malformed YAML raises ModuleParseError."""
        with pytest.raises(ModuleParseError):
            load_module("malformed_module", root_path=test_modules_root)

    def test_load_module_invalid_structure(self, invalid_module_root, test_modules_root):
        """Loading module with invalid structure raises ModuleStructureError."""
        with pytest.raises(ModuleStructureError):
            load_module("invalid_module", root_path=test_modules_root)

    def test_load_module_default_path(self, god_of_carnage_module_root):
        """Load module using default path (real God of Carnage module)."""
        if not god_of_carnage_module_root.exists():
            pytest.skip("God of Carnage module not found")

        # This should load the real God of Carnage module
        module = load_module("god_of_carnage")

        assert module.metadata.module_id == "god_of_carnage"
        assert len(module.characters) == 4  # Véronique, Michel, Annette, Alain
        assert "phase_1" in module.scene_phases


class TestModuleLoaderIntegration:
    """Integration tests for loader with real module structure."""

    def test_load_god_of_carnage_full(self, god_of_carnage_module_root):
        """Load and validate God of Carnage module."""
        if not god_of_carnage_module_root.exists():
            pytest.skip("God of Carnage module not found")

        loader = ModuleFileLoader()
        files = loader.load_all_module_files(god_of_carnage_module_root)

        # Should have all expected files
        assert "module" in files
        assert "characters" in files
        assert "relationships" in files
        assert "scenes" in files
        assert "transitions" in files
        assert "triggers" in files
        assert "endings" in files
        assert "escalation_axes" in files

        # Structure validation
        validator = ModuleStructureValidator()
        module = validator.validate_structure(files)

        assert module.metadata.module_id == "god_of_carnage"
        assert module.metadata.version == "0.1.0"
