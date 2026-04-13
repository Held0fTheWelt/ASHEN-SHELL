"""Schema-level checks for narrative governance model foundation."""

from __future__ import annotations

from sqlalchemy import inspect

from app.extensions import db


def test_narrative_governance_tables_exist(app):
    expected_tables = {
        "narrative_packages",
        "narrative_package_history_events",
        "narrative_previews",
        "narrative_revision_candidates",
        "narrative_revision_conflicts",
        "narrative_revision_status_history",
        "narrative_evaluation_runs",
        "narrative_evaluation_coverage",
        "narrative_notification_rules",
        "narrative_notifications",
        "narrative_runtime_health_events",
        "narrative_runtime_health_rollups",
    }
    with app.app_context():
        inspector = inspect(db.engine)
        actual = set(inspector.get_table_names())
        assert expected_tables.issubset(actual)


def test_narrative_packages_table_has_expected_columns(app):
    with app.app_context():
        inspector = inspect(db.engine)
        cols = {item["name"] for item in inspector.get_columns("narrative_packages")}
        assert {"module_id", "active_package_version", "active_manifest_path", "active_package_path"}.issubset(cols)
