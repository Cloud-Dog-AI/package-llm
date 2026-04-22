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

# cloud_dog_llm — Reliability middleware
"""Reliability middleware primitives: rate limiting and error fallback policies."""

from __future__ import annotations

import time
from dataclasses import dataclass

from cloud_dog_llm.domain.models import LLMRequest, LLMResponse, SessionContext
from cloud_dog_llm.middleware.base import LLMMiddleware


class FixedWindowRateLimiter:
    """Per-key in-memory fixed-window limiter for middleware checks."""

    def __init__(self, *, max_requests: int, window_seconds: int) -> None:
        self._max_requests = max_requests
        self._window_seconds = window_seconds
        self._windows: dict[str, tuple[float, int]] = {}

    def allow(self, key: str) -> bool:
        """Handle allow."""
        now = time.time()
        start, count = self._windows.get(key, (now, 0))
        if now - start >= self._window_seconds:
            start, count = now, 0
        count += 1
        self._windows[key] = (start, count)
        return count <= self._max_requests


@dataclass(frozen=True, slots=True)
class ReliabilityPolicy:
    """Represent reliability policy."""
    fallback_content: str | None = None
    append_footer: str | None = None


class ReliabilityPolicyMiddleware(LLMMiddleware):
    """Represent reliability policy middleware."""
    enabled: bool

    def __init__(
        self,
        *,
        policy: ReliabilityPolicy | None = None,
        limiter: FixedWindowRateLimiter | None = None,
        enabled: bool = True,
    ) -> None:
        self.enabled = enabled
        self._policy = policy or ReliabilityPolicy()
        self._limiter = limiter

    async def pre_request(self, request: LLMRequest, session: SessionContext) -> LLMRequest:
        """Handle pre request."""
        if self._limiter is None:
            return request
        identity = session.user_id or session.session_id
        if not self._limiter.allow(identity):
            raise RuntimeError("rate limit exceeded")
        return request

    async def post_response(
        self,
        request: LLMRequest,
        response: LLMResponse,
        session: SessionContext,
    ) -> LLMResponse:
        """Handle post response."""
        _ = request
        _ = session
        if self._policy.append_footer:
            return LLMResponse(
                request_id=response.request_id,
                provider_id=response.provider_id,
                model_id=response.model_id,
                content=f"{response.content}{self._policy.append_footer}",
                tool_calls=response.tool_calls,
                finish_reason=response.finish_reason,
                usage=response.usage,
                timing=response.timing,
                raw_provider_response=response.raw_provider_response,
            )
        return response

    async def on_error(
        self,
        request: LLMRequest,
        error: Exception,
        session: SessionContext,
    ) -> LLMResponse | Exception | None:
        """Handle on error."""
        _ = request
        _ = session
        if self._policy.fallback_content is None:
            return error
        return LLMResponse(
            request_id="fallback",
            provider_id=request.provider_id or "default",
            model_id=request.model or "unknown",
            content=self._policy.fallback_content,
            raw_provider_response={"error": str(error), "fallback": True},
        )
