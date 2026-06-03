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
from cloud_dog_llm.providers.openai_compat import OpenAICompatAdapter


@pytest.mark.asyncio
async def test_openai_compat_invoke() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/chat/completions"):
            auth = request.headers.get("Authorization", "")
            assert auth == "Bearer k"
            return httpx.Response(
                200,
                json={
                    "id": "r1",
                    "model": "qwen/qwen3-14b",
                    "choices": [{"message": {"content": "ok"}}],
                    "usage": {"prompt_tokens": 1, "completion_tokens": 1, "total_tokens": 2},
                },
            )
        if request.url.path.endswith("/models"):
            return httpx.Response(200, json={"data": []})
        return httpx.Response(404)

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    adapter = OpenAICompatAdapter(
        ProviderConfig("openai", "https://openai.test/v1", "qwen", api_key="k"), client=client
    )

    rsp = await adapter.invoke(LLMRequest(messages=[Message(role="user", content="x")]))
    assert rsp.content == "ok"
    assert rsp.usage.total_tokens == 2
    assert await adapter.health() is True


@pytest.mark.asyncio
async def test_openai_compat_stream_sse() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/chat/completions"):
            body = request.read().decode("utf-8").replace(" ", "")
            if '"stream":true' in body:
                content = (
                    'data: {"choices":[{"delta":{"content":"hel"}}]}\n\n'
                    'data: {"choices":[{"delta":{"content":"lo"}}]}\n\n'
                    "data: [DONE]\n\n"
                ).encode("utf-8")
                return httpx.Response(200, content=content, headers={"Content-Type": "text/event-stream"})
            return httpx.Response(200, json={"choices": [{"message": {"content": "ok"}}], "usage": {}})
        if request.url.path.endswith("/models"):
            return httpx.Response(200, json={"data": []})
        return httpx.Response(404)

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    adapter = OpenAICompatAdapter(
        ProviderConfig("openai", "https://openai.test/v1", "qwen", api_key="k"), client=client
    )
    events = [e async for e in adapter.invoke_stream(LLMRequest(messages=[Message(role="user", content="x")]))]
    assert [e.type.value for e in events] == ["response_started", "delta_text", "delta_text", "response_completed"]
    assert "".join(e.text for e in events if e.text) == "hello"
