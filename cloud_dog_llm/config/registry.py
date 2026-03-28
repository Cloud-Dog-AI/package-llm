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

# cloud_dog_llm — Provider config registry
"""Registry of provider configuration objects keyed by provider_id."""

from __future__ import annotations

from typing import Any

from cloud_dog_llm.config.models import ProviderConfig, provider_config_from_dict


class ProviderConfigRegistry:
    """Represent provider config registry."""
    def __init__(self) -> None:
        self._items: dict[str, ProviderConfig] = {}

    def register(self, provider_id: str, config: ProviderConfig) -> None:
        """Handle register."""
        self._items[provider_id] = config

    def get(self, provider_id: str) -> ProviderConfig:
        """Handle get."""
        if provider_id not in self._items:
            raise KeyError(provider_id)
        return self._items[provider_id]

    def list_ids(self) -> list[str]:
        """List ids."""
        return sorted(self._items.keys())

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> "ProviderConfigRegistry":
        """Handle from dict."""
        reg = cls()
        providers_raw = raw.get("providers", {}) if isinstance(raw, dict) else {}
        if isinstance(providers_raw, dict):
            for provider_id, provider_raw in providers_raw.items():
                if not isinstance(provider_raw, dict):
                    continue
                if not bool(provider_raw.get("enabled", True)):
                    continue
                reg.register(str(provider_id), provider_config_from_dict(str(provider_id), provider_raw))
        return reg
