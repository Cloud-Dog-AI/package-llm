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
from cloud_dog_llm.providers.ollama import OllamaAdapter
from cloud_dog_llm.testing.conformance import adapter_has_required_methods


@pytest.mark.asyncio
async def test_conformance_adapter_contract_and_health() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/api/tags"):
            return httpx.Response(200, json={"models": []})
        if request.url.path.endswith("/api/chat"):
            return httpx.Response(200, json={"message": {"content": "ok"}})
        return httpx.Response(404)

    adapter = OllamaAdapter(
        ProviderConfig("ollama", "https://llm2.example.test", "qwen3:14b"),
        client=httpx.AsyncClient(transport=httpx.MockTransport(handler)),
    )
    assert adapter_has_required_methods(adapter) is True
    assert await adapter.health() is True
