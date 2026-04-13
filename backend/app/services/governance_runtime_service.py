"""Operational settings and runtime governance services."""

from __future__ import annotations

from collections import defaultdict
from datetime import date, datetime, timezone
from decimal import Decimal
from uuid import uuid4

from flask import current_app
from sqlalchemy import and_
from sqlalchemy import inspect
from sqlalchemy.exc import OperationalError

from app.extensions import db
from app.governance.errors import GovernanceError, governance_error
from app.models import (
    AITaskRoute,
    AIModelConfig,
    AIProviderConfig,
    AIProviderCredential,
    AIUsageEvent,
    BootstrapConfig,
    BootstrapPreset,
    CostBudgetPolicy,
    CostRollup,
    ProviderHealthCheck,
    ResolvedRuntimeConfigSnapshot,
    SettingAuditEvent,
    SystemSettingRecord,
)
from app.services.activity_log_service import log_activity
from app.services.governance_secret_crypto_service import encrypt_secret


_REQUIRED_TASK_KINDS: tuple[str, ...] = (
    "narrative_live_generation",
    "narrative_preview_generation",
    "narrative_validation_semantic",
    "research_synthesis",
    "research_revision_drafting",
    "writers_room_revision_assist",
    "retrieval_embedding_generation",
    "retrieval_query_expansion",
)

_DEFAULT_PRESETS: tuple[dict, ...] = (
    {
        "preset_id": "safe_local",
        "display_name": "Local Mock Safe",
        "description": "Deterministic local mock setup with conservative defaults.",
        "generation_execution_mode": "mock_only",
        "retrieval_execution_mode": "disabled",
        "validation_execution_mode": "schema_only",
        "provider_selection_mode": "local_only",
        "default_runtime_profile": "safe_local",
        "default_provider_templates_json": [{"provider_type": "mock", "display_name": "Mock Provider", "enabled_by_default": True, "requires_secret": False}],
        "default_budget_policy_json": {"daily_limit": "0", "monthly_limit": "0", "warning_threshold_percent": 80, "hard_stop_enabled": False},
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
        "default_provider_templates_json": [{"provider_type": "openai", "display_name": "OpenAI Primary", "enabled_by_default": True, "base_url": "https://api.openai.com/v1", "requires_secret": True}],
        "default_budget_policy_json": {"daily_limit": "100.00", "monthly_limit": "2500.00", "warning_threshold_percent": 80, "hard_stop_enabled": False},
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
        "default_provider_templates_json": [{"provider_type": "mock", "display_name": "Mock Provider", "enabled_by_default": True, "requires_secret": False}],
        "default_budget_policy_json": {"daily_limit": "25.00", "monthly_limit": "500.00", "warning_threshold_percent": 75, "hard_stop_enabled": False},
    },
)


def _audit(event_type: str, scope: str, target_ref: str, changed_by: str, summary: str, metadata: dict | None = None) -> None:
    db.session.add(
        SettingAuditEvent(
            audit_event_id=f"audit_{uuid4().hex}",
            event_type=event_type,
            scope=scope,
            target_ref=target_ref,
            changed_by=changed_by,
            summary=summary,
            metadata_json=metadata or {},
        )
    )


def _seed_default_presets() -> None:
    for preset_payload in _DEFAULT_PRESETS:
        if BootstrapPreset.query.get(preset_payload["preset_id"]) is not None:
            continue
        db.session.add(BootstrapPreset(**preset_payload, is_builtin=True))


def _slug(value: str) -> str:
    return value.strip().lower().replace(" ", "_")


def get_bootstrap_status() -> dict:
    """Return current bootstrap state and available presets."""
    _seed_default_presets()
    db.session.flush()
    bootstrap = BootstrapConfig.query.order_by(BootstrapConfig.created_at.desc()).first()
    presets = BootstrapPreset.query.order_by(BootstrapPreset.display_name.asc()).all()
    if bootstrap is None:
        return {
            "bootstrap_required": True,
            "bootstrap_locked": False,
            "available_presets": [p.preset_id for p in presets],
            "configured": {
                "trust_anchor": False,
                "initial_admin": False,
                "secret_storage": False,
                "initial_provider": False,
            },
        }
    return {
        "bootstrap_required": bootstrap.bootstrap_state in {"uninitialized", "initializing", "bootstrap_recovery_required"},
        "bootstrap_locked": bool(bootstrap.bootstrap_locked),
        "available_presets": [p.preset_id for p in presets],
        "configured": {
            "trust_anchor": bool(bootstrap.trust_anchor_fingerprint),
            "initial_admin": bool(bootstrap.bootstrap_completed_by),
            "secret_storage": bool(bootstrap.secret_storage_mode),
            "initial_provider": bool(AIProviderConfig.query.count()),
        },
    }


