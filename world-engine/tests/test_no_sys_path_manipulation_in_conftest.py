"""Wave 6: no sys.path insert that reintroduces app package collision."""
from __future__ import annotations

from pathlib import Path


def test_no_sys_path_manipulation_inserts_world_engine_before_backend() -> None:
    root = Path(__file__).resolve().parents[2] / "conftest.py"
    text = root.read_text(encoding="utf-8")
    # World-engine must not be inserted at index 1 ahead of backend for ``app``.
    assert "sys.path.insert(1, _world_engine_str)" not in text
    assert "sys.path.append(_world_engine_str)" in text or "append(_world_engine_str)" in text
