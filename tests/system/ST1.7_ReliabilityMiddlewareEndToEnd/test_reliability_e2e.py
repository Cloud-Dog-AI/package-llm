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

import pytest

from cloud_dog_llm import LLMRequest, Message, SessionContext
from cloud_dog_llm.domain.models import LLMResponse
from cloud_dog_llm.middleware.reliability import FixedWindowRateLimiter, ReliabilityPolicy, ReliabilityPolicyMiddleware
from cloud_dog_llm.providers.base import ProviderAdapter
from cloud_dog_llm.providers.registry import ProviderRegistry
from cloud_dog_llm.registry.capabilities import CapabilityDescriptor
from cloud_dog_llm.runtime.client import LLMClient


class _FailThenPassAdapter(ProviderAdapter):
    def __init__(self) -> None:
        self.calls = 0

    async def invoke(self, request):
        self.calls += 1
        if self.calls == 1:
            raise RuntimeError("provider down")
        return LLMResponse(request_id="r", provider_id="test", model_id="m", content="ok")

    async def invoke_stream(self, request):
        if False:
            yield None

    async def health(self) -> bool:
        return True

    def capabilities(self) -> CapabilityDescriptor:
        return CapabilityDescriptor(provider_id="test", model_id="m")


@pytest.mark.asyncio
async def test_error_path_uses_fallback_and_rate_limiter_blocks() -> None:
    reg = ProviderRegistry()
    reg.register("test", _FailThenPassAdapter())

    limiter = FixedWindowRateLimiter(max_requests=1, window_seconds=60)
    middleware = ReliabilityPolicyMiddleware(
        policy=ReliabilityPolicy(fallback_content="fallback", append_footer="|safe"),
        limiter=limiter,
    )
    client = LLMClient(reg, default_provider_id="test", middlewares=[middleware])

    session = SessionContext(session_id="s", correlation_id="c", user_id="u")
    req = LLMRequest(messages=[Message(role="user", content="hello")])

    first = await client.chat(req, session)
    assert first.content == "fallback|safe"

    with pytest.raises(RuntimeError, match="rate limit exceeded"):
        await client.chat(req, session)
