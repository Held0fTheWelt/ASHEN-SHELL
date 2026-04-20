"""Published artifact loading for publish-bound session birth."""

from __future__ import annotations

import json
from pathlib import Path

from .config import get_settings
from .session_birth import PublishedArtifactBundle, validate_publish_bound_birth


class PublishedArtifactRegistry:
    """Loads the bundled published artifact used for authoritative session birth."""

    def __init__(self, bundle_path: Path | None = None):
        settings = get_settings()
        self.bundle_path = bundle_path or settings.published_bundle_path

    def load_bundle(self, module_id: str) -> PublishedArtifactBundle:
        """Return the published bundle for the requested module.

        Raises:
            FileNotFoundError: If the packaged bundle is missing.
            ValueError: If the bundle is incomplete or not published for the module.
        """

        data = json.loads(self.bundle_path.read_text(encoding="utf-8"))
        ok, missing = validate_publish_bound_birth(data)
        if not ok:
            raise ValueError(f"published artifact bundle incomplete: {', '.join(missing)}")
        if data["publish_state"] != "published":
            raise ValueError("artifact bundle is not published")
        if data["module_id"] != module_id:
            raise ValueError(f"module '{module_id}' is not present in bundled published artifacts")
        return PublishedArtifactBundle(**data)