def ensure_governance_baseline() -> None:
    """Ensure baseline bootstrap and operational setting rows exist."""
    try:
        inspector = inspect(db.engine)
        if not inspector.has_table("bootstrap_configs") or not inspector.has_table("system_setting_records"):
            return
    except OperationalError:
        return

    bootstrap = BootstrapConfig.query.order_by(BootstrapConfig.created_at.desc()).first()
    if bootstrap is None:
        bootstrap = BootstrapConfig(
            bootstrap_state="uninitialized",
            bootstrap_locked=False,
            selected_preset=None,
            secret_storage_mode="same_db_encrypted",
            runtime_profile="safe_local",
            generation_execution_mode="mock_only",
            retrieval_execution_mode="disabled",
            validation_execution_mode="schema_only",
            provider_selection_mode="local_only",
            reopen_requires_elevated_auth=True,
            trust_anchor_metadata_json={},
        )
        db.session.add(bootstrap)

    defaults: dict[str, dict[str, object]] = {
        "backend": {
            "play_service_internal_url": current_app.config.get("PLAY_SERVICE_INTERNAL_URL"),
            "play_service_public_url": current_app.config.get("PLAY_SERVICE_PUBLIC_URL"),
            "play_service_request_timeout_seconds": int(current_app.config.get("PLAY_SERVICE_REQUEST_TIMEOUT", 30)),
            "game_ticket_ttl_seconds": int(current_app.config.get("PLAY_SERVICE_TICKET_TTL_SECONDS", 900)),
        },
        "notifications": {
            "mail_enabled": bool(current_app.config.get("MAIL_ENABLED", False)),
            "email_verification_enabled": bool(current_app.config.get("EMAIL_VERIFICATION_ENABLED", True)),
            "verification_ttl_minutes": int(current_app.config.get("EMAIL_VERIFICATION_TOKEN_TTL_MINUTES", 30)),
        },
        "costs": {
            "daily_global_limit": "50.00",
            "monthly_global_limit": "1000.00",
            "warning_threshold_percent": 80,
            "hard_stop_enabled": False,
        },
        "retrieval": {
            "retrieval_execution_mode": bootstrap.retrieval_execution_mode,
            "embeddings_enabled": False,
            "embedding_cache_policy": "default",
        },
        "world_engine": {
            "validation_execution_mode": bootstrap.validation_execution_mode,
            "max_retry_attempts": 1,
            "enable_corrective_feedback": True,
            "preview_isolation_mode": "in_memory_namespace",
            "runtime_diagnostics_verbosity": "operator",
        },
    }
    for scope, values in defaults.items():
        for setting_key, setting_value in values.items():
            setting_id = _slug(f"{scope}_{setting_key}")
            if SystemSettingRecord.query.get(setting_id) is None:
                db.session.add(
                    SystemSettingRecord(
                        setting_id=setting_id,
                        scope=scope,
                        setting_key=setting_key,
                        setting_value_json=setting_value,
                        is_secret_backed=False,
                        is_user_visible=True,
                        updated_by="system",
                    )
                )
    _seed_default_presets()
    db.session.commit()


def list_bootstrap_presets() -> list[dict]:
    """List preset definitions."""
    _seed_default_presets()
    db.session.flush()
    presets = BootstrapPreset.query.order_by(BootstrapPreset.display_name.asc()).all()
    out: list[dict] = []
    for preset in presets:
        out.append(
            {
                "preset_id": preset.preset_id,
                "display_name": preset.display_name,
                "description": preset.description,
                "generation_execution_mode": preset.generation_execution_mode,
                "retrieval_execution_mode": preset.retrieval_execution_mode,
                "validation_execution_mode": preset.validation_execution_mode,
                "provider_selection_mode": preset.provider_selection_mode,
                "runtime_profile": preset.default_runtime_profile,
                "provider_templates": preset.default_provider_templates_json,
                "budget_policy": preset.default_budget_policy_json,
            }
        )
    return out


def initialize_bootstrap(payload: dict, actor: str) -> dict:
    """Initialize bootstrap config and optional initial provider/credential."""
    _seed_default_presets()
    db.session.flush()
    existing = BootstrapConfig.query.order_by(BootstrapConfig.created_at.desc()).first()
    if existing and existing.bootstrap_locked:
        raise governance_error("bootstrap_already_initialized", "Bootstrap is already initialized and locked.", 409, {})

    preset_id = (payload.get("selected_preset") or "").strip()
    preset = BootstrapPreset.query.get(preset_id)
    if preset is None:
        raise governance_error(
            "preset_not_found",
            f"Preset '{preset_id}' does not exist.",
            404,
            {"available_presets": [p.preset_id for p in BootstrapPreset.query.all()]},
        )

    admin_email = (payload.get("admin_email") or "").strip()
    if not admin_email:
        raise governance_error("bootstrap_missing_admin_identity", "admin_email is required.", 400, {})

    secret_storage_mode = (payload.get("secret_storage_mode") or "").strip() or preset.default_budget_policy_json.get(
        "secret_storage_mode", "same_db_encrypted"
    )
    if secret_storage_mode not in {"same_db_encrypted", "separate_secret_db_encrypted", "external_secret_manager"}:
        raise governance_error("bootstrap_secret_storage_invalid", "Unsupported secret storage mode.", 400, {"mode": secret_storage_mode})

    bootstrap = existing or BootstrapConfig(
        bootstrap_state="initializing",
        bootstrap_locked=False,
        selected_preset=preset_id,
        secret_storage_mode=secret_storage_mode,
        runtime_profile=payload.get("runtime_profile") or preset.default_runtime_profile,
        generation_execution_mode=payload.get("generation_execution_mode") or preset.generation_execution_mode,
        retrieval_execution_mode=payload.get("retrieval_execution_mode") or preset.retrieval_execution_mode,
        validation_execution_mode=payload.get("validation_execution_mode") or preset.validation_execution_mode,
        provider_selection_mode=payload.get("provider_selection_mode") or preset.provider_selection_mode,
        reopen_requires_elevated_auth=bool(payload.get("trust_anchor", {}).get("allow_reopen_with_recovery_token", True)),
    )
    bootstrap.bootstrap_state = "initialized"
    bootstrap.bootstrap_locked = True
    bootstrap.selected_preset = preset_id
    bootstrap.secret_storage_mode = secret_storage_mode
    bootstrap.runtime_profile = payload.get("runtime_profile") or preset.default_runtime_profile
    bootstrap.generation_execution_mode = payload.get("generation_execution_mode") or preset.generation_execution_mode
    bootstrap.retrieval_execution_mode = payload.get("retrieval_execution_mode") or preset.retrieval_execution_mode
    bootstrap.validation_execution_mode = payload.get("validation_execution_mode") or preset.validation_execution_mode
    bootstrap.provider_selection_mode = payload.get("provider_selection_mode") or preset.provider_selection_mode
    bootstrap.bootstrap_completed_at = datetime.now(timezone.utc)
    bootstrap.bootstrap_completed_by = admin_email
    bootstrap.trust_anchor_fingerprint = f"sha256:{uuid4().hex[:16]}"
    bootstrap.trust_anchor_metadata_json = payload.get("trust_anchor") or {}

    db.session.add(bootstrap)
    _audit("bootstrap_initialized", "bootstrap", "bootstrap_config", actor, "Bootstrap initialized.", {"preset_id": preset_id})

    initial_provider = payload.get("initial_provider") or {}
    provider: AIProviderConfig | None = None
    if initial_provider:
        provider = create_provider(initial_provider, actor)
        initial_credential = payload.get("initial_credential") or {}
        if initial_credential and initial_credential.get("api_key"):
            write_provider_credential(provider.provider_id, {"api_key": initial_credential["api_key"]}, actor)

    if provider is None:
        _ensure_default_mock_path(actor)
    db.session.commit()
    return {
        "bootstrap_status": "initialized",
        "bootstrap_locked": True,
        "secret_storage_mode": bootstrap.secret_storage_mode,
        "trust_anchor_fingerprint": bootstrap.trust_anchor_fingerprint,
        "next_actions": ["launch_stack", "open_administration_tool", "configure_models_and_routes"],
        "stack_start_ready": True,
    }


