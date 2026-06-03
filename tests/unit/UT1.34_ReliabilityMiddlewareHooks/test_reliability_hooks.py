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

from dataclasses import dataclass

import pytest

from cloud_dog_llm.domain.models import LLMRequest, LLMResponse, Message, SessionContext
from cloud_dog_llm.middleware.base import MiddlewareChain
from cloud_dog_llm.middleware.reliability import ReliabilityPolicy, ReliabilityPolicyMiddleware


@dataclass
class _TrackingMiddleware:
    name: str
    enabled: bool = True

    async def pre_request(self, request: LLMRequest, session: SessionContext) -> LLMRequest:
        _ = session
        request.params[f"pre_{self.name}"] = True
        return request

    async def post_response(self, request: LLMRequest, response: LLMResponse, session: SessionContext) -> LLMResponse:
        _ = request
        _ = session
        return LLMResponse(
            request_id=response.request_id,
            provider_id=response.provider_id,
            model_id=response.model_id,
            content=f"{response.content}|post_{self.name}",
            tool_calls=response.tool_calls,
            finish_reason=response.finish_reason,
            usage=response.usage,
            timing=response.timing,
            raw_provider_response=response.raw_provider_response,
        )

    async def on_error(
        self,
        request: LLMRequest,
        error: Exception,
        session: SessionContext,
    ) -> LLMResponse | Exception | None:
        _ = request
        _ = session
        return error


@pytest.mark.asyncio
async def test_chain_order_modifies_request_and_response() -> None:
    session = SessionContext(session_id="s1", correlation_id="c1", user_id="u1")
    req = LLMRequest(messages=[Message(role="user", content="hello")])
    m1 = _TrackingMiddleware("one")
    m2 = _TrackingMiddleware("two")
    chain = MiddlewareChain([m1, m2])

    async def invoke(r: LLMRequest) -> LLMResponse:
        assert r.params["pre_one"] is True
        assert r.params["pre_two"] is True
        return LLMResponse(request_id="r1", provider_id="p", model_id="m", content="ok")

    rsp = await chain.run(req, session, invoke)
    assert rsp.content == "ok|post_two|post_one"


@pytest.mark.asyncio
async def test_on_error_returns_fallback_response() -> None:
    session = SessionContext(session_id="s1", correlation_id="c1")
    req = LLMRequest(messages=[Message(role="user", content="hello")])
    fallback = ReliabilityPolicyMiddleware(policy=ReliabilityPolicy(fallback_content="fallback"))
    chain = MiddlewareChain([fallback])

    async def invoke(_: LLMRequest) -> LLMResponse:
        raise RuntimeError("boom")

    rsp = await chain.run(req, session, invoke)
    assert rsp.content == "fallback"


@pytest.mark.asyncio
async def test_disabled_middleware_is_skipped() -> None:
    session = SessionContext(session_id="s1", correlation_id="c1")
    req = LLMRequest(messages=[Message(role="user", content="hello")])
    disabled = _TrackingMiddleware("off", enabled=False)
    chain = MiddlewareChain([disabled])

    async def invoke(r: LLMRequest) -> LLMResponse:
        assert "pre_off" not in r.params
        return LLMResponse(request_id="r1", provider_id="p", model_id="m", content="ok")

    rsp = await chain.run(req, session, invoke)
    assert rsp.content == "ok"
