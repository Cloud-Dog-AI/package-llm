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

from cloud_dog_llm.a2a.client import A2AClient


@pytest.mark.asyncio
async def test_a2a_envelope_normalization() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["X-Correlation-Id"] == "c-1"
        return httpx.Response(200, headers={"X-Correlation-Id": "c-1"}, json={"data": {"ok": True}})

    client = A2AClient("https://a2a.test", client=httpx.AsyncClient(transport=httpx.MockTransport(handler)))
    data = await client.request("notify", {"x": 1}, "c-1")
    assert data["ok"] is True
    assert data["data"]["ok"] is True