def reopen_bootstrap(payload: dict, actor: str) -> dict:
    """Reopen bootstrap in explicit recovery mode."""
    bootstrap = BootstrapConfig.query.order_by(BootstrapConfig.created_at.desc()).first()
    if bootstrap is None:
        raise governance_error("bootstrap_recovery_token_invalid", "Bootstrap has not been initialized yet.", 403, {})
    recovery_token = (payload.get("recovery_token") or "").strip()
    configured_token = (current_app.config.get("BOOTSTRAP_RECOVERY_TOKEN") or "").strip()
    if not recovery_token or not configured_token or recovery_token != configured_token:
        raise governance_error("bootstrap_recovery_token_invalid", "Recovery token is invalid.", 403, {})
    bootstrap.bootstrap_state = "bootstrap_recovery_required"
    bootstrap.bootstrap_locked = False
    _audit("bootstrap_reopened", "bootstrap", "bootstrap_config", actor, "Bootstrap reopened in recovery mode.", {})
    db.session.commit()
    return {
        "bootstrap_reopen_status": "accepted",
        "recovery_mode": True,
        "allowed_sections": ["secret_storage", "provider_credentials", "runtime_modes"],
    }


def list_providers() -> list[dict]:
    rows = AIProviderConfig.query.order_by(AIProviderConfig.provider_id.asc()).all()
    return [
        {
            "provider_id": row.provider_id,
            "provider_type": row.provider_type,
            "display_name": row.display_name,
            "base_url": row.base_url,
            "is_enabled": row.is_enabled,
            "is_local": row.is_local,
            "supports_structured_output": row.supports_structured_output,
            "credential_configured": row.credential_configured,
            "credential_fingerprint": row.credential_fingerprint,
            "health_status": row.health_status,
            "last_tested_at": row.last_tested_at.isoformat() if row.last_tested_at else None,
            "allow_live_runtime": row.allow_live_runtime,
            "allow_preview_runtime": row.allow_preview_runtime,
            "allow_writers_room": row.allow_writers_room,
            "allow_research_suite": row.allow_research_suite,
        }
        for row in rows
    ]


def create_provider(payload: dict, actor: str) -> AIProviderConfig:
    """Create provider configuration."""
    provider_type = (payload.get("provider_type") or "").strip()
    display_name = (payload.get("display_name") or "").strip()
    if not provider_type or not display_name:
        raise governance_error("setting_value_invalid", "provider_type and display_name are required.", 400, {})
    provider_id = _slug(payload.get("provider_id") or f"{provider_type}_{display_name}")
    existing = AIProviderConfig.query.get(provider_id)
    if existing:
        return existing
    provider = AIProviderConfig(
        provider_id=provider_id,
        provider_type=provider_type,
        display_name=display_name,
        base_url=(payload.get("base_url") or "").strip() or None,
        is_enabled=bool(payload.get("is_enabled", True)),
        is_local=bool(payload.get("is_local", provider_type in {"mock", "ollama"})),
        supports_structured_output=bool(payload.get("supports_structured_output", False)),
        allow_live_runtime=bool(payload.get("allow_live_runtime", True)),
        allow_preview_runtime=bool(payload.get("allow_preview_runtime", True)),
        allow_writers_room=bool(payload.get("allow_writers_room", True)),
        allow_research_suite=bool(payload.get("allow_research_suite", True)),
    )
    db.session.add(provider)
    _audit("provider_created", "ai_runtime", provider.provider_id, actor, "Provider created.", {"provider_type": provider.provider_type})
    return provider


def update_provider(provider_id: str, payload: dict, actor: str) -> AIProviderConfig:
    provider = AIProviderConfig.query.get(provider_id)
    if provider is None:
        raise governance_error("provider_not_found", f"Provider '{provider_id}' not found.", 404, {"provider_id": provider_id})
    for key in (
        "display_name",
        "base_url",
        "is_enabled",
        "is_local",
        "supports_structured_output",
        "allow_live_runtime",
        "allow_preview_runtime",
        "allow_writers_room",
        "allow_research_suite",
    ):
        if key in payload:
            setattr(provider, key, payload[key])
    provider.updated_at = datetime.now(timezone.utc)
    _audit("provider_updated", "ai_runtime", provider.provider_id, actor, "Provider updated.", {})
    db.session.commit()
    return provider


def write_provider_credential(provider_id: str, payload: dict, actor: str) -> dict:
    """Write/replace provider credential in write-only mode."""
    provider = AIProviderConfig.query.get(provider_id)
    if provider is None:
        raise governance_error("provider_not_found", f"Provider '{provider_id}' not found.", 404, {"provider_id": provider_id})
    api_key = (payload.get("api_key") or payload.get("new_api_key") or "").strip()
    if not api_key:
        raise governance_error("provider_secret_rejected", "api_key is required.", 400, {})
    record = encrypt_secret(api_key)
    active = AIProviderCredential.query.filter_by(provider_id=provider_id, is_active=True).first()
    if active is not None:
        if active.rotation_in_progress:
            raise governance_error("credential_rotation_in_progress", "Credential rotation already in progress.", 409, {"provider_id": provider_id})
        active.is_active = False
    credential = AIProviderCredential(
        credential_id=f"cred_{uuid4().hex}",
        provider_id=provider_id,
        secret_name="api_key",
        encrypted_secret=record.encrypted_secret,
        encrypted_dek=record.encrypted_dek,
        secret_nonce=record.secret_nonce,
        dek_nonce=record.dek_nonce,
        dek_algorithm=record.dek_algorithm,
        secret_fingerprint=record.secret_fingerprint,
        is_active=True,
        rotated_at=datetime.now(timezone.utc),
    )
    provider.credential_configured = True
    provider.credential_fingerprint = record.secret_fingerprint
    db.session.add(credential)
    _audit("provider_credential_written", "ai_runtime", provider_id, actor, "Provider credential rotated.", {"fingerprint": record.secret_fingerprint})
    db.session.commit()
    return {
        "provider_id": provider_id,
        "credential_written": True,
        "credential_fingerprint": record.secret_fingerprint,
        "rotated_at": credential.rotated_at.isoformat() if credential.rotated_at else None,
    }


