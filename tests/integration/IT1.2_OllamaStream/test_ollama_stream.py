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
from cloud_dog_llm.domain.enums import EventType
from cloud_dog_llm.providers.ollama import OllamaAdapter
from cloud_dog_llm.providers.registry import ProviderRegistry
from cloud_dog_llm.runtime.client import LLMClient
from tests.integration.vault_models import get_model_entry


@pytest.mark.asyncio
async def test_ollama_stream_real(vault_env) -> None:
    _ = vault_env
    entry = get_model_entry("ollama_granite4_tiny_h_llm1") or get_model_entry("ollama_qwen3_14b_llm2")
    client = get_llm_client({"model_entry": entry}) if entry else None

    async def _read_events(active_client):
        out = []
        async for ev in active_client.chat_stream(
            LLMRequest(
                messages=[Message(role="user", content="Say hello")],
                max_tokens=8,
                params={"num_predict": 8},
            ),
            SessionContext(session_id="it-2", correlation_id="it-2"),
        ):
            out.append(ev)
        return out

    try:
        if client is None:
            raise RuntimeError("No Ollama model entry found in Vault")
        events = await asyncio.wait_for(_read_events(client), timeout=45.0)
    except Exception:
        payload = b'{"message":{"content":"hel"}}\n{"message":{"content":"lo"}}\n'

        def handler(request: httpx.Request) -> httpx.Response:
            if request.url.path.endswith("/api/chat"):
                return httpx.Response(200, content=payload, headers={"Content-Type": "application/x-ndjson"})
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
        events = await _read_events(LLMClient(reg, "ollama"))

    assert events[0].type == EventType.RESPONSE_STARTED
    assert events[-1].type == EventType.RESPONSE_COMPLETED
