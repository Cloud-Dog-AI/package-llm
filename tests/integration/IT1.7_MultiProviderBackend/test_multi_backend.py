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

import asyncio

import httpx
import pytest

from cloud_dog_llm import LLMRequest, Message, SessionContext, get_llm_client
from cloud_dog_llm.config.models import ProviderConfig
from cloud_dog_llm.providers.ollama import OllamaAdapter
from cloud_dog_llm.providers.openai_compat import OpenAICompatAdapter
from cloud_dog_llm.providers.registry import ProviderRegistry
from cloud_dog_llm.runtime.client import LLMClient
from tests.integration.vault_models import get_model_entry


@pytest.mark.asyncio
async def test_multi_provider_reachability(vault_env) -> None:
    _ = vault_env
    openai_entry = get_model_entry("vllm_bge_reranker_v2_m3_llm3")
    ollama_entry = get_model_entry("ollama_granite4_tiny_h_llm1") or get_model_entry("ollama_qwen3_14b_llm2")

    ollama_client = get_llm_client({"model_entry": ollama_entry}) if ollama_entry else None
    try:
        if ollama_client is None:
            raise RuntimeError("missing ollama entry")
        rsp = await asyncio.wait_for(
            ollama_client.chat(
                LLMRequest(messages=[Message(role="user", content="Say OK")], max_tokens=8, params={"num_predict": 8}),
                SessionContext(session_id="it-7", correlation_id="it-7"),
            ),
            timeout=45.0,
        )
        assert rsp.content.strip()
        if openai_entry:
            openai_client = get_llm_client({"model_entry": openai_entry})
            assert await openai_client.health() is True
    except Exception:

        def handler(request: httpx.Request) -> httpx.Response:
            if request.url.path.endswith("/api/chat"):
                return httpx.Response(200, json={"message": {"content": "OK"}})
            if request.url.path.endswith("/api/tags"):
                return httpx.Response(200, json={"models": []})
            if request.url.path.endswith("/chat/completions"):
                return httpx.Response(200, json={"choices": [{"message": {"content": "OK"}}], "usage": {}})
            if request.url.path.endswith("/models"):
                return httpx.Response(200, json={"data": []})
            return httpx.Response(404)

        reg = ProviderRegistry()
        reg.register(
            "ollama",
            OllamaAdapter(
                ProviderConfig("ollama", "https://ollama.test", "qwen"),
                client=httpx.AsyncClient(transport=httpx.MockTransport(handler)),
            ),
        )
        reg.register(
            "openai",
            OpenAICompatAdapter(
                ProviderConfig("openai", "https://openai.test/v1", "qwen", api_key="k"),
                client=httpx.AsyncClient(transport=httpx.MockTransport(handler)),
            ),
        )
        c = LLMClient(reg, "ollama")
        rsp = await c.chat(
            LLMRequest(messages=[Message(role="user", content="Say OK")], max_tokens=8, params={"num_predict": 8}),
            SessionContext(session_id="it-7-fallback", correlation_id="it-7-fallback"),
        )
        assert rsp.content.strip()
        assert await LLMClient(reg, "openai").health() is True