def test_provider_connection(provider_id: str, actor: str) -> dict:
    """Persist provider health status from simple configuration checks."""
    provider = AIProviderConfig.query.get(provider_id)
    if provider is None:
        raise governance_error("provider_not_found", f"Provider '{provider_id}' not found.", 404, {"provider_id": provider_id})
    if provider.provider_type != "mock" and not provider.credential_configured:
        raise governance_error("provider_credential_required", "Provider requires credential before health test.", 400, {"provider_id": provider_id})
    tested_at = datetime.now(timezone.utc)
    health_status = "healthy" if provider.is_enabled else "disabled"
    if provider.provider_type != "mock" and not provider.base_url:
        health_status = "degraded"
    provider.health_status = health_status
    provider.last_tested_at = tested_at
    db.session.add(
        ProviderHealthCheck(
            health_check_id=f"health_{uuid4().hex}",
            provider_id=provider_id,
            health_status=health_status,
            latency_ms=0,
            tested_at=tested_at,
        )
    )
    _audit("provider_health_tested", "ai_runtime", provider_id, actor, "Provider health test executed.", {"health_status": health_status})
    db.session.commit()
    return {
        "provider_id": provider_id,
        "health_status": health_status,
        "latency_ms": 0,
        "tested_at": tested_at.isoformat(),
    }


def list_models() -> list[dict]:
    rows = AIModelConfig.query.order_by(AIModelConfig.model_id.asc()).all()
    return [
        {
            "model_id": row.model_id,
            "provider_id": row.provider_id,
            "model_name": row.model_name,
            "display_name": row.display_name,
            "model_role": row.model_role,
            "is_enabled": row.is_enabled,
            "structured_output_capable": row.structured_output_capable,
            "timeout_seconds": row.timeout_seconds,
            "max_context_tokens": row.max_context_tokens,
            "cost_method": row.cost_method,
            "input_price_per_1k": str(row.input_price_per_1k) if row.input_price_per_1k is not None else None,
            "output_price_per_1k": str(row.output_price_per_1k) if row.output_price_per_1k is not None else None,
            "flat_request_price": str(row.flat_request_price) if row.flat_request_price is not None else None,
        }
        for row in rows
    ]


def create_model(payload: dict, actor: str) -> AIModelConfig:
    provider_id = (payload.get("provider_id") or "").strip()
    provider = AIProviderConfig.query.get(provider_id)
    if provider is None:
        raise governance_error("provider_not_found", f"Provider '{provider_id}' not found.", 404, {"provider_id": provider_id})
    model_name = (payload.get("model_name") or "").strip()
    if not model_name:
        raise governance_error("setting_value_invalid", "model_name is required.", 400, {})
    model_id = _slug(payload.get("model_id") or f"{provider_id}_{model_name}")
    model = AIModelConfig.query.get(model_id)
    if model:
        return model
    model = AIModelConfig(
        model_id=model_id,
        provider_id=provider_id,
        model_name=model_name,
        display_name=(payload.get("display_name") or model_name).strip(),
        model_role=(payload.get("model_role") or "llm").strip(),
        is_enabled=bool(payload.get("is_enabled", True)),
        structured_output_capable=bool(payload.get("supports_structured_output", payload.get("structured_output_capable", False))),
        timeout_seconds=int(payload.get("timeout_seconds", 30)),
        max_context_tokens=payload.get("max_context_tokens"),
        cost_method=(payload.get("cost_method") or "none").strip(),
        input_price_per_1k=Decimal(str(payload["input_price_per_1k"])) if payload.get("input_price_per_1k") is not None else None,
        output_price_per_1k=Decimal(str(payload["output_price_per_1k"])) if payload.get("output_price_per_1k") is not None else None,
        flat_request_price=Decimal(str(payload["flat_request_price"])) if payload.get("flat_request_price") is not None else None,
    )
    db.session.add(model)
    _audit("model_created", "ai_runtime", model_id, actor, "Model created.", {"provider_id": provider_id})
    db.session.commit()
    return model


def update_model(model_id: str, payload: dict, actor: str) -> AIModelConfig:
    model = AIModelConfig.query.get(model_id)
    if model is None:
        raise governance_error("model_not_found", f"Model '{model_id}' not found.", 404, {"model_id": model_id})
    for key in (
        "display_name",
        "model_role",
        "is_enabled",
        "structured_output_capable",
        "timeout_seconds",
        "max_context_tokens",
        "cost_method",
    ):
        if key in payload:
            setattr(model, key, payload[key])
    for key in ("input_price_per_1k", "output_price_per_1k", "flat_request_price"):
        if key in payload:
            value = payload[key]
            setattr(model, key, Decimal(str(value)) if value is not None else None)
    model.updated_at = datetime.now(timezone.utc)
    _audit("model_updated", "ai_runtime", model_id, actor, "Model updated.", {})
    db.session.commit()
    return model


def list_routes() -> list[dict]:
    rows = AITaskRoute.query.order_by(AITaskRoute.route_id.asc()).all()
    return [
        {
            "route_id": row.route_id,
            "task_kind": row.task_kind,
            "workflow_scope": row.workflow_scope,
            "preferred_model_id": row.preferred_model_id,
            "fallback_model_id": row.fallback_model_id,
            "mock_model_id": row.mock_model_id,
            "is_enabled": row.is_enabled,
            "use_mock_when_provider_unavailable": row.use_mock_when_provider_unavailable,
        }
        for row in rows
    ]


