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

# cloud_dog_llm — OpenRouter provider adapter
"""OpenRouter adapter built on OpenAI-compatible interface."""

from __future__ import annotations

from cloud_dog_llm.config.models import ProviderConfig
from cloud_dog_llm.providers.openai_compat import OpenAICompatAdapter


class OpenRouterAdapter(OpenAICompatAdapter):
    """Represent open router adapter."""
    def __init__(self, config: ProviderConfig) -> None:
        extra = dict(config.extra_headers or {})
        extra.setdefault("HTTP-Referer", "https://example.com")
        extra.setdefault("X-Title", "Public LLM Client")
        super().__init__(
            ProviderConfig(
                provider_id=config.provider_id,
                base_url=config.base_url,
                model=config.model,
                api_key=config.api_key,
                timeout_seconds=config.timeout_seconds,
                extra_headers=extra,
            )
        )
