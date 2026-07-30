"""Adapter construction for governed story-runtime providers."""
from __future__ import annotations

import os
from typing import Any

import httpx

from story_runtime_core.adapters import (
    BaseModelAdapter,
    MockModelAdapter,
    OllamaAdapter,
    OpenAIChatAdapter,
)
from story_runtime_core.model_call_accounting import wrap_adapters_with_counting


def _fetch_provider_api_key(
    *,
    row: dict[str, Any],
    provider_id: str,
    backend_url: str,
    token: str,
) -> str | None:
    if not row.get("credential_configured", False) or not token:
        return None
    credential_endpoint = row.get("credential_endpoint")
    if not credential_endpoint:
        return None
    endpoint_url = f"{backend_url}{credential_endpoint}"
    print(f"DEBUG: Fetching credential from {endpoint_url} for {provider_id}", flush=True)
    try:
        with httpx.Client(timeout=5.0) as client:
            response = client.get(endpoint_url, headers={"X-Internal-Config-Token": token})
            if response.status_code != 200:
                print(f"DEBUG: Failed to fetch credential for {provider_id}: HTTP {response.status_code}", flush=True)
                return None
            data = response.json()
            if isinstance(data, dict) and data.get("ok"):
                cred_data = data.get("data", {})
                api_key = cred_data.get("api_key")
                print(f"DEBUG: Credential fetch ok for {provider_id}: present={bool(api_key)}", flush=True)
                return api_key
            print(f"DEBUG: Invalid response from credential endpoint for {provider_id}: {response.status_code}", flush=True)
    except Exception as exc:
        print(f"DEBUG: Exception fetching credential for {provider_id}: {type(exc).__name__}", flush=True)
    return None


def build_governed_model_adapters(config: dict[str, Any]) -> dict[str, BaseModelAdapter]:
    adapters: dict[str, BaseModelAdapter] = {"mock": MockModelAdapter()}
    providers = config.get("providers") if isinstance(config.get("providers"), list) else []
    backend_url = os.getenv("BACKEND_RUNTIME_CONFIG_URL", "http://backend:8000").rstrip("/")
    token = os.getenv("INTERNAL_RUNTIME_CONFIG_TOKEN", "").strip()

    for row in providers:
        if not isinstance(row, dict):
            continue
        provider_id = str(row.get("provider_id") or "").strip()
        provider_type = str(row.get("provider_type") or "").strip().lower()
        base_url = str(row.get("base_url") or "").strip() or None
        api_key = _fetch_provider_api_key(
            row=row,
            provider_id=provider_id,
            backend_url=backend_url,
            token=token,
        )
        print(f"DEBUG: Building adapter for {provider_id} ({provider_type}): api_key_present={bool(api_key)}", flush=True)
        if provider_type in {"openai", "openrouter"}:
            adapters[provider_id] = OpenAIChatAdapter(base_url=base_url, api_key=api_key)
        elif provider_type == "ollama":
            adapters[provider_id] = OllamaAdapter(base_url=base_url)
        elif provider_type == "mock":
            adapters[provider_id] = MockModelAdapter()

    # Wave 0: ledger every productive generate at the adapter seam (D27).
    return wrap_adapters_with_counting(adapters)


__all__ = ["build_governed_model_adapters"]
