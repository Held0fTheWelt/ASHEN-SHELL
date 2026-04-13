# 04 API Catalog

All admin mutation APIs are backend-only and admin-authenticated.

## Standard envelopes

### Success

```json
{
  "ok": true,
  "data": {
    "...": "..."
  }
}
```

### Error

```json
{
  "ok": false,
  "error": {
    "code": "domain_specific_code",
    "message": "Actionable domain-specific message",
    "details": {
      "...": "..."
    }
  }
}
```

---

## Bootstrap

### GET `/api/v1/admin/bootstrap/status`
Returns whether bootstrap is required and which parts are configured.

**Example success response**
```json
{
  "ok": true,
  "data": {
    "bootstrap_required": true,
    "bootstrap_locked": false,
    "available_presets": ["safe_local", "balanced", "cost_aware", "quality_first"],
    "configured": {
      "trust_anchor": false,
      "initial_admin": false,
      "secret_storage": false,
      "initial_provider": false
    }
  }
}
```

### GET `/api/v1/admin/bootstrap/presets`
Returns bootstrap presets.

**Example success response**
```json
{
  "ok": true,
  "data": {
    "presets": [
      {
        "preset_id": "balanced",
        "display_name": "Balanced",
        "generation_execution_mode": "hybrid_routed_with_mock_fallback",
        "retrieval_execution_mode": "hybrid_dense_sparse",
        "validation_execution_mode": "schema_plus_semantic",
        "provider_templates": [
          {"provider_type": "mock", "enabled_by_default": true},
          {"provider_type": "ollama", "enabled_by_default": true},
          {"provider_type": "openai", "enabled_by_default": false}
        ]
      }
    ]
  }
}
```

### POST `/api/v1/admin/bootstrap/initialize`
Initializes the trust-anchor/bootstrap configuration.

**Request fields**
- selected preset
- initial admin data
- storage mode
- generation/retrieval/validation mode choices
- first provider configuration
- first secret submissions

**Example request**
```json
{
  "selected_preset": "balanced",
  "admin_email": "operator@example.com",
  "admin_display_name": "Primary Operator",
  "secret_storage_mode": "same_db_encrypted",
  "generation_execution_mode": "hybrid_routed_with_mock_fallback",
  "retrieval_execution_mode": "hybrid_dense_sparse",
  "validation_execution_mode": "schema_plus_semantic",
  "provider_selection_mode": "restricted_by_route",
  "trust_anchor": {
    "kek_source": "deployment_secret",
    "allow_reopen_with_recovery_token": true
  },
  "initial_provider": {
    "provider_type": "openai",
    "display_name": "OpenAI Primary",
    "base_url": "https://api.openai.com/v1"
  },
  "initial_credential": {
    "api_key": "sk-live-example"
  }
}
```

**Example success response**
```json
{
  "ok": true,
  "data": {
    "bootstrap_status": "initialized",
    "bootstrap_locked": true,
    "secret_storage_mode": "same_db_encrypted",
    "trust_anchor_fingerprint": "sha256:3d58c1...",
    "next_actions": [
      "launch_stack",
      "open_administration_tool",
      "configure_models_and_routes"
    ],
    "stack_start_ready": true
  }
}
```

**Example error response**
```json
{
  "ok": false,
  "error": {
    "code": "preset_not_found",
    "message": "Preset 'unknown' does not exist.",
    "details": {
      "available_presets": ["safe_local", "balanced", "cost_aware", "quality_first"]
    }
  }
}
```

### POST `/api/v1/admin/bootstrap/reopen`
Protected endpoint to reopen bootstrap UI in recovery mode.

**Example request**
```json
{
  "recovery_token": "bootstrap-recovery-token",
  "reason": "operator_lost_secret_storage_context"
}
```

**Example success response**
```json
{
  "ok": true,
  "data": {
    "bootstrap_reopen_status": "accepted",
    "recovery_mode": true,
    "allowed_sections": ["secret_storage", "provider_credentials", "runtime_modes"]
  }
}
```

---

## Providers

### GET `/api/v1/admin/ai/providers`
List providers.

**Example success response**
```json
{
  "ok": true,
  "data": {
    "providers": [
      {
        "provider_id": "openai_primary",
        "provider_type": "openai",
        "display_name": "OpenAI Primary",
        "base_url": "https://api.openai.com/v1",
        "is_enabled": true,
        "credential_configured": true,
        "credential_fingerprint": "sha256:81fe...",
        "health_status": "healthy"
      }
    ]
  }
}
```

### POST `/api/v1/admin/ai/providers`
Create provider config.

**Example request**
```json
{
  "provider_type": "ollama",
  "display_name": "Local Ollama",
  "base_url": "http://ollama:11434",
  "is_enabled": true,
  "allow_live_runtime": true,
  "allow_preview_runtime": true,
  "allow_writers_room": true,
  "allow_research_suite": true
}
```

