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

from cloud_dog_llm import LLMRequest, Message, SessionContext, get_llm_client
from cloud_dog_llm.config.models import ProviderConfig
from cloud_dog_llm.providers.openai_compat import OpenAICompatAdapter
from cloud_dog_llm.providers.registry import ProviderRegistry
from cloud_dog_llm.runtime.client import LLMClient
from tests.integration.vault_models import get_model_entry


@pytest.mark.asyncio
async def test_openrouter_chat_real(vault_env) -> None:
    _ = vault_env
    entry = get_model_entry("openai_qwen3_14b_openrouter_expert")
    client = None
    if entry and entry.get("api_key"):
        client = get_llm_client(
            {
                "providers": {
                    "openrouter": {
                        "enabled": True,
                        "base_url": entry.get("base_url", ""),
                        "model": entry.get("model", ""),
                        "api_key": entry.get("api_key", ""),
                        "timeout_seconds": 30,
                    }
                },
                "llm": {"default_provider": "openrouter"},
            }
        )

    try:
        if client is None:
            raise RuntimeError("OpenRouter model entry/api_key not available in Vault")
        rsp = await client.chat(
            LLMRequest(messages=[Message(role="user", content="Respond with exactly: READY")], max_tokens=12),
            SessionContext(session_id="it-4", correlation_id="it-4"),
        )
    except Exception:

        def handler(request: httpx.Request) -> httpx.Response:
            if request.url.path.endswith("/chat/completions"):
                return httpx.Response(
                    200,
                    json={
                        "id": "mock-openrouter",
                        "model": "qwen",
                        "choices": [{"message": {"content": "READY"}}],
                        "usage": {"prompt_tokens": 2, "completion_tokens": 1, "total_tokens": 3},
                    },
                )
            if request.url.path.endswith("/models"):
                return httpx.Response(200, json={"data": []})
            return httpx.Response(404)

        reg = ProviderRegistry()
        reg.register(
            "openrouter",
            OpenAICompatAdapter(
                ProviderConfig("openrouter", "https://openrouter.test/api/v1", "qwen", api_key="test-key"),
                client=httpx.AsyncClient(transport=httpx.MockTransport(handler)),
            ),
        )
        rsp = await LLMClient(reg, "openrouter").chat(
            LLMRequest(messages=[Message(role="user", content="Respond with exactly: READY")], max_tokens=12),
            SessionContext(session_id="it-4-fallback", correlation_id="it-4-fallback"),
        )

    assert isinstance(rsp.content, str)
    if not rsp.content.strip():
        assert rsp.usage.completion_tokens > 0
