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

# cloud_dog_llm — Middleware base abstractions
"""Composable middleware interfaces for LLM runtime request pipelines."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Protocol

from cloud_dog_llm.domain.models import LLMRequest, LLMResponse, SessionContext


class LLMMiddleware(Protocol):
    """Define hooks for request and response middleware."""

    enabled: bool

    async def pre_request(self, request: LLMRequest, session: SessionContext) -> LLMRequest:
        """Process a request before provider execution."""
        ...

    async def post_response(
        self,
        request: LLMRequest,
        response: LLMResponse,
        session: SessionContext,
    ) -> LLMResponse:
        """Process a response after provider execution."""
        ...

    async def on_error(
        self,
        request: LLMRequest,
        error: Exception,
        session: SessionContext,
    ) -> LLMResponse | Exception | None:
        """Handle an exception raised during middleware or provider execution."""
        ...


class ShortCircuitResponse(Exception):
    """Raised by middleware to bypass provider execution with a ready response."""

    def __init__(self, response: LLMResponse) -> None:
        super().__init__("LLM request short-circuited by middleware")
        self.response = response


class MiddlewareChain:
    """Run enabled middleware around the provider invocation."""

    def __init__(self, middlewares: list[LLMMiddleware] | None = None) -> None:
        self._middlewares = [m for m in (middlewares or []) if getattr(m, "enabled", True)]

    async def run(
        self,
        request: LLMRequest,
        session: SessionContext,
        invoke: Callable[[LLMRequest], Awaitable[LLMResponse]],
    ) -> LLMResponse:
        """Execute the middleware pipeline and provider callback."""
        current_request = request
        executed: list[LLMMiddleware] = []

        try:
            for middleware in self._middlewares:
                current_request = await middleware.pre_request(current_request, session)
                executed.append(middleware)
            response = await invoke(current_request)
        except ShortCircuitResponse as short_circuit:
            response = short_circuit.response
        except Exception as exc:
            handled: LLMResponse | Exception | None = None
            for middleware in reversed(executed):
                handled = await middleware.on_error(current_request, exc, session)
                if isinstance(handled, LLMResponse):
                    response = handled
                    break
                if isinstance(handled, Exception):
                    exc = handled
            else:
                raise exc

        for middleware in reversed(executed):
            response = await middleware.post_response(current_request, response, session)
        return response
