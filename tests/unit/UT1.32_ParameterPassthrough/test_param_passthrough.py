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
async def test_request_param_passthrough_to_provider() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/chat/completions"):
            body = request.read().decode("utf-8")
            assert '"top_p":0.9' in body.replace(" ", "")
            return httpx.Response(200, json={"choices": [{"message": {"content": "ok"}}], "usage": {}})
        return httpx.Response(200, json={"data": []})

    adapter = OpenAICompatAdapter(
        ProviderConfig("openai", "https://openai.test/v1", "m1"),
        client=httpx.AsyncClient(transport=httpx.MockTransport(handler)),
    )
    await adapter.invoke(
        LLMRequest(messages=[Message(role="user", content="x")], params={"top_p": 0.9, "x_provider.foo": 1})
    )
