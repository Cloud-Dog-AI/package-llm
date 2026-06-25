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

import httpx
import pytest

from cloud_dog_llm.mcp.client import MCPClient


@pytest.mark.asyncio
async def test_mcp_tool_call_end_to_end_mocked() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/initialize"):
            return httpx.Response(200, json={"ok": True}, headers={"Mcp-Session-Id": "sid-1"})
        if request.url.path.endswith("/messages"):
            body = request.read().decode("utf-8")
            if '"tools/call"' in body:
                return httpx.Response(200, json={"result": {"content": [{"type": "text", "text": "ok"}]}})
            return httpx.Response(200, json={"result": {"tools": [{"name": "search"}]}})
        return httpx.Response(404, json={})

    client = MCPClient("https://mcp.test", client=httpx.AsyncClient(transport=httpx.MockTransport(handler)))
    await client.initialize()
    listed = await client.tools_list()
    called = await client.tools_call("search", {"q": "x"})
    assert listed["result"]["tools"][0]["name"] == "search"
    assert called["result"]["content"][0]["text"] == "ok"
