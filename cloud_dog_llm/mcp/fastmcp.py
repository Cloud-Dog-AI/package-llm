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

from __future__ import annotations

from cloud_dog_llm.mcp.client import MCPClient


def from_fastmcp_url(base_url: str) -> MCPClient:
    """Handle from fastmcp url."""
    return MCPClient(base_url)


def from_fastmcp_config(config: dict) -> MCPClient:
    """Handle from fastmcp config."""
    base_url = str(config.get("base_url", "")).strip()
    if not base_url:
        raise ValueError("FastMCP config requires non-empty base_url")
    transport = str(config.get("transport", "http_jsonrpc"))
    return MCPClient(base_url, transport=transport)
