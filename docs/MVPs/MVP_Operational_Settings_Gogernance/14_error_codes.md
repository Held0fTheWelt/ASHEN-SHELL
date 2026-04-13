# 14 Error Codes

This catalog standardizes domain-specific error codes used by the operational settings and AI runtime governance APIs.

All errors must use the standard envelope:

```json
{
  "ok": false,
  "error": {
    "code": "domain_specific_code",
    "message": "Actionable domain-specific message",
    "details": { ... }
  }
}
```

## Bootstrap errors

- `bootstrap_already_initialized`
  - HTTP: `409 Conflict`
  - Meaning: bootstrap initialize was requested after the system was already locked.

- `bootstrap_secret_storage_invalid`
  - HTTP: `400 Bad Request`
  - Meaning: the selected secret storage mode is unsupported or incomplete.

- `bootstrap_missing_admin_identity`
  - HTTP: `400 Bad Request`
  - Meaning: required initial admin identity fields were missing.

- `bootstrap_secret_write_failed`
  - HTTP: `500 Internal Server Error`
  - Meaning: trust-anchor or initial credential write failed.

- `preset_not_found`
  - HTTP: `404 Not Found`
  - Meaning: the requested preset does not exist.

- `bootstrap_recovery_token_invalid`
  - HTTP: `403 Forbidden`
  - Meaning: reopen bootstrap was requested with an invalid recovery token.

## Provider and credential errors

- `provider_not_found`
  - HTTP: `404 Not Found`

- `provider_credential_required`
  - HTTP: `400 Bad Request`
  - Meaning: a provider action requiring an active credential was requested without one.

- `provider_secret_rejected`
  - HTTP: `400 Bad Request`
  - Meaning: the submitted secret format is invalid for the selected provider.

- `credential_encryption_failed`
  - HTTP: `500 Internal Server Error`
  - Meaning: the backend could not encrypt the submitted secret.

- `credential_rotation_in_progress`
  - HTTP: `409 Conflict`
  - Meaning: the same provider credential is already undergoing rotation.

- `provider_test_failed`
  - HTTP: `502 Bad Gateway`
  - Meaning: health test to provider failed or provider rejected credentials.

## Model and route errors

- `model_not_found`
  - HTTP: `404 Not Found`

- `route_not_found`
  - HTTP: `404 Not Found`

- `route_invalid_model_reference`
  - HTTP: `409 Conflict`
  - Meaning: route references a missing or disabled model.

- `route_requires_mock_model_for_hybrid_mode`
  - HTTP: `409 Conflict`
  - Meaning: hybrid mode requires a safe mock fallback route.

- `model_provider_mismatch`
  - HTTP: `409 Conflict`
  - Meaning: the model configuration does not belong to the referenced provider.

## Runtime mode and resolution errors

- `generation_mode_invalid`
  - HTTP: `400 Bad Request`

- `retrieval_mode_invalid`
  - HTTP: `400 Bad Request`

- `validation_mode_invalid`
  - HTTP: `400 Bad Request`

- `runtime_profile_invalid`
  - HTTP: `400 Bad Request`

- `resolved_config_generation_failed`
  - HTTP: `500 Internal Server Error`
  - Meaning: the backend could not generate a coherent resolved runtime config.

- `runtime_reload_failed`
  - HTTP: `502 Bad Gateway`
  - Meaning: internal service reload of runtime config failed or was refused.

## Cost and budget errors

- `budget_not_found`
  - HTTP: `404 Not Found`

- `budget_invalid_threshold`
  - HTTP: `400 Bad Request`
  - Meaning: threshold percentages or money values are invalid.

- `budget_limit_exceeded`
  - HTTP: `409 Conflict`
  - Meaning: a hard-stop budget policy blocks the attempted runtime action.

- `usage_rollup_unavailable`
  - HTTP: `503 Service Unavailable`
  - Meaning: rollup generation is unavailable or delayed.

## Settings errors

- `setting_scope_invalid`
  - HTTP: `400 Bad Request`

- `setting_value_invalid`
  - HTTP: `400 Bad Request`

- `setting_update_forbidden`
  - HTTP: `403 Forbidden`
  - Meaning: the caller lacks rights or the setting is trust-root controlled.

## Internal guidance

- Prefer domain-specific errors over generic transport errors.
- Do not collapse distinct failures into a single `configuration_error` bucket.
- Include remediation hints in `details` when useful, for example available presets, accepted provider types, or missing dependencies.
