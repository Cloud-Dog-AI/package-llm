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

# cloud_dog_llm — Governance policies
"""Allow/deny and bounds checks for model/tool usage."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class GovernancePolicy:
    """Represent governance policy."""
    allowed_providers: set[str] = field(default_factory=set)
    denied_providers: set[str] = field(default_factory=set)
    allowed_tools: set[str] = field(default_factory=set)
    denied_tools: set[str] = field(default_factory=set)
    max_prompt_chars: int = 32768
    max_output_tokens: int = 4096

    def provider_allowed(self, provider_id: str) -> bool:
        """Handle provider allowed."""
        if provider_id in self.denied_providers:
            return False
        if self.allowed_providers and provider_id not in self.allowed_providers:
            return False
        return True

    def tool_allowed(self, tool_id: str) -> bool:
        """Handle tool allowed."""
        if tool_id in self.denied_tools:
            return False
        if self.allowed_tools and tool_id not in self.allowed_tools:
            return False
        return True

    def validate_prompt(self, prompt: str) -> bool:
        """Validate prompt."""
        return len(prompt) <= self.max_prompt_chars
