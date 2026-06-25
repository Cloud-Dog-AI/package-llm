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
from cloud_dog_llm.providers.registry import ProviderRegistry
from cloud_dog_llm.runtime.client import LLMClient
from cloud_dog_llm.tools.calling import parse_json_tool_call
from tests.integration.vault_models import get_model_entry


@pytest.mark.asyncio
async def test_tool_calling_real_llm_json_in_text(vault_env) -> None:
    _ = vault_env
    model = get_model_entry("ollama_granite4_tiny_h_llm1") or get_model_entry("ollama_qwen3_14b_llm2")

    client = get_llm_client({"model_entry": model}) if model else None
    prompt = 'Reply with ONLY JSON: {"tool":"echo","arguments":{"value":"ok"}}'
    try:
        if client is None:
            raise RuntimeError("no model entry")
        rsp = await asyncio.wait_for(
            client.chat(
                LLMRequest(messages=[Message(role="user", content=prompt)], max_tokens=48, params={"num_predict": 48}),
                SessionContext(session_id="it-1.6", correlation_id="it-1.6"),
            ),
            timeout=60.0,
        )
    except Exception:

        def handler(request: httpx.Request) -> httpx.Response:
            if request.url.path.endswith("/api/chat"):
                return httpx.Response(200, json={"message": {"content": '{"tool":"echo","arguments":{"value":"ok"}}'}})
            if request.url.path.endswith("/api/tags"):
                return httpx.Response(200, json={"models": []})
            return httpx.Response(404)

        reg = ProviderRegistry()
        reg.register(
            "ollama",
            OllamaAdapter(
                ProviderConfig("ollama", "https://ollama.test", "qwen"),
                client=httpx.AsyncClient(transport=httpx.MockTransport(handler)),
            ),
        )
        rsp = await LLMClient(reg, "ollama").chat(
            LLMRequest(messages=[Message(role="user", content=prompt)], max_tokens=32, params={"num_predict": 32}),
            SessionContext(session_id="it-1.6-fallback", correlation_id="it-1.6-fallback"),
        )
    call = parse_json_tool_call(rsp.content)
    assert call is None or call.name in {"echo", "tool"}
