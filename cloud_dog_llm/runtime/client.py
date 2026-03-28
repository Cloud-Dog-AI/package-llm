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

# cloud_dog_llm — Runtime LLM client
"""Main runtime client coordinating provider adapters and embeddings."""

from __future__ import annotations

from collections.abc import AsyncIterator

from cloud_dog_llm.domain.models import LLMEvent, LLMRequest, LLMResponse, Message, SessionContext
from cloud_dog_llm.embeddings.manager import EmbeddingManager
from cloud_dog_llm.middleware.base import LLMMiddleware, MiddlewareChain
from cloud_dog_llm.providers.registry import ProviderRegistry


class LLMClient:
    """Represent l l m client."""
    def __init__(
        self,
        provider_registry: ProviderRegistry,
        default_provider_id: str,
        *,
        middlewares: list[LLMMiddleware] | None = None,
    ) -> None:
        self._providers = provider_registry
        self._default_provider_id = default_provider_id
        self._middleware_chain = MiddlewareChain(middlewares)

    def _provider_for(self, request: LLMRequest):
        provider_id = request.provider_id or self._default_provider_id
        return self._providers.get(provider_id)

    async def chat(self, request: LLMRequest, session: SessionContext) -> LLMResponse:
        """Handle chat."""
        async def _invoke(req: LLMRequest) -> LLMResponse:
            return await self._provider_for(req).invoke(req)

        return await self._middleware_chain.run(request, session, _invoke)

    async def complete(
        self,
        prompt: str,
        *,
        session: SessionContext,
        provider_id: str | None = None,
        model: str | None = None,
        max_tokens: int | None = None,
    ) -> LLMResponse:
        """Handle complete."""
        request = LLMRequest(
            provider_id=provider_id,
            model=model,
            max_tokens=max_tokens,
            messages=[Message(role="user", content=prompt)],
        )
        return await self.chat(request, session)

    async def chat_stream(self, request: LLMRequest, session: SessionContext) -> AsyncIterator[LLMEvent]:
        """Handle chat stream."""
        _ = session
        async for event in self._provider_for(request).invoke_stream(request):
            yield event

    async def embed(
        self, texts: list[str], *, provider_id: str | None = None, model: str | None = None
    ) -> list[list[float]]:
        """Handle embed."""
        pid = provider_id or self._default_provider_id
        manager = EmbeddingManager(self._providers.get(pid), model=model)
        return await manager.generate_embeddings(texts)

    async def health(self) -> bool:
        """Handle health."""
        for pid in self._providers.list_ids():
            if not await self._providers.get(pid).health():
                return False
        return True
