"""Wave 6 / G2: dormant ``runtime_sessions`` table must stay absent after drop."""

from __future__ import annotations

import sqlite3
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
LOCAL_DB = REPO_ROOT / "backend" / "instance" / "wos.db"


def test_runtime_sessions_table_absent() -> None:
    """Exit criterion for G2: local durable DB must not retain runtime_sessions."""
    assert LOCAL_DB.is_file(), f"expected local SQLite at {LOCAL_DB}"
    conn = sqlite3.connect(str(LOCAL_DB))
    try:
        row = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='runtime_sessions'"
        ).fetchone()
    finally:
        conn.close()
    assert row is None, "runtime_sessions must be dropped (Wave 6 / G2)"
