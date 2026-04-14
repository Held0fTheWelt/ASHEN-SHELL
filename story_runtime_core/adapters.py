from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any

import httpx


@dataclass(slots=True)
class ModelCallResult:
    content: str
    success: bool
    metadata: dict[str, Any]


class BaseModelAdapter:
    adapter_name: str = "base"

    def generate(
        self,
        prompt: str,
        *,
        timeout_seconds: float = 10.0,
        retrieval_context: str | None = None,
        model_name: str | None = None,
    ) -> ModelCallResult:
        raise NotImplementedError


class MockModelAdapter(BaseModelAdapter):
    adapter_name = "mock"

    def generate(
        self,
        prompt: str,
        *,
        timeout_seconds: float = 10.0,
        retrieval_context: str | None = None,
        model_name: str | None = None,
    ) -> ModelCallResult:
        return ModelCallResult(
            content=f"[mock] {prompt[:160]}",
            success=True,
            metadata={
                "adapter": self.adapter_name,
                "timeout_seconds": timeout_seconds,
                "retrieval_context_attached": bool(retrieval_context),
            },
        )


class OpenAIChatAdapter(BaseModelAdapter):
    adapter_name = "openai"

    def __init__(
        self,
        *,
        model_name: str = "gpt-4o-mini",
        base_url: str | None = None,
        api_key: str | None = None,
    ) -> None:
        self.model_name = model_name
        self.base_url = (base_url or os.getenv("OPENAI_BASE_URL") or "https://api.openai.com/v1").rstrip("/")
        self._configured_api_key = (api_key or "").strip() or None

    def generate(
        self,
        prompt: str,
        *,
        timeout_seconds: float = 20.0,
        retrieval_context: str | None = None,
        model_name: str | None = None,
    ) -> ModelCallResult:
        api_key = (self._configured_api_key or os.getenv("OPENAI_API_KEY") or "").strip()
        chosen_model = (model_name or self.model_name).strip() or self.model_name
        if not api_key:
            return ModelCallResult(
                content="",
                success=False,
                metadata={"error": "missing_openai_api_key", "model": chosen_model},
            )
        try:
            with httpx.Client(timeout=timeout_seconds) as client:
                response = client.post(
                    f"{self.base_url}/chat/completions",
                    headers={"Authorization": f"Bearer {api_key}"},
                    json={
                        "model": chosen_model,
                        "messages": [
                            {
                                "role": "system",
                                "content": retrieval_context or "No retrieval context attached.",
                            },
                            {"role": "user", "content": prompt},
                        ],
                        "temperature": 0.3,
                    },
                )
                response.raise_for_status()
                payload = response.json()
                message = payload["choices"][0]["message"]["content"]
                return ModelCallResult(
                    content=message,
                    success=True,
                    metadata={
                        "adapter": self.adapter_name,
                        "model": chosen_model,
                        "base_url": self.base_url,
                    },
                )
        except Exception as exc:
            return ModelCallResult(
                content="",
                success=False,
                metadata={"adapter": self.adapter_name, "model": chosen_model, "base_url": self.base_url, "error": str(exc)},
            )


class OllamaAdapter(BaseModelAdapter):
    adapter_name = "ollama"

    def __init__(self, *, model_name: str = "llama3.2", base_url: str | None = None) -> None:
        self.model_name = model_name
        self.base_url = (base_url or os.getenv("OLLAMA_BASE_URL") or "http://127.0.0.1:11434").rstrip("/")

    def generate(
        self,
        prompt: str,
        *,
        timeout_seconds: float = 10.0,
        retrieval_context: str | None = None,
        model_name: str | None = None,
    ) -> ModelCallResult:
        chosen_model = (model_name or self.model_name).strip() or self.model_name
        try:
            with httpx.Client(timeout=timeout_seconds) as client:
                response = client.post(
                    f"{self.base_url}/api/generate",
                    json={
                        "model": chosen_model,
                        "prompt": prompt if not retrieval_context else f"{retrieval_context}\n\n{prompt}",
                        "stream": False,
                    },
                )
                response.raise_for_status()
                payload = response.json()
                return ModelCallResult(
                    content=payload.get("response", ""),
                    success=True,
                    metadata={"adapter": self.adapter_name, "model": chosen_model},
                )
        except Exception as exc:
            return ModelCallResult(
                content="",
                success=False,
                metadata={"adapter": self.adapter_name, "model": chosen_model, "error": str(exc)},
            )


def build_default_model_adapters() -> dict[str, BaseModelAdapter]:
    """Concrete adapter instances keyed by provider name (startup registration surface).

    Used by the World-Engine story runtime host alongside :class:`ModelRegistry` specs.
    """
    return {
        "mock": MockModelAdapter(),
        "openai": OpenAIChatAdapter(),
        "ollama": OllamaAdapter(),
    }
