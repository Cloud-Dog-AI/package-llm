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

# cloud_dog_llm — Tool router
"""Policy-light unified tool router for local handlers."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from cloud_dog_llm.security.policies import GovernancePolicy
from cloud_dog_llm.tools.models import ToolCall, ToolDef, ToolResult

ToolHandler = Callable[[dict[str, Any]], Awaitable[dict[str, Any]]]


class ToolRouter:
    """Represent tool router."""
    def __init__(self, policy: GovernancePolicy | None = None) -> None:
        self._defs: dict[str, ToolDef] = {}
        self._handlers: dict[str, ToolHandler] = {}
        self._policy = policy or GovernancePolicy()

    def register(self, tool_def: ToolDef, handler: ToolHandler) -> None:
        """Handle register."""
        self._defs[tool_def.tool_id] = tool_def
        self._handlers[tool_def.tool_id] = handler

    async def route(self, call: ToolCall) -> ToolResult:
        """Handle route."""
        if not self._policy.tool_allowed(call.tool_id):
            return ToolResult(tool_id=call.tool_id, success=False, output={}, error="Tool blocked by policy")
        if call.tool_id not in self._handlers:
            return ToolResult(tool_id=call.tool_id, success=False, output={}, error="Tool not registered")
        try:
            out = await self._handlers[call.tool_id](call.arguments)
            return ToolResult(tool_id=call.tool_id, success=True, output=out)
        except Exception as exc:  # noqa: BLE001
            return ToolResult(tool_id=call.tool_id, success=False, output={}, error=str(exc))

    def available_tools(self) -> list[ToolDef]:
        """Handle available tools."""
        return list(self._defs.values())
