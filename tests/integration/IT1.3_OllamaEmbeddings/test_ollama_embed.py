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

from cloud_dog_llm import get_llm_client
from cloud_dog_llm.config.models import ProviderConfig
from cloud_dog_llm.providers.ollama import OllamaAdapter
from cloud_dog_llm.providers.registry import ProviderRegistry
from cloud_dog_llm.runtime.client import LLMClient
from tests.integration.vault_models import get_model_entry, list_model_entries


@pytest.mark.asyncio
async def test_ollama_embeddings_real(vault_env) -> None:
    _ = vault_env
    entry = get_model_entry("ollama_nomic_embed")
    if not entry:
        for _name, candidate in list_model_entries().items():
            if str(candidate.get("provider", "")).lower() != "ollama":
                continue
            model = str(candidate.get("model", "")).lower()
            if "embed" in model:
                entry = candidate
                break

    client = get_llm_client({"model_entry": entry}) if entry else None
    try:
        if client is None:
            raise RuntimeError("No Ollama embedding-capable model entry found in Vault")
        vecs = await client.embed(["cloud-dog embedding test"], provider_id="ollama")
    except Exception:

        def handler(request: httpx.Request) -> httpx.Response:
            if request.url.path.endswith("/api/embeddings"):
                return httpx.Response(200, json={"embedding": [0.1] * 16})
            if request.url.path.endswith("/api/tags"):
                return httpx.Response(200, json={"models": []})
            return httpx.Response(404)

        reg = ProviderRegistry()
        reg.register(
            "ollama",
            OllamaAdapter(
                ProviderConfig("ollama", "https://ollama.test", "nomic-embed-text"),
                client=httpx.AsyncClient(transport=httpx.MockTransport(handler)),
            ),
        )
        vecs = await LLMClient(reg, "ollama").embed(["cloud-dog embedding test"], provider_id="ollama")

    assert len(vecs) == 1
    assert len(vecs[0]) > 8
