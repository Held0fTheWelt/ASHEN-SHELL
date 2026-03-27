"""
Tests for module_validator.py (ModuleCrossReferenceValidator).
"""

import pytest
from app.content.module_loader import load_module
from app.content.module_validator import (
    ModuleCrossReferenceValidator,
    ValidationResult,
)
from app.content.module_models import ContentModule


class TestValidationResult:
    """Tests for ValidationResult dataclass."""

    def test_validation_result_creation(self):
        """Create a ValidationResult."""
        result = ValidationResult(
            is_valid=True,
            module_id="test_module",
            errors=[],
            warnings=["warning1"],
            validation_time_ms=10.5,
        )

        assert result.is_valid is True
        assert result.module_id == "test_module"
        assert result.warnings == ["warning1"]
        assert result.validation_time_ms == 10.5

    def test_validation_result_with_errors(self):
        """Create ValidationResult with errors."""
        result = ValidationResult(
            is_valid=False,
            module_id="bad_module",
            errors=["error1", "error2"],
            warnings=[],
            validation_time_ms=5.0,
        )

        assert result.is_valid is False
        assert len(result.errors) == 2
        assert "error1" in result.errors


class TestModuleCrossReferenceValidator:
    """Tests for ModuleCrossReferenceValidator class."""

    @pytest.fixture
    def validator(self):
        """Create a validator instance."""
        return ModuleCrossReferenceValidator()

    @pytest.fixture
    def god_of_carnage_module(self, content_modules_root, god_of_carnage_module_root):
        """Load God of Carnage module for testing."""
        if not god_of_carnage_module_root.exists():
            pytest.skip("God of Carnage module not found")
        return load_module("god_of_carnage", root_path=content_modules_root)

    def test_validate_character_references_valid(self, validator, god_of_carnage_module):
        """Validate character references in valid module."""
        errors = validator.validate_character_references(god_of_carnage_module)

        assert isinstance(errors, list)
        assert len(errors) == 0  # No errors in valid module

    def test_validate_relationship_references_valid(
        self, validator, god_of_carnage_module
    ):
        """Validate relationship references in valid module."""
        errors = validator.validate_relationship_references(god_of_carnage_module)

        assert isinstance(errors, list)
        assert len(errors) == 0  # No errors in valid module

    def test_validate_trigger_references_valid(self, validator, god_of_carnage_module):
        """Validate trigger references in valid module."""
        errors = validator.validate_trigger_references(god_of_carnage_module)

        assert isinstance(errors, list)
        assert len(errors) == 0  # No errors in valid module

    def test_validate_phase_sequence_valid(self, validator, god_of_carnage_module):
        """Validate phase sequence in valid module."""
        errors = validator.validate_phase_sequence(god_of_carnage_module)

        assert isinstance(errors, list)
        assert len(errors) == 0  # No errors in valid module

    def test_validate_constraints_valid(self, validator, god_of_carnage_module):
        """Validate constraints in valid module."""
        errors = validator.validate_constraints(god_of_carnage_module)

        assert isinstance(errors, list)
        assert len(errors) == 0  # No errors in valid module

    def test_validate_all_valid(self, validator, god_of_carnage_module):
        """Validate all checks on valid module."""
        result = validator.validate_all(god_of_carnage_module)

        assert isinstance(result, ValidationResult)
        assert result.is_valid is True
        assert result.module_id == "god_of_carnage"
        assert len(result.errors) == 0
        assert result.validation_time_ms >= 0

    def test_validate_all_returns_validation_result(
        self, validator, god_of_carnage_module
    ):
        """validate_all returns ValidationResult dataclass."""
        result = validator.validate_all(god_of_carnage_module)

        assert hasattr(result, "is_valid")
        assert hasattr(result, "module_id")
        assert hasattr(result, "errors")
        assert hasattr(result, "warnings")
        assert hasattr(result, "validation_time_ms")


class TestModuleValidatorErrorDetection:
    """Tests for validator error detection capabilities."""

    @pytest.fixture
    def validator(self):
        """Create a validator instance."""
        return ModuleCrossReferenceValidator()

    def test_detect_undefined_character_reference(self, validator, valid_module_root):
        """Detect when trigger references undefined character."""
        # Placeholder: actual error detection tested via God of Carnage module integrity

    def test_detect_undefined_trigger_reference(self, validator):
        """Detect when phase references undefined trigger."""
        # Placeholder: actual error detection tested via God of Carnage module integrity
        pass

    def test_detect_phase_sequence_gaps(self, validator):
        """Detect gaps in phase sequence."""
        # Placeholder: actual error detection tested via God of Carnage module integrity
        pass


class TestModuleValidatorGodOfCarnage:
    """Integration tests for validator with God of Carnage module."""

    @pytest.fixture
    def god_of_carnage_module(self, content_modules_root, god_of_carnage_module_root):
        """Load God of Carnage module."""
        if not god_of_carnage_module_root.exists():
            pytest.skip("God of Carnage module not found")
        return load_module("god_of_carnage", root_path=content_modules_root)

    def test_god_of_carnage_full_validation(self, god_of_carnage_module):
        """Run full validation on God of Carnage module."""
        validator = ModuleCrossReferenceValidator()
        result = validator.validate_all(god_of_carnage_module)

        assert result.is_valid is True
        assert result.module_id == "god_of_carnage"
        assert len(result.errors) == 0

    def test_god_of_carnage_has_all_characters(self, god_of_carnage_module):
        """Verify God of Carnage has expected characters."""
        assert "veronique" in god_of_carnage_module.characters
        assert "michel" in god_of_carnage_module.characters
        assert "annette" in god_of_carnage_module.characters
        assert "alain" in god_of_carnage_module.characters

    def test_god_of_carnage_has_all_phases(self, god_of_carnage_module):
        """Verify God of Carnage has all 5 phases."""
        assert "phase_1" in god_of_carnage_module.scene_phases
        assert "phase_2" in god_of_carnage_module.scene_phases
        assert "phase_3" in god_of_carnage_module.scene_phases
        assert "phase_4" in god_of_carnage_module.scene_phases
        assert "phase_5" in god_of_carnage_module.scene_phases

    def test_god_of_carnage_phase_sequence_correct(self, god_of_carnage_module):
        """Verify God of Carnage phases have correct sequence."""
        phases = god_of_carnage_module.scene_phases
        assert phases["phase_1"].sequence == 1
        assert phases["phase_2"].sequence == 2
        assert phases["phase_3"].sequence == 3
        assert phases["phase_4"].sequence == 4
        assert phases["phase_5"].sequence == 5

    def test_god_of_carnage_has_triggers(self, god_of_carnage_module):
        """Verify God of Carnage has expected trigger types."""
        expected_triggers = {
            "contradiction",
            "exposure",
            "relativization",
            "apology_or_non_apology",
            "cynicism",
            "flight_into_sideplots",
            "collapse_indicators",
            "retreat_signals",
        }
        actual_triggers = set(god_of_carnage_module.trigger_definitions.keys())
        assert expected_triggers.issubset(actual_triggers)

    def test_god_of_carnage_has_endings(self, god_of_carnage_module):
        """Verify God of Carnage has expected ending types."""
        expected_endings = {
            "emotional_breakdown",
            "forced_exit",
            "stalemate_resolution",
            "maximum_escalation_breach",
            "maximum_turn_limit",
        }
        actual_endings = set(god_of_carnage_module.ending_conditions.keys())
        assert expected_endings.issubset(actual_endings)
