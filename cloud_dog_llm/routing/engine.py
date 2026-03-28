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

# cloud_dog_llm — Routing engine
"""Execution router that delegates to tool router / MCP / A2A clients."""

from __future__ import annotations

from typing import Any

from cloud_dog_llm.routing.policies import RoutingPolicy
from cloud_dog_llm.tools.models import ToolCall, ToolResult
from cloud_dog_llm.tools.router import ToolRouter


class RoutingEngine:
    """Represent routing engine."""
    def __init__(
        self,
        tool_router: ToolRouter,
        *,
        policy: RoutingPolicy | None = None,
        mcp_client: Any | None = None,
        a2a_client: Any | None = None,
    ) -> None:
        self._router = tool_router
        self._policy = policy or RoutingPolicy()
        self._mcp = mcp_client
        self._a2a = a2a_client

    async def route_tool_call(self, call: ToolCall) -> ToolResult:
        """Handle route tool call."""
        target = self._policy.target_for_tool(call.tool_id)
        if target == "mcp" and self._mcp is not None:
            result = await self._mcp.tools_call(call.name, call.arguments)
            return ToolResult(tool_id=call.tool_id, success=True, output=result)
        if target == "a2a" and self._a2a is not None:
            result = await self._a2a.call({"tool": call.name, "arguments": call.arguments})
            return ToolResult(tool_id=call.tool_id, success=True, output=result)
        return await self._router.route(call)