**Example success response**
```json
{
  "ok": true,
  "data": {
    "provider_id": "ollama_local",
    "created": true
  }
}
```

### PATCH `/api/v1/admin/ai/providers/<provider_id>`
Update provider metadata.

**Example request**
```json
{
  "is_enabled": false,
  "allow_live_runtime": false,
  "display_name": "OpenAI Primary (paused)"
}
```

### POST `/api/v1/admin/ai/providers/<provider_id>/credential`
Write or replace provider credential. Write-only.

**Example request**
```json
{
  "api_key": "sk-live-example",
  "label": "primary-key-2026-04"
}
```

**Example success response**
```json
{
  "ok": true,
  "data": {
    "provider_id": "openai_primary",
    "credential_written": true,
    "credential_fingerprint": "sha256:bb81...",
    "rotated_at": "2026-04-13T14:18:00Z"
  }
}
```

**Example error response**
```json
{
  "ok": false,
  "error": {
    "code": "credential_encryption_failed",
    "message": "The credential could not be encrypted using the configured secret storage backend.",
    "details": {
      "provider_id": "openai_primary",
      "secret_storage_mode": "same_db_encrypted"
    }
  }
}
```

### POST `/api/v1/admin/ai/providers/<provider_id>/rotate-credential`
Rotate provider credential.

**Example request**
```json
{
  "new_api_key": "sk-rotated-example",
  "retire_previous_after_seconds": 300
}
```

### POST `/api/v1/admin/ai/providers/<provider_id>/test-connection`
Test provider health using current credential/config.

**Example success response**
```json
{
  "ok": true,
  "data": {
    "provider_id": "openai_primary",
    "health_status": "healthy",
    "latency_ms": 842,
    "tested_at": "2026-04-13T14:19:12Z"
  }
}
```

---

## Models

### GET `/api/v1/admin/ai/models`
List models.

### POST `/api/v1/admin/ai/models`
Create model config.

**Example request**
```json
{
  "provider_id": "openai_primary",
  "model_name": "gpt-4o-mini",
  "model_role": "llm",
  "supports_structured_output": true,
  "timeout_seconds": 30,
  "cost_method": "provider_reported",
  "is_enabled": true
}
```

### PATCH `/api/v1/admin/ai/models/<model_id>`
Update model config.

---

## Routes

### GET `/api/v1/admin/ai/routes`
List task routes.

### POST `/api/v1/admin/ai/routes`
Create task route.

**Example request**
```json
{
  "task_kind": "narrative_generation",
  "workflow_scope": "global",
  "preferred_model_id": "openai_gpt_4o_mini",
  "fallback_model_id": "mock_deterministic",
  "is_enabled": true
}
```

### PATCH `/api/v1/admin/ai/routes/<route_id>`
Update task route.

**Example error response**
```json
{
  "ok": false,
  "error": {
    "code": "route_requires_mock_model_for_hybrid_mode",
    "message": "Hybrid mode requires at least one route with a mock-capable fallback model.",
    "details": {
      "route_id": "narrative_generation_global"
    }
  }
}
```

---

## Modes and runtime profile

### GET `/api/v1/admin/runtime/modes`
Get current execution modes and profile.

### PATCH `/api/v1/admin/runtime/modes`
Update:
- generation execution mode
- retrieval execution mode
- validation execution mode
- provider selection mode
- runtime profile

**Example request**
```json
{
  "generation_execution_mode": "routed_llm_slm",
  "retrieval_execution_mode": "hybrid_dense_sparse",
  "validation_execution_mode": "schema_plus_semantic",
  "provider_selection_mode": "restricted_by_route",
  "runtime_profile": "balanced"
}
```

**Example success response**
```json
{
  "ok": true,
  "data": {
    "updated": true,
    "runtime_profile": "balanced",
    "effective_generation_execution_mode": "routed_llm_slm"
  }
}
```

### GET `/api/v1/admin/runtime/resolved-config`
Return current resolved runtime config. Must mask or omit secrets.

**Example success response**
```json
{
  "ok": true,
  "data": {
    "generated_at": "2026-04-13T14:22:00Z",
    "providers": [
      {
        "provider_id": "openai_primary",
        "provider_type": "openai",
        "base_url": "https://api.openai.com/v1",
        "credential_configured": true
      }
    ],
    "modes": {
      "generation_execution_mode": "routed_llm_slm",
      "retrieval_execution_mode": "hybrid_dense_sparse",
      "validation_execution_mode": "schema_plus_semantic"
    },
    "routes": [
      {
        "task_kind": "narrative_generation",
        "preferred_model_id": "openai_gpt_4o_mini",
        "fallback_model_id": "mock_deterministic"
      }
    ]
  }
}
```

