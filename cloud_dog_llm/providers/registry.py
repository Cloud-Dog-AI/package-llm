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

# cloud_dog_llm — Provider registry
"""Provider adapter registry and lookup."""

from __future__ import annotations

from cloud_dog_llm.providers.base import ProviderAdapter


class ProviderRegistry:
    """Represent provider registry."""
    def __init__(self) -> None:
        self._providers: dict[str, ProviderAdapter] = {}

    def register(self, provider_id: str, adapter: ProviderAdapter) -> None:
        """Handle register."""
        self._providers[provider_id] = adapter

    def get(self, provider_id: str) -> ProviderAdapter:
        """Handle get."""
        if provider_id not in self._providers:
            raise KeyError(f"Provider not registered: {provider_id}")
        return self._providers[provider_id]

    def has(self, provider_id: str) -> bool:
        """Handle has."""
        return provider_id in self._providers

    def list_ids(self) -> list[str]:
        """List ids."""
        return sorted(self._providers.keys())
