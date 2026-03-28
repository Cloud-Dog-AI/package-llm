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

# cloud_dog_llm — Config models
"""Runtime config helpers for provider and timeout settings."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class ProviderConfig:
    """Represent provider config."""
    provider_id: str
    base_url: str
    model: str
    api_key: str = ""
    timeout_seconds: float = 300.0
    extra_headers: dict[str, str] | None = None


def provider_config_from_dict(provider_id: str, raw: dict[str, Any]) -> ProviderConfig:
    """Handle provider config from dict."""
    return ProviderConfig(
        provider_id=provider_id,
        base_url=str(raw.get("base_url", "")),
        model=str(raw.get("model", "")),
        api_key=str(raw.get("api_key", "")),
        timeout_seconds=float(raw.get("timeout_seconds", 300.0) or 300.0),
        extra_headers=dict(raw.get("extra_headers", {})) if isinstance(raw.get("extra_headers"), dict) else None,
    )
