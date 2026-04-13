"""operational settings and ai runtime governance foundation

Revision ID: 043
Revises: 042
Create Date: 2026-04-13
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op


revision = "043"
down_revision = "042"
branch_labels = None
depends_on = None


def _insert_default_presets() -> None:
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc)
    table = sa.table(
        "bootstrap_presets",
        sa.column("preset_id", sa.String),
        sa.column("display_name", sa.String),
        sa.column("description", sa.Text),
        sa.column("generation_execution_mode", sa.String),
        sa.column("retrieval_execution_mode", sa.String),
        sa.column("validation_execution_mode", sa.String),
        sa.column("provider_selection_mode", sa.String),
        sa.column("default_runtime_profile", sa.String),
        sa.column("default_provider_templates_json", sa.JSON),
        sa.column("default_budget_policy_json", sa.JSON),
        sa.column("is_builtin", sa.Boolean),
        sa.column("created_at", sa.DateTime(timezone=True)),
        sa.column("updated_at", sa.DateTime(timezone=True)),
    )
    rows = [
            {
                "preset_id": "safe_local",
                "display_name": "Local Mock Safe",
                "description": "Deterministic local mock setup with conservative defaults.",
                "generation_execution_mode": "mock_only",
                "retrieval_execution_mode": "disabled",
                "validation_execution_mode": "schema_only",
                "provider_selection_mode": "local_only",
                "default_runtime_profile": "safe_local",
                "default_provider_templates_json": [
                    {"provider_type": "mock", "display_name": "Mock Provider", "enabled_by_default": True, "requires_secret": False}
                ],
                "default_budget_policy_json": {"daily_limit": "0", "monthly_limit": "0", "warning_threshold_percent": 80, "hard_stop_enabled": False},
                "is_builtin": True,
            },
            {
                "preset_id": "balanced",
                "display_name": "Local Hybrid",
                "description": "Hybrid routed setup with mock fallback and optional cloud provider.",
                "generation_execution_mode": "hybrid_routed_with_mock_fallback",
                "retrieval_execution_mode": "hybrid_dense_sparse",
                "validation_execution_mode": "schema_plus_semantic",
                "provider_selection_mode": "restricted_by_route",
                "default_runtime_profile": "balanced",
                "default_provider_templates_json": [
                    {"provider_type": "mock", "display_name": "Mock Provider", "enabled_by_default": True, "requires_secret": False},
                    {"provider_type": "ollama", "display_name": "Local Ollama", "enabled_by_default": True, "base_url": "http://ollama:11434", "requires_secret": False},
                ],
                "default_budget_policy_json": {"daily_limit": "50.00", "monthly_limit": "1000.00", "warning_threshold_percent": 80, "hard_stop_enabled": False},
                "is_builtin": True,
            },
            {
                "preset_id": "quality_first",
                "display_name": "Cloud Narrative",
                "description": "Cloud-first quality path with routed LLM/SLM and full costs tracking.",
                "generation_execution_mode": "routed_llm_slm",
                "retrieval_execution_mode": "hybrid_dense_sparse",
                "validation_execution_mode": "schema_plus_semantic",
                "provider_selection_mode": "remote_preferred",
                "default_runtime_profile": "quality_first",
                "default_provider_templates_json": [
                    {"provider_type": "openai", "display_name": "OpenAI Primary", "enabled_by_default": True, "base_url": "https://api.openai.com/v1", "requires_secret": True},
                ],
                "default_budget_policy_json": {"daily_limit": "100.00", "monthly_limit": "2500.00", "warning_threshold_percent": 80, "hard_stop_enabled": False},
                "is_builtin": True,
            },
            {
                "preset_id": "cost_aware",
                "display_name": "Research / Evaluation",
                "description": "Hybrid or AI-focused profile for research and evaluation workflows.",
                "generation_execution_mode": "hybrid_routed_with_mock_fallback",
                "retrieval_execution_mode": "hybrid_dense_sparse",
                "validation_execution_mode": "schema_plus_semantic",
                "provider_selection_mode": "remote_allowed",
                "default_runtime_profile": "cost_aware",
                "default_provider_templates_json": [
                    {"provider_type": "mock", "display_name": "Mock Provider", "enabled_by_default": True, "requires_secret": False},
                    {"provider_type": "openai", "display_name": "OpenAI Research", "enabled_by_default": False, "base_url": "https://api.openai.com/v1", "requires_secret": True},
                ],
                "default_budget_policy_json": {"daily_limit": "25.00", "monthly_limit": "500.00", "warning_threshold_percent": 75, "hard_stop_enabled": False},
                "is_builtin": True,
            },
    ]
    for row in rows:
        row["created_at"] = now
        row["updated_at"] = now
    op.bulk_insert(table, rows)


def _seed_bootstrap_presets_if_empty() -> None:
    """If bootstrap_presets exists (e.g. from db.create_all) but has no rows, insert defaults."""
    count = op.get_bind().execute(sa.text("SELECT COUNT(*) FROM bootstrap_presets")).scalar()
    if not count:
        _insert_default_presets()


def upgrade() -> None:
    # Idempotent: volumes may already have these tables from db.create_all() or a partial
    # upgrade while alembic_version still points at 042 (same pattern as migration 039).
    from sqlalchemy import inspect

    bind = op.get_bind()
    existing = set(inspect(bind).get_table_names())

    if "bootstrap_configs" not in existing:
        op.create_table(
            "bootstrap_configs",
            sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
            sa.Column("bootstrap_state", sa.String(length=64), nullable=False),
            sa.Column("bootstrap_locked", sa.Boolean(), nullable=False, server_default=sa.text("0")),
            sa.Column("selected_preset", sa.String(length=64), nullable=True),
            sa.Column("secret_storage_mode", sa.String(length=64), nullable=False),
            sa.Column("runtime_profile", sa.String(length=64), nullable=False),
            sa.Column("generation_execution_mode", sa.String(length=64), nullable=False),
            sa.Column("retrieval_execution_mode", sa.String(length=64), nullable=False),
            sa.Column("validation_execution_mode", sa.String(length=64), nullable=False),
            sa.Column("provider_selection_mode", sa.String(length=64), nullable=False),
            sa.Column("trust_anchor_fingerprint", sa.String(length=256), nullable=True),
            sa.Column("trust_anchor_metadata_json", sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
            sa.Column("reopen_requires_elevated_auth", sa.Boolean(), nullable=False, server_default=sa.text("1")),
            sa.Column("bootstrap_completed_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("bootstrap_completed_by", sa.String(length=128), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        )
        op.create_index("ix_bootstrap_configs_bootstrap_state", "bootstrap_configs", ["bootstrap_state"])

    if "bootstrap_presets" not in existing:
        op.create_table(
            "bootstrap_presets",
            sa.Column("preset_id", sa.String(length=64), primary_key=True),
            sa.Column("display_name", sa.String(length=128), nullable=False),
            sa.Column("description", sa.Text(), nullable=False),
            sa.Column("generation_execution_mode", sa.String(length=64), nullable=False),
            sa.Column("retrieval_execution_mode", sa.String(length=64), nullable=False),
            sa.Column("validation_execution_mode", sa.String(length=64), nullable=False),
            sa.Column("provider_selection_mode", sa.String(length=64), nullable=False),
            sa.Column("default_runtime_profile", sa.String(length=64), nullable=False),
            sa.Column("default_provider_templates_json", sa.JSON(), nullable=False, server_default=sa.text("'[]'")),
            sa.Column("default_budget_policy_json", sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
            sa.Column("is_builtin", sa.Boolean(), nullable=False, server_default=sa.text("1")),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        )
        _insert_default_presets()
    else:
        _seed_bootstrap_presets_if_empty()

    if "ai_provider_configs" not in existing:
        op.create_table(
            "ai_provider_configs",
            sa.Column("provider_id", sa.String(length=128), primary_key=True),
            sa.Column("provider_type", sa.String(length=64), nullable=False),
            sa.Column("display_name", sa.String(length=128), nullable=False),
            sa.Column("base_url", sa.String(length=512), nullable=True),
            sa.Column("is_enabled", sa.Boolean(), nullable=False, server_default=sa.text("1")),
            sa.Column("is_local", sa.Boolean(), nullable=False, server_default=sa.text("0")),
            sa.Column("supports_structured_output", sa.Boolean(), nullable=False, server_default=sa.text("0")),
            sa.Column("health_status", sa.String(length=32), nullable=False, server_default="unknown"),
            sa.Column("credential_configured", sa.Boolean(), nullable=False, server_default=sa.text("0")),
            sa.Column("credential_fingerprint", sa.String(length=256), nullable=True),
            sa.Column("last_tested_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("allow_live_runtime", sa.Boolean(), nullable=False, server_default=sa.text("1")),
            sa.Column("allow_preview_runtime", sa.Boolean(), nullable=False, server_default=sa.text("1")),
            sa.Column("allow_writers_room", sa.Boolean(), nullable=False, server_default=sa.text("1")),
            sa.Column("allow_research_suite", sa.Boolean(), nullable=False, server_default=sa.text("1")),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        )
        op.create_index("ix_ai_provider_configs_provider_type", "ai_provider_configs", ["provider_type"])
        op.create_index("ix_ai_provider_configs_is_enabled", "ai_provider_configs", ["is_enabled"])

    if "ai_provider_credentials" not in existing:
        op.create_table(
            "ai_provider_credentials",
            sa.Column("credential_id", sa.String(length=128), primary_key=True),
            sa.Column("provider_id", sa.String(length=128), sa.ForeignKey("ai_provider_configs.provider_id"), nullable=False),
            sa.Column("secret_name", sa.String(length=128), nullable=False),
            sa.Column("encrypted_secret", sa.LargeBinary(), nullable=False),
            sa.Column("encrypted_dek", sa.LargeBinary(), nullable=False),
            sa.Column("secret_nonce", sa.LargeBinary(), nullable=False),
            sa.Column("dek_nonce", sa.LargeBinary(), nullable=False),
            sa.Column("dek_algorithm", sa.String(length=64), nullable=False, server_default="AES-256-GCM"),
            sa.Column("kek_key_id", sa.String(length=128), nullable=True),
            sa.Column("secret_fingerprint", sa.String(length=256), nullable=False),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("rotated_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
            sa.Column("rotation_in_progress", sa.Boolean(), nullable=False, server_default=sa.text("0")),
        )
        op.create_index("ix_ai_provider_credentials_provider_id", "ai_provider_credentials", ["provider_id"])
        op.create_index(
            "ix_ai_provider_credentials_secret_fingerprint",
            "ai_provider_credentials",
            ["secret_fingerprint"],
        )

    if "ai_model_configs" not in existing:
        op.create_table(
            "ai_model_configs",
            sa.Column("model_id", sa.String(length=128), primary_key=True),
            sa.Column("provider_id", sa.String(length=128), sa.ForeignKey("ai_provider_configs.provider_id"), nullable=False),
            sa.Column("model_name", sa.String(length=256), nullable=False),
            sa.Column("display_name", sa.String(length=256), nullable=False),
            sa.Column("model_role", sa.String(length=32), nullable=False),
            sa.Column("is_enabled", sa.Boolean(), nullable=False, server_default=sa.text("1")),
            sa.Column("structured_output_capable", sa.Boolean(), nullable=False, server_default=sa.text("0")),
            sa.Column("timeout_seconds", sa.Integer(), nullable=False, server_default="30"),
            sa.Column("max_context_tokens", sa.Integer(), nullable=True),
            sa.Column("cost_method", sa.String(length=64), nullable=False, server_default="none"),
            sa.Column("input_price_per_1k", sa.Numeric(18, 6), nullable=True),
            sa.Column("output_price_per_1k", sa.Numeric(18, 6), nullable=True),
            sa.Column("flat_request_price", sa.Numeric(18, 6), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        )
        op.create_index("ix_ai_model_configs_provider_id", "ai_model_configs", ["provider_id"])
        op.create_index("ix_ai_model_configs_is_enabled", "ai_model_configs", ["is_enabled"])
        op.create_index("ix_ai_model_configs_model_role", "ai_model_configs", ["model_role"])

    if "ai_task_routes" not in existing:
        op.create_table(
            "ai_task_routes",
            sa.Column("route_id", sa.String(length=128), primary_key=True),
            sa.Column("task_kind", sa.String(length=128), nullable=False),
            sa.Column("workflow_scope", sa.String(length=128), nullable=False),
            sa.Column("preferred_model_id", sa.String(length=128), sa.ForeignKey("ai_model_configs.model_id"), nullable=True),
            sa.Column("fallback_model_id", sa.String(length=128), sa.ForeignKey("ai_model_configs.model_id"), nullable=True),
            sa.Column("mock_model_id", sa.String(length=128), sa.ForeignKey("ai_model_configs.model_id"), nullable=True),
            sa.Column("is_enabled", sa.Boolean(), nullable=False, server_default=sa.text("1")),
            sa.Column("use_mock_when_provider_unavailable", sa.Boolean(), nullable=False, server_default=sa.text("1")),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        )
        op.create_index("ix_ai_task_routes_task_kind", "ai_task_routes", ["task_kind"])
        op.create_index("ix_ai_task_routes_workflow_scope", "ai_task_routes", ["workflow_scope"])
        op.create_index("ix_ai_task_routes_is_enabled", "ai_task_routes", ["is_enabled"])
        op.create_index("ix_ai_task_routes_task_scope_enabled", "ai_task_routes", ["task_kind", "workflow_scope", "is_enabled"])

    if "system_setting_records" not in existing:
        op.create_table(
            "system_setting_records",
            sa.Column("setting_id", sa.String(length=128), primary_key=True),
            sa.Column("scope", sa.String(length=64), nullable=False),
            sa.Column("setting_key", sa.String(length=128), nullable=False),
            sa.Column("setting_value_json", sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
            sa.Column("is_secret_backed", sa.Boolean(), nullable=False, server_default=sa.text("0")),
            sa.Column("is_user_visible", sa.Boolean(), nullable=False, server_default=sa.text("1")),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("updated_by", sa.String(length=128), nullable=True),
        )
        op.create_index("ix_system_setting_records_scope", "system_setting_records", ["scope"])
        op.create_index("ix_system_setting_records_setting_key", "system_setting_records", ["setting_key"])

    if "resolved_runtime_config_snapshots" not in existing:
        op.create_table(
            "resolved_runtime_config_snapshots",
            sa.Column("snapshot_id", sa.String(length=128), primary_key=True),
            sa.Column("config_version", sa.String(length=128), nullable=False, unique=True),
            sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("generation_execution_mode", sa.String(length=64), nullable=False),
            sa.Column("retrieval_execution_mode", sa.String(length=64), nullable=False),
            sa.Column("validation_execution_mode", sa.String(length=64), nullable=False),
            sa.Column("runtime_profile", sa.String(length=64), nullable=False),
            sa.Column("provider_selection_mode", sa.String(length=64), nullable=False),
            sa.Column("resolved_config_json", sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("1")),
        )
        op.create_index("ix_resolved_runtime_config_snapshots_generated_at", "resolved_runtime_config_snapshots", ["generated_at"])
        op.create_index("ix_resolved_runtime_config_snapshots_is_active", "resolved_runtime_config_snapshots", ["is_active"])

    if "provider_health_checks" not in existing:
        op.create_table(
            "provider_health_checks",
            sa.Column("health_check_id", sa.String(length=128), primary_key=True),
            sa.Column("provider_id", sa.String(length=128), sa.ForeignKey("ai_provider_configs.provider_id"), nullable=False),
            sa.Column("health_status", sa.String(length=32), nullable=False),
            sa.Column("latency_ms", sa.Integer(), nullable=True),
            sa.Column("error_code", sa.String(length=128), nullable=True),
            sa.Column("error_message", sa.String(length=512), nullable=True),
            sa.Column("tested_at", sa.DateTime(timezone=True), nullable=False),
        )
        op.create_index("ix_provider_health_checks_provider_id", "provider_health_checks", ["provider_id"])
        op.create_index("ix_provider_health_checks_health_status", "provider_health_checks", ["health_status"])
        op.create_index("ix_provider_health_checks_tested_at", "provider_health_checks", ["tested_at"])

    if "ai_usage_events" not in existing:
        op.create_table(
            "ai_usage_events",
            sa.Column("usage_event_id", sa.String(length=128), primary_key=True),
            sa.Column("provider_id", sa.String(length=128), sa.ForeignKey("ai_provider_configs.provider_id"), nullable=True),
            sa.Column("model_id", sa.String(length=128), sa.ForeignKey("ai_model_configs.model_id"), nullable=True),
            sa.Column("task_kind", sa.String(length=128), nullable=False),
            sa.Column("workflow_scope", sa.String(length=128), nullable=False),
            sa.Column("request_id", sa.String(length=128), nullable=False),
            sa.Column("success", sa.Boolean(), nullable=False, server_default=sa.text("1")),
            sa.Column("latency_ms", sa.Integer(), nullable=True),
            sa.Column("input_tokens", sa.Integer(), nullable=True),
            sa.Column("output_tokens", sa.Integer(), nullable=True),
            sa.Column("provider_reported_cost", sa.Numeric(18, 6), nullable=True),
            sa.Column("estimated_cost", sa.Numeric(18, 6), nullable=True),
            sa.Column("cost_method_used", sa.String(length=64), nullable=False, server_default="none"),
            sa.Column("degraded_mode_used", sa.Boolean(), nullable=False, server_default=sa.text("0")),
            sa.Column("retry_used", sa.Boolean(), nullable=False, server_default=sa.text("0")),
            sa.Column("fallback_used", sa.Boolean(), nullable=False, server_default=sa.text("0")),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        )
        op.create_index("ix_ai_usage_events_created_at", "ai_usage_events", ["created_at"])
        op.create_index("ix_ai_usage_events_provider_id", "ai_usage_events", ["provider_id"])
        op.create_index("ix_ai_usage_events_model_id", "ai_usage_events", ["model_id"])
        op.create_index("ix_ai_usage_events_workflow_scope", "ai_usage_events", ["workflow_scope"])

    if "cost_budget_policies" not in existing:
        op.create_table(
            "cost_budget_policies",
            sa.Column("budget_policy_id", sa.String(length=128), primary_key=True),
            sa.Column("scope_kind", sa.String(length=64), nullable=False),
            sa.Column("scope_ref", sa.String(length=128), nullable=True),
            sa.Column("daily_limit", sa.Numeric(18, 6), nullable=True),
            sa.Column("monthly_limit", sa.Numeric(18, 6), nullable=True),
            sa.Column("warning_threshold_percent", sa.Integer(), nullable=False, server_default="80"),
            sa.Column("hard_stop_enabled", sa.Boolean(), nullable=False, server_default=sa.text("0")),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        )
        op.create_index("ix_cost_budget_policies_scope_kind", "cost_budget_policies", ["scope_kind"])
        op.create_index("ix_cost_budget_policies_scope_ref", "cost_budget_policies", ["scope_ref"])

    if "cost_rollups" not in existing:
        op.create_table(
            "cost_rollups",
            sa.Column("rollup_id", sa.String(length=128), primary_key=True),
            sa.Column("rollup_date", sa.Date(), nullable=False),
            sa.Column("provider_id", sa.String(length=128), sa.ForeignKey("ai_provider_configs.provider_id"), nullable=True),
            sa.Column("model_id", sa.String(length=128), sa.ForeignKey("ai_model_configs.model_id"), nullable=True),
            sa.Column("workflow_scope", sa.String(length=128), nullable=True),
            sa.Column("request_count", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("estimated_cost_total", sa.Numeric(18, 6), nullable=False, server_default="0"),
            sa.Column("provider_reported_cost_total", sa.Numeric(18, 6), nullable=True),
            sa.Column("retry_count", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("fallback_count", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        )
        op.create_index("ix_cost_rollups_rollup_date", "cost_rollups", ["rollup_date"])
        op.create_index("ix_cost_rollups_provider_id", "cost_rollups", ["provider_id"])
        op.create_index("ix_cost_rollups_model_id", "cost_rollups", ["model_id"])
        op.create_index("ix_cost_rollups_workflow_scope", "cost_rollups", ["workflow_scope"])

    if "setting_audit_events" not in existing:
        op.create_table(
            "setting_audit_events",
            sa.Column("audit_event_id", sa.String(length=128), primary_key=True),
            sa.Column("event_type", sa.String(length=128), nullable=False),
            sa.Column("scope", sa.String(length=64), nullable=False),
            sa.Column("target_ref", sa.String(length=256), nullable=False),
            sa.Column("changed_by", sa.String(length=128), nullable=False),
            sa.Column("changed_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("summary", sa.String(length=512), nullable=False),
            sa.Column("metadata_json", sa.JSON(), nullable=False, server_default=sa.text("'{}'")),
        )
        op.create_index("ix_setting_audit_events_changed_at", "setting_audit_events", ["changed_at"])
        op.create_index("ix_setting_audit_events_scope", "setting_audit_events", ["scope"])
        op.create_index("ix_setting_audit_events_target_ref", "setting_audit_events", ["target_ref"])


def downgrade() -> None:
    op.drop_index("ix_setting_audit_events_target_ref", table_name="setting_audit_events")
    op.drop_index("ix_setting_audit_events_scope", table_name="setting_audit_events")
    op.drop_index("ix_setting_audit_events_changed_at", table_name="setting_audit_events")
    op.drop_table("setting_audit_events")

    op.drop_index("ix_cost_rollups_workflow_scope", table_name="cost_rollups")
    op.drop_index("ix_cost_rollups_model_id", table_name="cost_rollups")
    op.drop_index("ix_cost_rollups_provider_id", table_name="cost_rollups")
    op.drop_index("ix_cost_rollups_rollup_date", table_name="cost_rollups")
    op.drop_table("cost_rollups")

    op.drop_index("ix_cost_budget_policies_scope_ref", table_name="cost_budget_policies")
    op.drop_index("ix_cost_budget_policies_scope_kind", table_name="cost_budget_policies")
    op.drop_table("cost_budget_policies")

    op.drop_index("ix_ai_usage_events_workflow_scope", table_name="ai_usage_events")
    op.drop_index("ix_ai_usage_events_model_id", table_name="ai_usage_events")
    op.drop_index("ix_ai_usage_events_provider_id", table_name="ai_usage_events")
    op.drop_index("ix_ai_usage_events_created_at", table_name="ai_usage_events")
    op.drop_table("ai_usage_events")

    op.drop_index("ix_provider_health_checks_tested_at", table_name="provider_health_checks")
    op.drop_index("ix_provider_health_checks_health_status", table_name="provider_health_checks")
    op.drop_index("ix_provider_health_checks_provider_id", table_name="provider_health_checks")
    op.drop_table("provider_health_checks")

    op.drop_index("ix_resolved_runtime_config_snapshots_is_active", table_name="resolved_runtime_config_snapshots")
    op.drop_index("ix_resolved_runtime_config_snapshots_generated_at", table_name="resolved_runtime_config_snapshots")
    op.drop_table("resolved_runtime_config_snapshots")

    op.drop_index("ix_system_setting_records_setting_key", table_name="system_setting_records")
    op.drop_index("ix_system_setting_records_scope", table_name="system_setting_records")
    op.drop_table("system_setting_records")

    op.drop_index("ix_ai_task_routes_task_scope_enabled", table_name="ai_task_routes")
    op.drop_index("ix_ai_task_routes_is_enabled", table_name="ai_task_routes")
    op.drop_index("ix_ai_task_routes_workflow_scope", table_name="ai_task_routes")
    op.drop_index("ix_ai_task_routes_task_kind", table_name="ai_task_routes")
    op.drop_table("ai_task_routes")

    op.drop_index("ix_ai_model_configs_model_role", table_name="ai_model_configs")
    op.drop_index("ix_ai_model_configs_is_enabled", table_name="ai_model_configs")
    op.drop_index("ix_ai_model_configs_provider_id", table_name="ai_model_configs")
    op.drop_table("ai_model_configs")

    op.drop_index("ix_ai_provider_credentials_secret_fingerprint", table_name="ai_provider_credentials")
    op.drop_index("ix_ai_provider_credentials_provider_id", table_name="ai_provider_credentials")
    op.drop_table("ai_provider_credentials")

    op.drop_index("ix_ai_provider_configs_is_enabled", table_name="ai_provider_configs")
    op.drop_index("ix_ai_provider_configs_provider_type", table_name="ai_provider_configs")
    op.drop_table("ai_provider_configs")

    op.drop_table("bootstrap_presets")
    op.drop_index("ix_bootstrap_configs_bootstrap_state", table_name="bootstrap_configs")
    op.drop_table("bootstrap_configs")
