# 03 Data Contracts

## Enum catalog

### BootstrapState
- `uninitialized`
- `initializing`
- `initialized`
- `bootstrap_locked`
- `bootstrap_recovery_required`

### SecretStorageMode
- `same_db_encrypted`
- `separate_secret_db_encrypted`
- `external_secret_manager`

### GenerationExecutionMode
- `mock_only`
- `ai_only`
- `routed_llm_slm`
- `hybrid_routed_with_mock_fallback`

### RetrievalExecutionMode
- `disabled`
- `sparse_only`
- `hybrid_dense_sparse`

### ValidationExecutionMode
- `schema_only`
- `schema_plus_semantic`
- `strict_rule_engine`

### ProviderSelectionMode
- `local_only`
- `remote_allowed`
- `remote_preferred`
- `restricted_by_route`

### AIProviderType
- `openai`
- `ollama`
- `anthropic`
- `custom_http`
- `mock`

### AIModelRole
- `llm`
- `slm`
- `mock`

### CostMethod
- `provider_reported`
- `price_table_estimated`
- `flat_per_request`
- `none`

### RuntimeProfile
- `safe_local`
- `balanced`
- `cost_aware`
- `quality_first`
- `custom`

### HealthStatus
- `unknown`
- `healthy`
- `degraded`
- `failing`
- `disabled`

### SettingScope
- `bootstrap`
- `backend`
- `world_engine`
- `ai_runtime`
- `retrieval`
- `notifications`
- `costs`

## Core contracts

### BootstrapTrustAnchorConfig
- `bootstrap_state: BootstrapState`
- `secret_storage_mode: SecretStorageMode`
- `runtime_profile: RuntimeProfile`
- `generation_execution_mode: GenerationExecutionMode`
- `retrieval_execution_mode: RetrievalExecutionMode`
- `validation_execution_mode: ValidationExecutionMode`
- `provider_selection_mode: ProviderSelectionMode`
- `bootstrap_completed_at: datetime | null`
- `bootstrap_completed_by: str | null`
- `reopen_requires_elevated_auth: bool`

### BootstrapPreset
- `preset_id: str`
- `display_name: str`
- `description: str`
- `generation_execution_mode: GenerationExecutionMode`
- `retrieval_execution_mode: RetrievalExecutionMode`
- `validation_execution_mode: ValidationExecutionMode`
- `provider_selection_mode: ProviderSelectionMode`
- `default_runtime_profile: RuntimeProfile`
- `default_provider_templates: list[BootstrapProviderTemplate]`
- `default_budget_policy: BootstrapBudgetTemplate`

### BootstrapProviderTemplate
- `provider_type: AIProviderType`
- `display_name: str`
- `enabled_by_default: bool`
- `suggested_role: AIModelRole | null`
- `base_url: str | null`
- `requires_secret: bool`

### AIProviderConfig
- `provider_id: str`
- `provider_type: AIProviderType`
- `display_name: str`
- `base_url: str | null`
- `is_enabled: bool`
- `is_local: bool`
- `supports_structured_output: bool`
- `health_status: HealthStatus`
- `credential_configured: bool`
- `last_tested_at: datetime | null`

### AIProviderCredential
- `credential_id: str`
- `provider_id: str`
- `secret_name: str`
- `encrypted_secret: bytes`
- `encrypted_dek: bytes`
- `dek_algorithm: str`
- `secret_fingerprint: str`
- `created_at: datetime`
- `updated_at: datetime`
- `rotated_at: datetime | null`
- `is_active: bool`

### AIModelConfig
- `model_id: str`
- `provider_id: str`
- `model_name: str`
- `display_name: str`
- `model_role: AIModelRole`
- `is_enabled: bool`
- `structured_output_capable: bool`
- `timeout_seconds: int`
- `max_context_tokens: int | null`
- `cost_method: CostMethod`
- `input_price_per_1k: Decimal | null`
- `output_price_per_1k: Decimal | null`
- `flat_request_price: Decimal | null`

### AITaskRoute
- `route_id: str`
- `task_kind: str`
- `workflow_scope: str`
- `preferred_model_id: str | null`
- `fallback_model_id: str | null`
- `mock_model_id: str | null`
- `is_enabled: bool`
- `use_mock_when_provider_unavailable: bool`

### SystemSettingRecord
- `setting_id: str`
- `scope: SettingScope`
- `setting_key: str`
- `setting_value_json: dict`
- `is_secret_backed: bool`
- `is_user_visible: bool`
- `updated_at: datetime`
- `updated_by: str | null`

### ResolvedRuntimeConfig
- `generated_at: datetime`
- `generation_execution_mode: GenerationExecutionMode`
- `retrieval_execution_mode: RetrievalExecutionMode`
- `validation_execution_mode: ValidationExecutionMode`
- `runtime_profile: RuntimeProfile`
- `provider_selection_mode: ProviderSelectionMode`
- `providers: list[ResolvedProviderConfig]`
- `models: list[ResolvedModelConfig]`
- `routes: list[ResolvedRouteConfig]`
- `backend_settings: dict`
- `world_engine_settings: dict`
- `retrieval_settings: dict`
- `cost_settings: dict`
- `notification_settings: dict`

### ResolvedProviderConfig
- `provider_id: str`
- `provider_type: AIProviderType`
- `base_url: str | null`
- `resolved_secret_ref: str | null`
- `is_enabled: bool`

### ResolvedModelConfig
- `model_id: str`
- `provider_id: str`
- `model_name: str`
- `model_role: AIModelRole`
- `timeout_seconds: int`
- `structured_output_capable: bool`

### ResolvedRouteConfig
- `route_id: str`
- `task_kind: str`
- `workflow_scope: str`
- `preferred_model_id: str | null`
- `fallback_model_id: str | null`
- `mock_model_id: str | null`
- `effective_strategy: str`

### AIUsageEvent
- `usage_event_id: str`
- `provider_id: str | null`
- `model_id: str | null`
- `task_kind: str`
- `workflow_scope: str`
- `request_id: str`
- `success: bool`
- `latency_ms: int | null`
- `input_tokens: int | null`
- `output_tokens: int | null`
- `provider_reported_cost: Decimal | null`
- `estimated_cost: Decimal | null`
- `cost_method_used: CostMethod`
- `degraded_mode_used: bool`
- `retry_used: bool`
- `fallback_used: bool`
- `created_at: datetime`

### CostBudgetPolicy
- `budget_policy_id: str`
- `scope_kind: str`
- `scope_ref: str | null`
- `daily_limit: Decimal | null`
- `monthly_limit: Decimal | null`
- `warning_threshold_percent: int`
- `hard_stop_enabled: bool`

### CostRollup
- `rollup_id: str`
- `rollup_date: date`
- `provider_id: str | null`
- `model_id: str | null`
- `workflow_scope: str | null`
- `request_count: int`
- `estimated_cost_total: Decimal`
- `provider_reported_cost_total: Decimal | null`
- `retry_count: int`
- `fallback_count: int`

### SettingAuditEvent
- `audit_event_id: str`
- `event_type: str`
- `scope: SettingScope`
- `target_ref: str`
- `changed_by: str`
- `changed_at: datetime`
- `summary: str`

## Sensitive vs non-sensitive data rule

### Sensitive
- provider credentials
- encrypted secrets
- key fingerprints beyond masked display
- trust-anchor recovery material
- external service auth tokens

### Non-sensitive
- enabled flags
- model metadata
- route mappings
- timeouts
- runtime profile names
- mode selection values
- budget thresholds
- health statuses