### POST `/api/v1/admin/runtime/reload-resolved-config`
Force regeneration of resolved runtime config and notify internal services.

---

## Backend and world-engine settings

### GET `/api/v1/admin/settings/backend`
### PATCH `/api/v1/admin/settings/backend`

**Example request**
```json
{
  "play_service_internal_url": "http://play-service:8000",
  "play_service_public_url": "http://localhost:8001",
  "play_service_request_timeout_seconds": 20,
  "game_ticket_ttl_seconds": 900
}
```

### GET `/api/v1/admin/settings/world-engine`
### PATCH `/api/v1/admin/settings/world-engine`

**Example request**
```json
{
  "preview_isolation_mode": "in_memory_namespace",
  "max_retry_attempts": 1,
  "enable_corrective_feedback": true,
  "fallback_alert_threshold": 5,
  "runtime_diagnostics_verbosity": "operator"
}
```

### GET `/api/v1/admin/settings/retrieval`
### PATCH `/api/v1/admin/settings/retrieval`

### GET `/api/v1/admin/settings/notifications`
### PATCH `/api/v1/admin/settings/notifications`

### GET `/api/v1/admin/settings/costs`
### PATCH `/api/v1/admin/settings/costs`

**Example request**
```json
{
  "daily_global_limit": "50.00",
  "monthly_global_limit": "1000.00",
  "warning_threshold_percent": 80,
  "hard_stop_enabled": false
}
```

---

## Cost and usage

### GET `/api/v1/admin/costs/usage-events`
List usage events.

**Example success response**
```json
{
  "ok": true,
  "data": {
    "items": [
      {
        "usage_event_id": "evt_001",
        "provider_id": "openai_primary",
        "model_id": "openai_gpt_4o_mini",
        "task_kind": "narrative_generation",
        "workflow_scope": "god_of_carnage",
        "input_tokens": 2048,
        "output_tokens": 512,
        "estimated_cost": "0.0580",
        "cost_method_used": "provider_reported",
        "fallback_used": false,
        "retry_used": true
      }
    ]
  }
}
```

### GET `/api/v1/admin/costs/rollups`
List cost rollups.

### GET `/api/v1/admin/costs/budgets`
List budgets.

### POST `/api/v1/admin/costs/budgets`
Create budget.

**Example request**
```json
{
  "scope_kind": "workflow",
  "scope_ref": "god_of_carnage",
  "daily_limit": "10.00",
  "monthly_limit": "150.00",
  "warning_threshold_percent": 80,
  "hard_stop_enabled": false
}
```

### PATCH `/api/v1/admin/costs/budgets/<budget_policy_id>`
Update budget.

---

## Internal runtime config

### GET `/internal/runtime-config`
Internal endpoint for world-engine / ai_stack to fetch resolved config.

**Example success response**
```json
{
  "ok": true,
  "data": {
    "config_version": "cfg_2026_04_13_001",
    "providers": [{"provider_id": "mock_default", "provider_type": "mock", "is_enabled": true}],
    "routes": [{"task_kind": "narrative_generation", "preferred_model_id": "mock_deterministic"}]
  }
}
```

### POST `/internal/runtime-config/reload`
Internal endpoint to signal config refresh.

---

## Required error conditions

The complete catalog lives in `14_error_codes.md`.
The following error families are mandatory:

### Bootstrap
- `bootstrap_already_initialized`
- `bootstrap_secret_storage_invalid`
- `bootstrap_missing_admin_identity`
- `bootstrap_secret_write_failed`
- `preset_not_found`

### Provider / credentials
- `provider_not_found`
- `provider_credential_required`
- `provider_test_failed`
- `provider_secret_rejected`
- `credential_encryption_failed`
- `credential_rotation_in_progress`

### Models / routes
- `model_not_found`
- `route_invalid_model_reference`
- `route_requires_mock_model_for_hybrid_mode`

### Runtime modes
- `generation_mode_invalid`
- `validation_mode_invalid`
- `runtime_profile_invalid`
- `resolved_config_generation_failed`
- `runtime_reload_failed`

### Costs
- `budget_invalid_threshold`
- `usage_rollup_unavailable`
- `budget_limit_exceeded`

## Guard rules

- Only admin roles may call admin mutation endpoints.
- Bootstrap initialize may only run while system is not initialized or in explicit recovery mode.
- Credential endpoints are write-only.
- Resolved config endpoint must not expose raw secrets.
- Switching to AI-only mode must fail if no valid enabled provider/model route set exists.
- Hybrid mode must fail if no safe fallback path exists.
- Secret rotation must reject concurrent rotation jobs for the same provider.
- World-engine/internal config reload failures must be surfaced as explicit errors, not soft success.
