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
from cloud_dog_llm.providers.ollama import OllamaAdapter


@pytest.mark.asyncio
async def test_ollama_chat_and_health() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/api/chat"):
            return httpx.Response(200, json={"message": {"content": "hello"}})
        if request.url.path.endswith("/api/tags"):
            return httpx.Response(200, json={"models": []})
        return httpx.Response(404)

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    adapter = OllamaAdapter(ProviderConfig("ollama", "http://ollama", "qwen3:14b"), client=client)

    rsp = await adapter.invoke(LLMRequest(messages=[Message(role="user", content="hi")]))
    assert rsp.content == "hello"
    assert await adapter.health() is True


@pytest.mark.asyncio
async def test_ollama_embeddings() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/api/embeddings"):
            return httpx.Response(200, json={"embedding": [0.1, 0.2]})
        return httpx.Response(404)

    client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    adapter = OllamaAdapter(ProviderConfig("ollama", "http://ollama", "nomic-embed-text"), client=client)

    vecs = await adapter.embeddings(["a", "b"])
    assert vecs == [[0.1, 0.2], [0.1, 0.2]]


@pytest.mark.asyncio
async def test_ollama_streaming_parses_line_events() -> None:
    def stream_handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/api/chat"):
            if b'"stream":false' in request.content.replace(b" ", b""):
                return httpx.Response(200, json={"message": {"content": "non-stream"}})
            payload = b'{"message":{"content":"hel"}}\n{"message":{"content":"lo"}}\n'
            return httpx.Response(200, content=payload, headers={"Content-Type": "application/x-ndjson"})
        if request.url.path.endswith("/api/tags"):
            return httpx.Response(200, json={"models": []})
        return httpx.Response(404)

    client = httpx.AsyncClient(transport=httpx.MockTransport(stream_handler))
    adapter = OllamaAdapter(ProviderConfig("ollama", "http://ollama", "qwen3:14b"), client=client)
    events = [e async for e in adapter.invoke_stream(LLMRequest(messages=[Message(role="user", content="hi")]))]
    assert [e.type.value for e in events] == ["response_started", "delta_text", "delta_text", "response_completed"]
    assert "".join(e.text for e in events if e.text) == "hello"
