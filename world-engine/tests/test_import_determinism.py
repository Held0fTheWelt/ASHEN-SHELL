"""Wave 6: import determinism — world_engine is not shadowed by backend app."""
from __future__ import annotations

import importlib
from pathlib import Path


def test_world_engine_import_is_deterministic() -> None:
    mod = importlib.import_module("world_engine")
    path = Path(mod.__file__).resolve()
    assert path.name == "__init__.py"
    assert path.parent.name == "world_engine"
    assert "world-engine" in path.parts or "WorldOfShadows" in str(path)
    # Must not resolve to backend/app
    assert "backend" not in path.parts or path.parts[path.parts.index("world_engine") - 1] == "world-engine"


def test_world_engine_main_importable() -> None:
    mod = importlib.import_module("world_engine.main")
    assert hasattr(mod, "app")


def test_backend_app_still_resolves_separately() -> None:
    import sys
    from pathlib import Path as P

    repo = P(__file__).resolve().parents[2]
    backend = str(repo / "backend")
    if backend not in sys.path:
        sys.path.insert(0, backend)
    # Clear cached wrong bindings if any.
    sys.modules.pop("app", None)
    backend_mod = importlib.import_module("app")
    we = importlib.import_module("world_engine")
    assert P(backend_mod.__file__).resolve() != P(we.__file__).resolve()
    assert "backend" in P(backend_mod.__file__).resolve().parts
