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

# cloud_dog_llm — Role-based access control helpers
"""Simple RBAC checks for tools and providers."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class RBACPolicy:
    """Maps roles to allowed tools/providers."""

    role_tools: dict[str, set[str]] = field(default_factory=dict)
    role_providers: dict[str, set[str]] = field(default_factory=dict)

    def can_use_tool(self, role: str, tool_id: str) -> bool:
        """Handle can use tool."""
        allowed = self.role_tools.get(role, set())
        return not allowed or tool_id in allowed

    def can_use_provider(self, role: str, provider_id: str) -> bool:
        """Handle can use provider."""
        allowed = self.role_providers.get(role, set())
        return not allowed or provider_id in allowed


__all__ = ["RBACPolicy"]
