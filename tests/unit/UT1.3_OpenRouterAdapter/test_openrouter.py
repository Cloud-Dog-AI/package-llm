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

from cloud_dog_llm.config.models import ProviderConfig
from cloud_dog_llm.domain.models import LLMRequest, Message
from cloud_dog_llm.providers.openrouter import OpenRouterAdapter


@pytest.mark.asyncio
async def test_openrouter_headers() -> None:
    seen = {"referer": "", "title": ""}

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/chat/completions"):
            seen["referer"] = request.headers.get("HTTP-Referer", "")
            seen["title"] = request.headers.get("X-Title", "")
            return httpx.Response(200, json={"id": "r", "model": "m", "choices": [{"message": {"content": "done"}}]})
        return httpx.Response(404)

    adapter = OpenRouterAdapter(
        ProviderConfig("openrouter", "https://openrouter.ai/api/v1", "qwen/qwen3-14b", api_key="k")
    )
    adapter._client = httpx.AsyncClient(transport=httpx.MockTransport(handler))

    rsp = await adapter.invoke(LLMRequest(messages=[Message(role="user", content="h")]))
    assert rsp.content == "done"
    assert seen["referer"]
    assert seen["title"]