def _ensure_model_exists(model_id: str | None) -> None:
    if model_id is None:
        return
    model = AIModelConfig.query.get(model_id)
    if model is None or not model.is_enabled:
        raise governance_error("route_invalid_model_reference", "Route references missing or disabled model.", 409, {"model_id": model_id})


def create_route(payload: dict, actor: str) -> AITaskRoute:
    route_id = _slug(payload.get("route_id") or f"{payload.get('task_kind','task')}_{payload.get('workflow_scope','global')}")
    for field in ("preferred_model_id", "fallback_model_id", "mock_model_id"):
        _ensure_model_exists(payload.get(field))
    route = AITaskRoute.query.get(route_id)
    if route:
        return route
    route = AITaskRoute(
        route_id=route_id,
        task_kind=(payload.get("task_kind") or "").strip(),
        workflow_scope=(payload.get("workflow_scope") or "global").strip(),
        preferred_model_id=payload.get("preferred_model_id"),
        fallback_model_id=payload.get("fallback_model_id"),
        mock_model_id=payload.get("mock_model_id"),
        is_enabled=bool(payload.get("is_enabled", True)),
        use_mock_when_provider_unavailable=bool(payload.get("use_mock_when_provider_unavailable", True)),
    )
    db.session.add(route)
    _audit("route_created", "ai_runtime", route_id, actor, "Route created.", {})
    db.session.commit()
    return route


def update_route(route_id: str, payload: dict, actor: str) -> AITaskRoute:
    route = AITaskRoute.query.get(route_id)
    if route is None:
        raise governance_error("route_not_found", f"Route '{route_id}' not found.", 404, {"route_id": route_id})
    for field in ("preferred_model_id", "fallback_model_id", "mock_model_id"):
        if field in payload:
            _ensure_model_exists(payload.get(field))
            setattr(route, field, payload.get(field))
    for field in ("task_kind", "workflow_scope", "is_enabled", "use_mock_when_provider_unavailable"):
        if field in payload:
            setattr(route, field, payload.get(field))
    route.updated_at = datetime.now(timezone.utc)
    _audit("route_updated", "ai_runtime", route_id, actor, "Route updated.", {})
    db.session.commit()
    return route


def _current_bootstrap() -> BootstrapConfig:
    bootstrap = BootstrapConfig.query.order_by(BootstrapConfig.created_at.desc()).first()
    if bootstrap is None:
        bootstrap = BootstrapConfig(
            bootstrap_state="uninitialized",
            bootstrap_locked=False,
            selected_preset=None,
            secret_storage_mode="same_db_encrypted",
            runtime_profile="safe_local",
            generation_execution_mode="mock_only",
            retrieval_execution_mode="disabled",
            validation_execution_mode="schema_only",
            provider_selection_mode="local_only",
            reopen_requires_elevated_auth=True,
            trust_anchor_metadata_json={},
        )
        db.session.add(bootstrap)
        _seed_default_presets()
        db.session.commit()
    return bootstrap


def get_runtime_modes() -> dict:
    bootstrap = _current_bootstrap()
    return {
        "generation_execution_mode": bootstrap.generation_execution_mode,
        "retrieval_execution_mode": bootstrap.retrieval_execution_mode,
        "validation_execution_mode": bootstrap.validation_execution_mode,
        "provider_selection_mode": bootstrap.provider_selection_mode,
        "runtime_profile": bootstrap.runtime_profile,
    }


def update_runtime_modes(payload: dict, actor: str) -> dict:
    bootstrap = _current_bootstrap()
    updates = {
        "generation_execution_mode": payload.get("generation_execution_mode", bootstrap.generation_execution_mode),
        "retrieval_execution_mode": payload.get("retrieval_execution_mode", bootstrap.retrieval_execution_mode),
        "validation_execution_mode": payload.get("validation_execution_mode", bootstrap.validation_execution_mode),
        "provider_selection_mode": payload.get("provider_selection_mode", bootstrap.provider_selection_mode),
        "runtime_profile": payload.get("runtime_profile", bootstrap.runtime_profile),
    }
    _validate_runtime_modes(updates)
    for key, value in updates.items():
        setattr(bootstrap, key, value)
    _audit("runtime_modes_updated", "ai_runtime", "runtime_modes", actor, "Runtime modes updated.", updates)
    db.session.commit()
    return {"updated": True, "runtime_profile": bootstrap.runtime_profile, "effective_generation_execution_mode": bootstrap.generation_execution_mode}


def _validate_runtime_modes(modes: dict) -> None:
    generation_mode = modes["generation_execution_mode"]
    providers = AIProviderConfig.query.filter_by(is_enabled=True).all()
    routes = AITaskRoute.query.filter_by(is_enabled=True).all()
    real_provider_ids = {p.provider_id for p in providers if p.provider_type != "mock" and p.credential_configured}
    route_models: set[str] = set()
    has_mock_fallback = False
    for route in routes:
        for mid in (route.preferred_model_id, route.fallback_model_id):
            if mid:
                model = AIModelConfig.query.get(mid)
                if model and model.provider_id in real_provider_ids and model.is_enabled:
                    route_models.add(mid)
        if route.mock_model_id:
            model = AIModelConfig.query.get(route.mock_model_id)
            if model and model.is_enabled and model.model_role == "mock":
                has_mock_fallback = True
    if generation_mode in {"ai_only", "routed_llm_slm"} and (not real_provider_ids or not route_models):
        raise governance_error(
            "generation_mode_invalid",
            "AI execution mode requires at least one enabled provider/model route set.",
            400,
            {"generation_execution_mode": generation_mode},
        )
    if generation_mode == "hybrid_routed_with_mock_fallback" and not has_mock_fallback:
        raise governance_error(
            "route_requires_mock_model_for_hybrid_mode",
            "Hybrid mode requires a mock-capable fallback route.",
            409,
            {},
        )


