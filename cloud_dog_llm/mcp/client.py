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

# cloud_dog_llm — MCP client
"""Lightweight MCP HTTP JSON-RPC client used by unit/system tests."""

from __future__ import annotations

from typing import Any

import httpx

from cloud_dog_llm.mcp.session import MCPSession
from cloud_dog_llm.mcp.transports.http_jsonrpc import HTTPJSONRPCTransport
from cloud_dog_llm.mcp.transports.legacy_sse import LegacySSETransport
from cloud_dog_llm.mcp.transports.stdio import StdioTransport
from cloud_dog_llm.mcp.transports.streamable_http import StreamableHTTPTransport


class MCPClient:
    """Represent m c p client."""
    def __init__(self, base_url: str, client: httpx.AsyncClient | None = None, transport: str = "http_jsonrpc") -> None:
        self.base_url = base_url.rstrip("/")
        self._client = client or httpx.AsyncClient(timeout=30.0)
        self._session = MCPSession()
        self._transport_name = transport

    def _transport(self):
        headers = self._session.headers()
        if self._transport_name == "streamable_http":
            return StreamableHTTPTransport(self.base_url, self._client, headers)
        if self._transport_name == "legacy_sse":
            return LegacySSETransport(self.base_url, self._client, headers)
        if self._transport_name == "stdio":
            return StdioTransport()
        return HTTPJSONRPCTransport(self.base_url, self._client, headers)

    async def initialize(self) -> str | None:
        """Handle initialize."""
        response = await self._client.post(f"{self.base_url}/initialize", json={"protocolVersion": "2025-03-26"})
        if response.status_code < 400:
            self._session.session_id = response.headers.get("Mcp-Session-Id") or ""
        return self._session.session_id or None

    async def tools_list(self) -> dict[str, Any]:
        """Handle tools list."""
        return await self._transport().send({"jsonrpc": "2.0", "id": "1", "method": "tools/list", "params": {}})

    async def tools_call(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """Handle tools call."""
        return await self._transport().send(
            {
                "jsonrpc": "2.0",
                "id": "2",
                "method": "tools/call",
                "params": {"name": name, "arguments": arguments},
            }
        )
