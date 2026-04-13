"""Active and preview package loader for world-engine narrative governance."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json

from app.narrative.package_models import NarrativePackage


@dataclass(slots=True)
class LoadedPackageState:
    """Current package load state."""

    module_id: str
    active_version: str | None = None
    loaded_previews: dict[str, str] | None = None

    def __post_init__(self) -> None:
        if self.loaded_previews is None:
            self.loaded_previews = {}


class NarrativePackageLoader:
    """Resolve compiled package artifacts for active and preview runtime paths."""

    def __init__(self, repo_root: Path) -> None:
        self._repo_root = repo_root
        self._state_by_module: dict[str, LoadedPackageState] = {}

    def _module_root(self, module_id: str) -> Path:
        return self._repo_root / "content" / "compiled_packages" / module_id

    def _load_package_file(self, path: Path) -> NarrativePackage:
        if not path.exists():
            raise FileNotFoundError(str(path))
        return NarrativePackage.model_validate(json.loads(path.read_text(encoding="utf-8")))

    def reload_active(self, *, module_id: str, expected_active_version: str) -> dict[str, str]:
        package_file = self._module_root(module_id) / "versions" / expected_active_version / "package.json"
        self._load_package_file(package_file)
        state = self._state_by_module.setdefault(module_id, LoadedPackageState(module_id=module_id))
        state.active_version = expected_active_version
        return {"reload_status": "accepted", "loaded_version": expected_active_version}

    def load_preview(self, *, module_id: str, preview_id: str) -> dict[str, str]:
        package_file = self._module_root(module_id) / "previews" / preview_id / "package.json"
        self._load_package_file(package_file)
        state = self._state_by_module.setdefault(module_id, LoadedPackageState(module_id=module_id))
        if preview_id in (state.loaded_previews or {}):
            raise ValueError("preview_already_loaded")
        state.loaded_previews[preview_id] = "loaded"
        return {"preview_id": preview_id, "load_status": "loaded"}

    def unload_preview(self, *, module_id: str, preview_id: str) -> dict[str, str]:
        state = self._state_by_module.setdefault(module_id, LoadedPackageState(module_id=module_id))
        if preview_id not in (state.loaded_previews or {}):
            raise KeyError("preview_not_loaded")
        state.loaded_previews.pop(preview_id, None)
        return {"preview_id": preview_id, "unload_status": "accepted"}

    def state(self, module_id: str) -> dict[str, object]:
        state = self._state_by_module.get(module_id)
        if state is None:
            return {"module_id": module_id, "active_version": None, "loaded_previews": []}
        return {
            "module_id": module_id,
            "active_version": state.active_version,
            "loaded_previews": sorted((state.loaded_previews or {}).keys()),
        }
