# Copyright 2026 Cloud-Dog, Viewdeck Engineering Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# cloud_dog_llm — Client factory
"""Factory helpers for building an LLMClient from config dictionaries."""

from __future__ import annotations

from typing import Any

from cloud_dog_llm.config.models import ProviderConfig, provider_config_from_dict
from cloud_dog_llm.providers.anthropic import AnthropicAdapter
from cloud_dog_llm.providers.ollama import OllamaAdapter
from cloud_dog_llm.providers.openai import OpenAIAdapter
from cloud_dog_llm.providers.openai_compat import OpenAICompatAdapter
from cloud_dog_llm.providers.openrouter import OpenRouterAdapter
from cloud_dog_llm.providers.registry import ProviderRegistry
from cloud_dog_llm.runtime.client import LLMClient


def _provider_from_config(cfg: ProviderConfig):
    pid = cfg.provider_id.lower()
    if pid == "ollama":
        return OllamaAdapter(cfg)
    if pid == "openrouter":
        return OpenRouterAdapter(cfg)
    if pid == "anthropic":
        return AnthropicAdapter(cfg)
    if pid == "openai":
        return OpenAIAdapter(cfg)
    if pid in {"openai_compat", "vllm"}:
        return OpenAICompatAdapter(cfg)
    return OpenAICompatAdapter(cfg)


def get_llm_client(config: dict[str, Any]) -> LLMClient:
    """Return llm client."""
    providers = ProviderRegistry()

    default_provider_id = str(config.get("llm", {}).get("default_provider", "ollama"))
    providers_raw = config.get("providers", {})
    if isinstance(providers_raw, dict) and providers_raw:
        for pid, raw in providers_raw.items():
            if not isinstance(raw, dict):
                continue
            enabled = bool(raw.get("enabled", True))
            if not enabled:
                continue
            pconf = provider_config_from_dict(str(pid), raw)
            providers.register(str(pid), _provider_from_config(pconf))

    if not providers.list_ids() and "model_entry" in config:
        entry = config["model_entry"]
        if isinstance(entry, dict):
            provider_hint = str(entry.get("provider", "openai"))
            if provider_hint == "ollama":
                pid = "ollama"
            elif "openrouter" in str(entry.get("base_url", "")):
                pid = "openrouter"
            else:
                pid = "openai"
            pconf = ProviderConfig(
                provider_id=pid,
                base_url=str(entry.get("base_url", "")),
                model=str(entry.get("model", "")),
                api_key=str(entry.get("api_key", "")),
                timeout_seconds=float((entry.get("params", {}) or {}).get("timeout_seconds", 300) or 300),
            )
            providers.register(pid, _provider_from_config(pconf))
            default_provider_id = pid

    if not providers.has(default_provider_id):
        ids = providers.list_ids()
        if not ids:
            raise ValueError("No enabled providers configured")
        default_provider_id = ids[0]

    return LLMClient(provider_registry=providers, default_provider_id=default_provider_id)