def _resolve_provider_selection(providers: list[AIProviderConfig], provider_selection_mode: str) -> list[AIProviderConfig]:
    if provider_selection_mode == "local_only":
        selected = [p for p in providers if p.is_local]
    elif provider_selection_mode == "remote_preferred":
        remote = [p for p in providers if not p.is_local]
        selected = remote or providers
    else:
        selected = providers
    return selected


def _validate_and_resolve_routes(*, routes: list[AITaskRoute], models_by_id: dict[str, AIModelConfig], selected_provider_ids: set[str], generation_execution_mode: str) -> list[dict]:
    """Validate route model references and return resolved route payload."""
    missing_required_tasks = {task for task in _REQUIRED_TASK_KINDS}
    resolved_routes: list[dict] = []
    for route in routes:
        missing_required_tasks.discard(route.task_kind)
        for ref_name in ("preferred_model_id", "fallback_model_id", "mock_model_id"):
            ref_id = getattr(route, ref_name)
            if ref_id is None:
                continue
            model = models_by_id.get(ref_id)
            if model is None:
                raise governance_error("resolved_config_generation_failed", "Route references missing model.", 500, {"route_id": route.route_id, "model_id": ref_id})
            if model.provider_id not in selected_provider_ids and model.model_role != "mock":
                raise governance_error(
                    "resolved_config_generation_failed",
                    "Route references model whose provider is not currently selectable.",
                    500,
                    {"route_id": route.route_id, "model_id": ref_id, "provider_id": model.provider_id},
                )
        resolved_routes.append(
            {
                "route_id": route.route_id,
                "task_kind": route.task_kind,
                "workflow_scope": route.workflow_scope,
                "preferred_model_id": route.preferred_model_id,
                "fallback_model_id": route.fallback_model_id,
                "mock_model_id": route.mock_model_id,
                "effective_strategy": "hybrid" if route.use_mock_when_provider_unavailable else "strict",
            }
        )
    if missing_required_tasks and generation_execution_mode != "mock_only":
        raise governance_error(
            "resolved_config_generation_failed",
            "Not all required task kinds have enabled routes.",
            500,
            {"missing_task_kinds": sorted(missing_required_tasks)},
        )
    return resolved_routes


def _serialize_provider_rows(providers: list[AIProviderConfig]) -> list[dict]:
    return [
        {
            "provider_id": provider.provider_id,
            "provider_type": provider.provider_type,
            "base_url": provider.base_url,
            "resolved_secret_ref": f"credential:{provider.provider_id}" if provider.credential_configured else None,
            "credential_configured": provider.credential_configured,
            "is_enabled": True,
            "health_status": provider.health_status,
        }
        for provider in providers
    ]


def _serialize_model_rows(models: list[AIModelConfig], selected_provider_ids: set[str]) -> list[dict]:
    return [
        {
            "model_id": model.model_id,
            "provider_id": model.provider_id,
            "model_name": model.model_name,
            "model_role": model.model_role,
            "timeout_seconds": model.timeout_seconds,
            "structured_output_capable": model.structured_output_capable,
        }
        for model in models
        if model.provider_id in selected_provider_ids
    ]


def _collect_scope_settings() -> dict[str, dict]:
    return {
        "backend_settings": read_scope_settings("backend"),
        "world_engine_settings": read_scope_settings("world_engine"),
        "retrieval_settings": read_scope_settings("retrieval"),
        "cost_settings": read_scope_settings("costs"),
        "notification_settings": read_scope_settings("notifications"),
    }


def _persist_resolved_snapshot(*, config_version: str, bootstrap: BootstrapConfig, resolved: dict, actor: str) -> None:
    ResolvedRuntimeConfigSnapshot.query.filter_by(is_active=True).update({"is_active": False})
    db.session.add(
        ResolvedRuntimeConfigSnapshot(
            snapshot_id=f"snap_{uuid4().hex}",
            config_version=config_version,
            generation_execution_mode=bootstrap.generation_execution_mode,
            retrieval_execution_mode=bootstrap.retrieval_execution_mode,
            validation_execution_mode=bootstrap.validation_execution_mode,
            runtime_profile=bootstrap.runtime_profile,
            provider_selection_mode=bootstrap.provider_selection_mode,
            resolved_config_json=resolved,
            is_active=True,
        )
    )
    _audit("resolved_config_rebuilt", "ai_runtime", config_version, actor, "Resolved runtime config rebuilt.", {})
    db.session.commit()


def build_resolved_runtime_config(*, persist_snapshot: bool, actor: str) -> dict:
    """Resolve active runtime config and validate route completeness."""
    bootstrap = _current_bootstrap()
    providers = AIProviderConfig.query.filter_by(is_enabled=True).all()
    providers = _resolve_provider_selection(providers, bootstrap.provider_selection_mode)
    models = AIModelConfig.query.filter_by(is_enabled=True).all()
    models_by_id = {m.model_id: m for m in models}
    selected_provider_ids = {p.provider_id for p in providers}
    routes = AITaskRoute.query.filter_by(is_enabled=True).all()
    resolved_routes = _validate_and_resolve_routes(
        routes=routes,
        models_by_id=models_by_id,
        selected_provider_ids=selected_provider_ids,
        generation_execution_mode=bootstrap.generation_execution_mode,
    )
    providers_out = _serialize_provider_rows(providers)
    models_out = _serialize_model_rows(models, selected_provider_ids)
    scoped_settings = _collect_scope_settings()

    generated_at = datetime.now(timezone.utc)
    config_version = f"cfg_{generated_at.strftime('%Y%m%d_%H%M%S')}_{uuid4().hex[:6]}"
    resolved = {
        "config_version": config_version,
        "generated_at": generated_at.isoformat(),
        "generation_execution_mode": bootstrap.generation_execution_mode,
        "retrieval_execution_mode": bootstrap.retrieval_execution_mode,
        "validation_execution_mode": bootstrap.validation_execution_mode,
        "runtime_profile": bootstrap.runtime_profile,
        "provider_selection_mode": bootstrap.provider_selection_mode,
        "providers": providers_out,
        "models": models_out,
        "routes": resolved_routes,
        **scoped_settings,
    }
    if persist_snapshot:
        _persist_resolved_snapshot(
            config_version=config_version,
            bootstrap=bootstrap,
            resolved=resolved,
            actor=actor,
        )
    return resolved


