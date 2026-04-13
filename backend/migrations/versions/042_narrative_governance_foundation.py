"""narrative governance foundation tables

Revision ID: 042
Revises: 041
Create Date: 2026-04-13
"""

from alembic import op
import sqlalchemy as sa


revision = "042"
down_revision = "041"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "narrative_packages",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("module_id", sa.String(length=128), nullable=False),
        sa.Column("active_package_version", sa.String(length=64), nullable=False),
        sa.Column("active_manifest_path", sa.String(length=512), nullable=False),
        sa.Column("active_package_path", sa.String(length=512), nullable=False),
        sa.Column("active_source_revision", sa.String(length=256), nullable=False),
        sa.Column("validation_status", sa.String(length=32), nullable=False, server_default="unknown"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("module_id"),
    )
    op.create_index("ix_narrative_packages_module_id", "narrative_packages", ["module_id"])
    op.create_index(
        "ix_narrative_packages_active_package_version",
        "narrative_packages",
        ["active_package_version"],
    )

    op.create_table(
        "narrative_package_history_events",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("module_id", sa.String(length=128), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("package_version", sa.String(length=64), nullable=True),
        sa.Column("from_version", sa.String(length=64), nullable=True),
        sa.Column("to_version", sa.String(length=64), nullable=True),
        sa.Column("preview_id", sa.String(length=64), nullable=True),
        sa.Column("actor_id", sa.String(length=128), nullable=True),
        sa.Column("reason", sa.Text(), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_narrative_package_history_events_module_id",
        "narrative_package_history_events",
        ["module_id"],
    )
    op.create_index(
        "ix_narrative_package_history_events_event_type",
        "narrative_package_history_events",
        ["event_type"],
    )
    op.create_index(
        "ix_narrative_package_history_events_preview_id",
        "narrative_package_history_events",
        ["preview_id"],
    )
    op.create_index(
        "ix_narrative_package_history_events_occurred_at",
        "narrative_package_history_events",
        ["occurred_at"],
    )
    op.create_index(
        "ix_narrative_package_history_events_module_occured",
        "narrative_package_history_events",
        ["module_id", "occurred_at"],
    )

    op.create_table(
        "narrative_previews",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("preview_id", sa.String(length=64), nullable=False),
        sa.Column("module_id", sa.String(length=128), nullable=False),
        sa.Column("package_version", sa.String(length=64), nullable=False),
        sa.Column("draft_workspace_id", sa.String(length=128), nullable=True),
        sa.Column("build_status", sa.String(length=32), nullable=False),
        sa.Column("validation_status", sa.String(length=32), nullable=False, server_default="unknown"),
        sa.Column("evaluation_status", sa.String(length=32), nullable=False, server_default="not_run"),
        sa.Column("promotion_readiness_json", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("artifact_root_path", sa.String(length=512), nullable=False),
        sa.Column("created_by", sa.String(length=128), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("preview_id"),
    )
    op.create_index("ix_narrative_previews_preview_id", "narrative_previews", ["preview_id"])
    op.create_index("ix_narrative_previews_module_id", "narrative_previews", ["module_id"])
    op.create_index("ix_narrative_previews_created_at", "narrative_previews", ["created_at"])
    op.create_index("ix_narrative_previews_build_status", "narrative_previews", ["build_status"])
    op.create_index(
        "ix_narrative_previews_evaluation_status",
        "narrative_previews",
        ["evaluation_status"],
    )
    op.create_index(
        "ix_narrative_previews_module_created_at",
        "narrative_previews",
        ["module_id", "created_at"],
    )

    op.create_table(
        "narrative_revision_candidates",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("revision_id", sa.String(length=64), nullable=False),
        sa.Column("module_id", sa.String(length=128), nullable=False),
        sa.Column("source_finding_id", sa.String(length=64), nullable=True),
        sa.Column("target_kind", sa.String(length=64), nullable=False),
        sa.Column("target_ref", sa.String(length=255), nullable=False),
        sa.Column("operation", sa.String(length=64), nullable=False),
        sa.Column("structured_delta_json", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("expected_effects_json", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("risk_flags_json", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("review_status", sa.String(length=32), nullable=False),
        sa.Column("requires_review", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("mutation_allowed", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("created_by", sa.String(length=128), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("revision_id"),
    )
    op.create_index(
        "ix_narrative_revision_candidates_revision_id",
        "narrative_revision_candidates",
        ["revision_id"],
    )
    op.create_index(
        "ix_narrative_revision_candidates_module_id",
        "narrative_revision_candidates",
        ["module_id"],
    )
    op.create_index(
        "ix_narrative_revision_candidates_source_finding_id",
        "narrative_revision_candidates",
        ["source_finding_id"],
    )
    op.create_index(
        "ix_narrative_revision_candidates_review_status",
        "narrative_revision_candidates",
        ["review_status"],
    )
    op.create_index(
        "ix_narrative_revision_candidates_module_target",
        "narrative_revision_candidates",
        ["module_id", "target_kind", "target_ref"],
    )

    op.create_table(
        "narrative_revision_conflicts",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("conflict_id", sa.String(length=64), nullable=False),
        sa.Column("module_id", sa.String(length=128), nullable=False),
        sa.Column("candidate_ids_json", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("conflict_type", sa.String(length=64), nullable=False),
        sa.Column("target_kind", sa.String(length=64), nullable=False),
        sa.Column("target_ref", sa.String(length=255), nullable=False),
        sa.Column("resolution_status", sa.String(length=32), nullable=False, server_default="pending"),
        sa.Column("resolution_strategy", sa.String(length=64), nullable=True),
        sa.Column("winner_revision_id", sa.String(length=64), nullable=True),
        sa.Column("resolved_by", sa.String(length=128), nullable=True),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("conflict_id"),
    )
    op.create_index(
        "ix_narrative_revision_conflicts_conflict_id",
        "narrative_revision_conflicts",
        ["conflict_id"],
    )
    op.create_index(
        "ix_narrative_revision_conflicts_module_id",
        "narrative_revision_conflicts",
        ["module_id"],
    )
    op.create_index(
        "ix_narrative_revision_conflicts_resolution_status",
        "narrative_revision_conflicts",
        ["resolution_status"],
    )
    op.create_index(
        "ix_narrative_revision_conflicts_module_target",
        "narrative_revision_conflicts",
        ["module_id", "target_kind", "target_ref"],
    )

    op.create_table(
        "narrative_revision_status_history",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("revision_id", sa.String(length=64), nullable=False),
        sa.Column("from_status", sa.String(length=32), nullable=True),
        sa.Column("to_status", sa.String(length=32), nullable=False),
        sa.Column("actor_id", sa.String(length=128), nullable=True),
        sa.Column("actor_role", sa.String(length=64), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_narrative_revision_status_history_revision_id",
        "narrative_revision_status_history",
        ["revision_id"],
    )
    op.create_index(
        "ix_narrative_revision_status_history_to_status",
        "narrative_revision_status_history",
        ["to_status"],
    )
    op.create_index(
        "ix_narrative_revision_status_history_occurred_at",
        "narrative_revision_status_history",
        ["occurred_at"],
    )
    op.create_index(
        "ix_narrative_revision_status_history_revision_occurred",
        "narrative_revision_status_history",
        ["revision_id", "occurred_at"],
    )

    op.create_table(
        "narrative_evaluation_runs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("run_id", sa.String(length=64), nullable=False),
        sa.Column("module_id", sa.String(length=128), nullable=False),
        sa.Column("preview_id", sa.String(length=64), nullable=True),
        sa.Column("package_version", sa.String(length=64), nullable=True),
        sa.Column("run_type", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("scores_json", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("promotion_readiness_json", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("run_id"),
    )
    op.create_index("ix_narrative_evaluation_runs_run_id", "narrative_evaluation_runs", ["run_id"])
    op.create_index("ix_narrative_evaluation_runs_module_id", "narrative_evaluation_runs", ["module_id"])
    op.create_index("ix_narrative_evaluation_runs_preview_id", "narrative_evaluation_runs", ["preview_id"])
    op.create_index("ix_narrative_evaluation_runs_status", "narrative_evaluation_runs", ["status"])
    op.create_index(
        "ix_narrative_evaluation_runs_module_created_at",
        "narrative_evaluation_runs",
        ["module_id", "created_at"],
    )
    op.create_index(
        "ix_narrative_evaluation_runs_preview_created_at",
        "narrative_evaluation_runs",
        ["preview_id", "created_at"],
    )

    op.create_table(
        "narrative_evaluation_coverage",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("run_id", sa.String(length=64), nullable=False),
        sa.Column("coverage_kind", sa.String(length=64), nullable=False),
        sa.Column("covered_count", sa.Integer(), nullable=False),
        sa.Column("total_count", sa.Integer(), nullable=False),
        sa.Column("coverage_percentage", sa.Float(), nullable=False),
        sa.Column("missing_refs_json", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_narrative_evaluation_coverage_run_kind",
        "narrative_evaluation_coverage",
        ["run_id", "coverage_kind"],
    )

    op.create_table(
        "narrative_notification_rules",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("rule_id", sa.String(length=64), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("condition_json", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("channels_json", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("recipients_json", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("rule_id"),
    )
    op.create_index("ix_narrative_notification_rules_rule_id", "narrative_notification_rules", ["rule_id"])
    op.create_index(
        "ix_narrative_notification_rules_event_enabled",
        "narrative_notification_rules",
        ["event_type", "enabled"],
    )

    op.create_table(
        "narrative_notifications",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("notification_id", sa.String(length=64), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("severity", sa.String(length=16), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("body", sa.Text(), nullable=True),
        sa.Column("payload_json", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("acknowledged", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        sa.Column("acknowledged_by", sa.String(length=128), nullable=True),
        sa.Column("acknowledged_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("notification_id"),
    )
    op.create_index("ix_narrative_notifications_notification_id", "narrative_notifications", ["notification_id"])
    op.create_index(
        "ix_narrative_notifications_ack_created_at",
        "narrative_notifications",
        ["acknowledged", "created_at"],
    )
    op.create_index(
        "ix_narrative_notifications_severity_created_at",
        "narrative_notifications",
        ["severity", "created_at"],
    )

    op.create_table(
        "narrative_runtime_health_events",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("event_id", sa.String(length=64), nullable=False),
        sa.Column("module_id", sa.String(length=128), nullable=False),
        sa.Column("scene_id", sa.String(length=128), nullable=True),
        sa.Column("turn_number", sa.Integer(), nullable=True),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("severity", sa.String(length=16), nullable=False),
        sa.Column("failure_types_json", sa.JSON(), nullable=True),
        sa.Column("payload_json", sa.JSON(), nullable=False, server_default="{}"),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("event_id"),
    )
    op.create_index("ix_narrative_runtime_health_events_event_id", "narrative_runtime_health_events", ["event_id"])
    op.create_index(
        "ix_narrative_runtime_health_events_module_id",
        "narrative_runtime_health_events",
        ["module_id"],
    )
    op.create_index(
        "ix_narrative_runtime_health_events_scene_id",
        "narrative_runtime_health_events",
        ["scene_id"],
    )
    op.create_index(
        "ix_narrative_runtime_health_events_event_type",
        "narrative_runtime_health_events",
        ["event_type"],
    )
    op.create_index(
        "ix_narrative_runtime_health_events_occurred_at",
        "narrative_runtime_health_events",
        ["occurred_at"],
    )
    op.create_index(
        "ix_narrative_runtime_health_events_module_scene_time",
        "narrative_runtime_health_events",
        ["module_id", "scene_id", "occurred_at"],
    )

    op.create_table(
        "narrative_runtime_health_rollups",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("module_id", sa.String(length=128), nullable=False),
        sa.Column("window_key", sa.String(length=64), nullable=False),
        sa.Column("window_start", sa.DateTime(timezone=True), nullable=False),
        sa.Column("window_end", sa.DateTime(timezone=True), nullable=False),
        sa.Column("total_turns", sa.Integer(), nullable=False),
        sa.Column("first_pass_success_rate", sa.Float(), nullable=False),
        sa.Column("corrective_retry_rate", sa.Float(), nullable=False),
        sa.Column("safe_fallback_rate", sa.Float(), nullable=False),
        sa.Column("top_failure_types_json", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_narrative_runtime_health_rollups_module_window_start",
        "narrative_runtime_health_rollups",
        ["module_id", "window_start"],
    )
    op.create_index(
        "ix_narrative_runtime_health_rollups_module_windowkey_window_start",
        "narrative_runtime_health_rollups",
        ["module_id", "window_key", "window_start"],
    )


def downgrade():
    op.drop_index(
        "ix_narrative_runtime_health_rollups_module_windowkey_window_start",
        table_name="narrative_runtime_health_rollups",
    )
    op.drop_index(
        "ix_narrative_runtime_health_rollups_module_window_start",
        table_name="narrative_runtime_health_rollups",
    )
    op.drop_table("narrative_runtime_health_rollups")

    op.drop_index(
        "ix_narrative_runtime_health_events_module_scene_time",
        table_name="narrative_runtime_health_events",
    )
    op.drop_index("ix_narrative_runtime_health_events_occurred_at", table_name="narrative_runtime_health_events")
    op.drop_index("ix_narrative_runtime_health_events_event_type", table_name="narrative_runtime_health_events")
    op.drop_index("ix_narrative_runtime_health_events_scene_id", table_name="narrative_runtime_health_events")
    op.drop_index("ix_narrative_runtime_health_events_module_id", table_name="narrative_runtime_health_events")
    op.drop_index("ix_narrative_runtime_health_events_event_id", table_name="narrative_runtime_health_events")
    op.drop_table("narrative_runtime_health_events")

    op.drop_index("ix_narrative_notifications_severity_created_at", table_name="narrative_notifications")
    op.drop_index("ix_narrative_notifications_ack_created_at", table_name="narrative_notifications")
    op.drop_index("ix_narrative_notifications_notification_id", table_name="narrative_notifications")
    op.drop_table("narrative_notifications")

    op.drop_index("ix_narrative_notification_rules_event_enabled", table_name="narrative_notification_rules")
    op.drop_index("ix_narrative_notification_rules_rule_id", table_name="narrative_notification_rules")
    op.drop_table("narrative_notification_rules")

    op.drop_index("ix_narrative_evaluation_coverage_run_kind", table_name="narrative_evaluation_coverage")
    op.drop_table("narrative_evaluation_coverage")

    op.drop_index("ix_narrative_evaluation_runs_preview_created_at", table_name="narrative_evaluation_runs")
    op.drop_index("ix_narrative_evaluation_runs_module_created_at", table_name="narrative_evaluation_runs")
    op.drop_index("ix_narrative_evaluation_runs_status", table_name="narrative_evaluation_runs")
    op.drop_index("ix_narrative_evaluation_runs_preview_id", table_name="narrative_evaluation_runs")
    op.drop_index("ix_narrative_evaluation_runs_module_id", table_name="narrative_evaluation_runs")
    op.drop_index("ix_narrative_evaluation_runs_run_id", table_name="narrative_evaluation_runs")
    op.drop_table("narrative_evaluation_runs")

    op.drop_index(
        "ix_narrative_revision_status_history_revision_occurred",
        table_name="narrative_revision_status_history",
    )
    op.drop_index("ix_narrative_revision_status_history_occurred_at", table_name="narrative_revision_status_history")
    op.drop_index("ix_narrative_revision_status_history_to_status", table_name="narrative_revision_status_history")
    op.drop_index("ix_narrative_revision_status_history_revision_id", table_name="narrative_revision_status_history")
    op.drop_table("narrative_revision_status_history")

    op.drop_index(
        "ix_narrative_revision_conflicts_module_target",
        table_name="narrative_revision_conflicts",
    )
    op.drop_index(
        "ix_narrative_revision_conflicts_resolution_status",
        table_name="narrative_revision_conflicts",
    )
    op.drop_index("ix_narrative_revision_conflicts_module_id", table_name="narrative_revision_conflicts")
    op.drop_index("ix_narrative_revision_conflicts_conflict_id", table_name="narrative_revision_conflicts")
    op.drop_table("narrative_revision_conflicts")

    op.drop_index(
        "ix_narrative_revision_candidates_module_target",
        table_name="narrative_revision_candidates",
    )
    op.drop_index(
        "ix_narrative_revision_candidates_review_status",
        table_name="narrative_revision_candidates",
    )
    op.drop_index(
        "ix_narrative_revision_candidates_source_finding_id",
        table_name="narrative_revision_candidates",
    )
    op.drop_index("ix_narrative_revision_candidates_module_id", table_name="narrative_revision_candidates")
    op.drop_index("ix_narrative_revision_candidates_revision_id", table_name="narrative_revision_candidates")
    op.drop_table("narrative_revision_candidates")

    op.drop_index("ix_narrative_previews_module_created_at", table_name="narrative_previews")
    op.drop_index("ix_narrative_previews_evaluation_status", table_name="narrative_previews")
    op.drop_index("ix_narrative_previews_build_status", table_name="narrative_previews")
    op.drop_index("ix_narrative_previews_created_at", table_name="narrative_previews")
    op.drop_index("ix_narrative_previews_module_id", table_name="narrative_previews")
    op.drop_index("ix_narrative_previews_preview_id", table_name="narrative_previews")
    op.drop_table("narrative_previews")

    op.drop_index(
        "ix_narrative_package_history_events_module_occured",
        table_name="narrative_package_history_events",
    )
    op.drop_index(
        "ix_narrative_package_history_events_occurred_at",
        table_name="narrative_package_history_events",
    )
    op.drop_index(
        "ix_narrative_package_history_events_preview_id",
        table_name="narrative_package_history_events",
    )
    op.drop_index(
        "ix_narrative_package_history_events_event_type",
        table_name="narrative_package_history_events",
    )
    op.drop_index(
        "ix_narrative_package_history_events_module_id",
        table_name="narrative_package_history_events",
    )
    op.drop_table("narrative_package_history_events")

    op.drop_index("ix_narrative_packages_active_package_version", table_name="narrative_packages")
    op.drop_index("ix_narrative_packages_module_id", table_name="narrative_packages")
    op.drop_table("narrative_packages")
