"""
Module loader for content modules.

Handles loading, parsing, and validating content modules from YAML files
in a structured module directory. Provides non-fail-fast validation that
collects all errors before raising exceptions.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from .module_exceptions import (
    ModuleFileReadError,
    ModuleNotFoundError,
    ModuleParseError,
    ModuleStructureError,
)
from .module_models import ContentModule


class ModuleFileLoader:
    """Handles reading and parsing YAML files from module directories.

    This loader is responsible for reading individual YAML files and loading
    all YAML files from a module directory structure. It handles YAML parsing
    errors and file I/O errors with appropriate exception context.
    """

    def load_file(self, path: Path) -> dict[str, Any]:
        """Load a single YAML file and return its contents.

        Args:
            path: Path to the YAML file to load.

        Returns:
            Dictionary containing the parsed YAML content.

        Raises:
            ModuleParseError: If the file contains invalid YAML.
        """
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = yaml.safe_load(f)
                # safe_load returns None for empty files, convert to empty dict
                return content if content is not None else {}
        except yaml.YAMLError as e:
            raise ModuleParseError(
                message="Failed to parse YAML file",
                module_id="unknown",
                file_path=str(path),
                errors=[str(e)],
            )

    def load_all_module_files(self, module_root: Path) -> dict[str, dict]:
        """Load all YAML files from a module directory.

        Scans the module root directory for all .yaml files and loads each one,
        returning a dictionary mapping filenames (without extension) to their
        parsed contents.

        Args:
            module_root: Path to the root directory of the module.

        Returns:
            Dictionary mapping filename (without .yaml) to parsed content.

        Raises:
            ModuleFileReadError: If the directory doesn't exist or cannot be read.
            ModuleParseError: If any YAML file fails to parse.
        """
        if not module_root.exists():
            raise ModuleFileReadError(
                message=f"Module directory does not exist",
                module_id="unknown",
                file_path=str(module_root),
            )

        if not module_root.is_dir():
            raise ModuleFileReadError(
                message=f"Module path is not a directory",
                module_id="unknown",
                file_path=str(module_root),
            )

        try:
            yaml_files = sorted(module_root.glob("*.yaml"))
        except (PermissionError, OSError) as e:
            raise ModuleFileReadError(
                message=f"Failed to read module directory",
                module_id="unknown",
                file_path=str(module_root),
                errors=[str(e)],
            )

        result = {}
        for yaml_file in yaml_files:
            filename = yaml_file.stem  # filename without .yaml extension
            result[filename] = self.load_file(yaml_file)

        return result


class ModuleStructureValidator:
    """Validates module structure against Pydantic models.

    This validator performs non-fail-fast validation, collecting all Pydantic
    validation errors before raising a ModuleStructureError with complete
    error information.
    """

    def validate_structure(self, raw_data: dict[str, dict]) -> ContentModule:
        """Validate and construct a ContentModule from raw parsed data.

        Takes a dictionary of parsed YAML files and attempts to construct a
        ContentModule instance. All Pydantic validation errors are collected
        and included in the exception if validation fails.

        Args:
            raw_data: Dictionary mapping file identifiers to parsed YAML content.
                     Expected keys typically include 'metadata', 'characters',
                     'relationship_axes', 'trigger_definitions', 'scene_phases',
                     'phase_transitions', and 'ending_conditions'.

        Returns:
            A validated ContentModule instance.

        Raises:
            ModuleStructureError: If validation fails, containing all validation errors.
        """
        try:
            return ContentModule(**raw_data)
        except ValidationError as e:
            # Collect all validation errors with descriptive messages
            error_messages = []
            for error in e.errors():
                loc = ".".join(str(x) for x in error["loc"])
                msg = error["msg"]
                error_messages.append(f"{loc}: {msg}")

            # Extract module_id from metadata if available
            module_id = "unknown"
            if "metadata" in raw_data and isinstance(raw_data["metadata"], dict):
                module_id = raw_data["metadata"].get("module_id", "unknown")

            raise ModuleStructureError(
                message="Content module structure validation failed",
                module_id=module_id,
                errors=error_messages,
            )


def load_module(
    module_id: str,
    *,
    root_path: Path | None = None,
) -> ContentModule:
    """Load and validate a content module.

    Loads all YAML files from a module directory, validates the structure,
    and returns a fully constructed ContentModule instance.

    Args:
        module_id: The unique identifier of the module to load.
        root_path: Optional root path for module files. If not provided,
                  defaults to content/modules/{module_id}/

    Returns:
        A validated ContentModule instance.

    Raises:
        ModuleNotFoundError: If the module directory cannot be found.
        ModuleFileReadError: If module files cannot be read.
        ModuleParseError: If any YAML file fails to parse.
        ModuleStructureError: If the module structure is invalid.

    Example:
        >>> module = load_module("god_of_carnage")
        >>> print(module.metadata.title)
    """
    # Determine module root path
    if root_path is None:
        root_path = Path("content/modules") / module_id

    # Ensure it's a Path object
    if isinstance(root_path, str):
        root_path = Path(root_path)

    # Check if module directory exists before attempting to load
    if not root_path.exists():
        raise ModuleNotFoundError(
            message=f"Module not found",
            module_id=module_id,
            file_path=str(root_path),
        )

    # Load all YAML files from the module directory
    loader = ModuleFileLoader()
    try:
        raw_data = loader.load_all_module_files(root_path)
    except (ModuleFileReadError, ModuleParseError):
        # Re-raise with proper module_id context
        raise

    # Validate and construct the ContentModule
    validator = ModuleStructureValidator()
    module = validator.validate_structure(raw_data)

    return module