def get_active_runtime_snapshot() -> dict | None:
    """Return active resolved snapshot, if one exists."""
    row = ResolvedRuntimeConfigSnapshot.query.filter_by(is_active=True).order_by(ResolvedRuntimeConfigSnapshot.generated_at.desc()).first()
    if row is None:
        return None
    return row.resolved_config_json or None


def _ensure_default_mock_path(actor: str) -> None:
    provider = AIProviderConfig.query.get("mock_default")
    if provider is None:
        provider = AIProviderConfig(
            provider_id="mock_default",
            provider_type="mock",
            display_name="Mock Default",
            is_enabled=True,
            is_local=True,
            supports_structured_output=True,
            credential_configured=False,
            health_status="healthy",
        )
        db.session.add(provider)
    model = AIModelConfig.query.get("mock_deterministic")
    if model is None:
        model = AIModelConfig(
            model_id="mock_deterministic",
            provider_id=provider.provider_id,
            model_name="mock-deterministic",
            display_name="Mock Deterministic",
            model_role="mock",
            is_enabled=True,
            structured_output_capable=True,
            timeout_seconds=5,
            cost_method="none",
        )
        db.session.add(model)
    for task_kind in _REQUIRED_TASK_KINDS:
        route_id = f"{task_kind}_global"
        if AITaskRoute.query.get(route_id) is None:
            db.session.add(
                AITaskRoute(
                    route_id=route_id,
                    task_kind=task_kind,
                    workflow_scope="global",
                    preferred_model_id=model.model_id,
                    fallback_model_id=model.model_id,
                    mock_model_id=model.model_id,
                    is_enabled=True,
                    use_mock_when_provider_unavailable=True,
                )
            )
    _audit("mock_path_seeded", "ai_runtime", "mock_default", actor, "Default mock path ensured.", {})


def read_scope_settings(scope: str) -> dict:
    rows = SystemSettingRecord.query.filter_by(scope=scope).all()
    return {row.setting_key: row.setting_value_json for row in rows}


def update_scope_settings(scope: str, payload: dict, actor: str) -> dict:
    for setting_key, setting_value in payload.items():
        setting_id = _slug(f"{scope}_{setting_key}")
        row = SystemSettingRecord.query.get(setting_id)
        if row is None:
            row = SystemSettingRecord(
                setting_id=setting_id,
                scope=scope,
                setting_key=setting_key,
                setting_value_json=setting_value,
                is_secret_backed=False,
                is_user_visible=True,
                updated_by=actor,
            )
            db.session.add(row)
        else:
            row.setting_value_json = setting_value
            row.updated_by = actor
            row.updated_at = datetime.now(timezone.utc)
        _audit("setting_updated", scope, setting_key, actor, "Setting updated.", {"scope": scope})
    db.session.commit()
    return read_scope_settings(scope)


def ingest_usage_event(payload: dict, actor: str) -> dict:
    event = AIUsageEvent(
        usage_event_id=payload.get("usage_event_id") or f"evt_{uuid4().hex}",
        provider_id=payload.get("provider_id"),
        model_id=payload.get("model_id"),
        task_kind=payload["task_kind"],
        workflow_scope=payload.get("workflow_scope") or "global",
        request_id=payload["request_id"],
        success=bool(payload.get("success", True)),
        latency_ms=payload.get("latency_ms"),
        input_tokens=payload.get("input_tokens"),
        output_tokens=payload.get("output_tokens"),
        provider_reported_cost=Decimal(str(payload["provider_reported_cost"])) if payload.get("provider_reported_cost") is not None else None,
        estimated_cost=Decimal(str(payload["estimated_cost"])) if payload.get("estimated_cost") is not None else None,
        cost_method_used=payload.get("cost_method_used") or "none",
        degraded_mode_used=bool(payload.get("degraded_mode_used", False)),
        retry_used=bool(payload.get("retry_used", False)),
        fallback_used=bool(payload.get("fallback_used", False)),
    )
    db.session.add(event)
    _audit("usage_event_ingested", "costs", event.usage_event_id, actor, "Usage event ingested.", {})
    db.session.commit()
    return {"usage_event_id": event.usage_event_id, "created_at": event.created_at.isoformat() if event.created_at else None}


def list_usage_events(limit: int = 100) -> list[dict]:
    rows = AIUsageEvent.query.order_by(AIUsageEvent.created_at.desc()).limit(limit).all()
    return [
        {
            "usage_event_id": row.usage_event_id,
            "provider_id": row.provider_id,
            "model_id": row.model_id,
            "task_kind": row.task_kind,
            "workflow_scope": row.workflow_scope,
            "input_tokens": row.input_tokens,
            "output_tokens": row.output_tokens,
            "provider_reported_cost": str(row.provider_reported_cost) if row.provider_reported_cost is not None else None,
            "estimated_cost": str(row.estimated_cost) if row.estimated_cost is not None else None,
            "cost_method_used": row.cost_method_used,
            "fallback_used": row.fallback_used,
            "retry_used": row.retry_used,
            "degraded_mode_used": row.degraded_mode_used,
            "created_at": row.created_at.isoformat() if row.created_at else None,
        }
        for row in rows
    ]


def upsert_budget(policy_id: str | None, payload: dict, actor: str) -> CostBudgetPolicy:
    warning = int(payload.get("warning_threshold_percent", 80))
    if warning < 1 or warning > 100:
        raise governance_error("budget_invalid_threshold", "warning_threshold_percent must be between 1 and 100.", 400, {"warning_threshold_percent": warning})
    budget_policy_id = policy_id or f"budget_{uuid4().hex}"
    budget = CostBudgetPolicy.query.get(budget_policy_id)
    if budget is None:
        budget = CostBudgetPolicy(
            budget_policy_id=budget_policy_id,
            scope_kind=(payload.get("scope_kind") or "global").strip(),
            scope_ref=(payload.get("scope_ref") or "").strip() or None,
        )
        db.session.add(budget)
    budget.daily_limit = Decimal(str(payload["daily_limit"])) if payload.get("daily_limit") is not None else None
    budget.monthly_limit = Decimal(str(payload["monthly_limit"])) if payload.get("monthly_limit") is not None else None
    budget.warning_threshold_percent = warning
    budget.hard_stop_enabled = bool(payload.get("hard_stop_enabled", False))
    _audit("budget_updated", "costs", budget_policy_id, actor, "Budget policy upserted.", {})
    db.session.commit()
    return budget


