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

# cloud_dog_llm — Settings model
"""High-level runtime settings resolved from config dictionaries."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class LLMSettings:
    """Represent l l m settings."""
    default_provider: str = "ollama"
    connect_timeout_seconds: float = 30.0
    read_timeout_seconds: float = 300.0
    overall_timeout_seconds: float = 480.0


def settings_from_dict(raw: dict[str, Any]) -> LLMSettings:
    """Handle settings from dict."""
    llm = raw.get("llm", {}) if isinstance(raw, dict) else {}
    return LLMSettings(
        default_provider=str(llm.get("default_provider", "ollama")),
        connect_timeout_seconds=float(llm.get("connect_timeout_seconds", 30.0) or 30.0),
        read_timeout_seconds=float(llm.get("read_timeout_seconds", 300.0) or 300.0),
        overall_timeout_seconds=float(llm.get("overall_timeout_seconds", 480.0) or 480.0),
    )
