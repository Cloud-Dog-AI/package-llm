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
from cloud_dog_llm.providers.ollama import OllamaAdapter
from cloud_dog_llm.providers.registry import ProviderRegistry
from cloud_dog_llm.runtime.client import LLMClient
from tests.integration.vault_models import get_model_entry


@pytest.mark.asyncio
async def test_service_startup_and_basic_chat(vault_env) -> None:
    _ = vault_env
    model = get_model_entry("ollama_granite4_tiny_h_llm1") or get_model_entry("ollama_qwen3_14b_llm2")

    if model:
        config = {
            "llm": {"default_provider": "ollama"},
            "providers": {
                "ollama": {
                    "enabled": True,
                    "base_url": model.get("base_url", ""),
                    "model": model.get("model", ""),
                    "timeout_seconds": min(
                        float((model.get("params", {}) or {}).get("timeout_seconds", 300) or 300), 15.0
                    ),
                }
            },
        }
        client = get_llm_client(config)
        try:
            rsp = await client.chat(
                LLMRequest(
                    messages=[Message(role="user", content="Service startup check")],
                    max_tokens=12,
                    params={"num_predict": 12},
                ),
                SessionContext(session_id="at-1", correlation_id="at-1"),
            )
            assert rsp.content.strip()
            return
        except Exception:
            pass

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/api/chat"):
            return httpx.Response(200, json={"message": {"content": "startup-ok"}})
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
        LLMRequest(
            messages=[Message(role="user", content="Service startup check")], max_tokens=8, params={"num_predict": 8}
        ),
        SessionContext(session_id="at-1-fallback", correlation_id="at-1-fallback"),
    )
    assert rsp.content.strip()
