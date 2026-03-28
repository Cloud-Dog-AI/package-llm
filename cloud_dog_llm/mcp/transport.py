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

# cloud_dog_llm — MCP transport selector
"""Factory for MCP transport instances by name."""

from __future__ import annotations

import httpx

from cloud_dog_llm.mcp.transports.http_jsonrpc import HTTPJSONRPCTransport
from cloud_dog_llm.mcp.transports.legacy_sse import LegacySSETransport
from cloud_dog_llm.mcp.transports.stdio import StdioTransport
from cloud_dog_llm.mcp.transports.streamable_http import StreamableHTTPTransport


def select_transport(name: str, base_url: str, client: httpx.AsyncClient, headers: dict[str, str]):
    """Handle select transport."""
    if name == "streamable_http":
        return StreamableHTTPTransport(base_url, client, headers)
    if name == "legacy_sse":
        return LegacySSETransport(base_url, client, headers)
    if name == "stdio":
        return StdioTransport()
    return HTTPJSONRPCTransport(base_url, client, headers)
