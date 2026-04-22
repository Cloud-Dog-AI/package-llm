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

# cloud_dog_llm — Provider factory
"""Factory helpers for concrete provider adapter creation."""

from __future__ import annotations

from cloud_dog_llm.config.models import ProviderConfig
from cloud_dog_llm.providers.anthropic import AnthropicAdapter
from cloud_dog_llm.providers.base import ProviderAdapter
from cloud_dog_llm.providers.ollama import OllamaAdapter
from cloud_dog_llm.providers.openai import OpenAIAdapter
from cloud_dog_llm.providers.openai_compat import OpenAICompatAdapter
from cloud_dog_llm.providers.openrouter import OpenRouterAdapter
from cloud_dog_llm.providers.registry import ProviderRegistry


def create_provider(config: ProviderConfig) -> ProviderAdapter:
    """Create provider."""
    provider = config.provider_id.lower()
    if provider == "ollama":
        return OllamaAdapter(config)
    if provider == "openrouter":
        return OpenRouterAdapter(config)
    if provider == "anthropic":
        return AnthropicAdapter(config)
    if provider == "openai":
        return OpenAIAdapter(config)
    return OpenAICompatAdapter(config)


def build_provider_registry(configs: list[ProviderConfig]) -> ProviderRegistry:
    """Build provider registry."""
    registry = ProviderRegistry()
    for cfg in configs:
        registry.register(cfg.provider_id, create_provider(cfg))
    return registry