def list_budgets() -> list[dict]:
    rows = CostBudgetPolicy.query.order_by(CostBudgetPolicy.scope_kind.asc(), CostBudgetPolicy.scope_ref.asc()).all()
    return [
        {
            "budget_policy_id": row.budget_policy_id,
            "scope_kind": row.scope_kind,
            "scope_ref": row.scope_ref,
            "daily_limit": str(row.daily_limit) if row.daily_limit is not None else None,
            "monthly_limit": str(row.monthly_limit) if row.monthly_limit is not None else None,
            "warning_threshold_percent": row.warning_threshold_percent,
            "hard_stop_enabled": row.hard_stop_enabled,
        }
        for row in rows
    ]


def rebuild_rollups(actor: str) -> list[dict]:
    """Rebuild daily rollups from usage events."""
    rows = AIUsageEvent.query.all()
    grouped: dict[tuple[date, str | None, str | None, str | None], list[AIUsageEvent]] = defaultdict(list)
    for row in rows:
        if row.created_at is None:
            continue
        grouped[(row.created_at.date(), row.provider_id, row.model_id, row.workflow_scope)].append(row)
    CostRollup.query.delete()
    out: list[dict] = []
    for key, events in grouped.items():
        rollup_date, provider_id, model_id, workflow_scope = key
        estimated_total = Decimal("0")
        provider_total: Decimal | None = Decimal("0")
        for event in events:
            if event.estimated_cost is not None:
                estimated_total += event.estimated_cost
            if event.provider_reported_cost is None:
                provider_total = None
            elif provider_total is not None:
                provider_total += event.provider_reported_cost
        rollup = CostRollup(
            rollup_id=f"roll_{uuid4().hex}",
            rollup_date=rollup_date,
            provider_id=provider_id,
            model_id=model_id,
            workflow_scope=workflow_scope,
            request_count=len(events),
            estimated_cost_total=estimated_total,
            provider_reported_cost_total=provider_total,
            retry_count=sum(1 for event in events if event.retry_used),
            fallback_count=sum(1 for event in events if event.fallback_used),
        )
        db.session.add(rollup)
        out.append(
            {
                "rollup_id": rollup.rollup_id,
                "rollup_date": rollup_date.isoformat(),
                "provider_id": provider_id,
                "model_id": model_id,
                "workflow_scope": workflow_scope,
                "request_count": rollup.request_count,
                "estimated_cost_total": str(rollup.estimated_cost_total),
                "provider_reported_cost_total": str(rollup.provider_reported_cost_total) if rollup.provider_reported_cost_total is not None else None,
                "retry_count": rollup.retry_count,
                "fallback_count": rollup.fallback_count,
            }
        )
    _audit("cost_rollup_rebuilt", "costs", "cost_rollups", actor, "Cost rollups rebuilt.", {"count": len(out)})
    db.session.commit()
    return out


def list_rollups(limit: int = 100) -> list[dict]:
    rows = CostRollup.query.order_by(CostRollup.rollup_date.desc()).limit(limit).all()
    return [
        {
            "rollup_id": row.rollup_id,
            "rollup_date": row.rollup_date.isoformat(),
            "provider_id": row.provider_id,
            "model_id": row.model_id,
            "workflow_scope": row.workflow_scope,
            "request_count": row.request_count,
            "estimated_cost_total": str(row.estimated_cost_total),
            "provider_reported_cost_total": str(row.provider_reported_cost_total) if row.provider_reported_cost_total is not None else None,
            "retry_count": row.retry_count,
            "fallback_count": row.fallback_count,
        }
        for row in rows
    ]


def list_audit_events(limit: int = 200) -> list[dict]:
    rows = SettingAuditEvent.query.order_by(SettingAuditEvent.changed_at.desc()).limit(limit).all()
    return [row.to_dict() for row in rows]


def enforce_budget_guard(provider_id: str | None, workflow_scope: str | None) -> None:
    """Raise if hard-stop budget has been exceeded."""
    today = datetime.now(timezone.utc).date()
    day_rollups = CostRollup.query.filter(CostRollup.rollup_date == today).all()
    totals = Decimal("0")
    for roll in day_rollups:
        if provider_id and roll.provider_id not in {provider_id, None}:
            continue
        if workflow_scope and roll.workflow_scope not in {workflow_scope, None}:
            continue
        totals += roll.provider_reported_cost_total or roll.estimated_cost_total
    budgets = CostBudgetPolicy.query.filter_by(hard_stop_enabled=True).all()
    for budget in budgets:
        if budget.scope_kind == "provider" and budget.scope_ref and provider_id != budget.scope_ref:
            continue
        if budget.scope_kind == "workflow" and budget.scope_ref and workflow_scope != budget.scope_ref:
            continue
        if budget.daily_limit is not None and totals > budget.daily_limit:
            raise governance_error(
                "budget_limit_exceeded",
                "Hard-stop budget policy blocks this runtime action.",
                409,
                {"scope_kind": budget.scope_kind, "scope_ref": budget.scope_ref, "daily_limit": str(budget.daily_limit), "current_total": str(totals)},
            )


def record_operational_activity(actor_user, action: str, message: str, metadata: dict | None = None) -> None:
    """Mirror key governance events to shared activity log."""
    log_activity(
        actor=actor_user,
        category="governance",
        action=action,
        status="success",
        message=message,
        route="governance",
        method="SYSTEM",
        metadata=metadata or {},
        target_type="operational_settings",
        target_id="runtime",
    )
