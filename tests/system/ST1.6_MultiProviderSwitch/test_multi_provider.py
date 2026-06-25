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

from cloud_dog_llm import Message, LLMRequest, SessionContext
from cloud_dog_llm.config.models import ProviderConfig
from cloud_dog_llm.providers.ollama import OllamaAdapter
from cloud_dog_llm.providers.openai_compat import OpenAICompatAdapter
from cloud_dog_llm.providers.registry import ProviderRegistry
from cloud_dog_llm.runtime.client import LLMClient


@pytest.mark.asyncio
async def test_switch_between_ollama_and_openai() -> None:
    def o_handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/api/chat"):
            return httpx.Response(200, json={"message": {"content": "from ollama"}})
        return httpx.Response(404)

    def x_handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/chat/completions"):
            return httpx.Response(
                200, json={"id": "x", "model": "m", "choices": [{"message": {"content": "from openai"}}]}
            )
        return httpx.Response(404)

    reg = ProviderRegistry()
    reg.register(
        "ollama",
        OllamaAdapter(
            ProviderConfig("ollama", "http://ollama", "m"),
            client=httpx.AsyncClient(transport=httpx.MockTransport(o_handler)),
        ),
    )
    reg.register(
        "openai",
        OpenAICompatAdapter(
            ProviderConfig("openai", "http://openai/v1", "m"),
            client=httpx.AsyncClient(transport=httpx.MockTransport(x_handler)),
        ),
    )

    client = LLMClient(reg, default_provider_id="ollama")
    session = SessionContext(session_id="s", correlation_id="c")

    r1 = await client.chat(LLMRequest(messages=[Message(role="user", content="a")]), session)
    r2 = await client.chat(LLMRequest(messages=[Message(role="user", content="b")], provider_id="openai"), session)

    assert r1.content == "from ollama"
    assert r2.content == "from openai"
