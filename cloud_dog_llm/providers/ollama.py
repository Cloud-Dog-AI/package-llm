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

# cloud_dog_llm — Ollama provider adapter
"""Adapter for Ollama chat/generate and embeddings APIs."""

from __future__ import annotations

import uuid
import json
from collections.abc import AsyncIterator

import httpx

from cloud_dog_llm.config.models import ProviderConfig
from cloud_dog_llm.domain.enums import EventType
from cloud_dog_llm.domain.errors import InvalidRequestError, ProviderUnavailableError
from cloud_dog_llm.domain.models import LLMEvent, LLMRequest, LLMResponse
from cloud_dog_llm.multimodal.handler import to_provider_text
from cloud_dog_llm.providers.base import ProviderAdapter
from cloud_dog_llm.registry.capabilities import CapabilityDescriptor


class OllamaAdapter(ProviderAdapter):
    """Represent ollama adapter."""
    def __init__(self, config: ProviderConfig, client: httpx.AsyncClient | None = None) -> None:
        self.config = config
        self._client = client or httpx.AsyncClient(timeout=config.timeout_seconds)

    async def invoke(self, request: LLMRequest) -> LLMResponse:
        """Handle invoke."""
        model = request.model or self.config.model
        messages = [{"role": m.role, "content": to_provider_text(m.content)} for m in request.messages]
        options = dict(request.params)
        if request.max_tokens is not None and "num_predict" not in options:
            options["num_predict"] = int(request.max_tokens)

        body = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": options,
        }
        try:
            resp = await self._client.post(f"{self.config.base_url.rstrip('/')}/api/chat", json=body)
        except httpx.HTTPError as exc:
            raise ProviderUnavailableError(str(exc)) from exc

        if resp.status_code >= 400:
            raise InvalidRequestError(f"Ollama chat failed with {resp.status_code}")

        data = resp.json()
        message = data.get("message") or {}
        content = str(message.get("content") or "")
        thinking = str(message.get("thinking") or "")
        if thinking and not content:
            content = thinking

        return LLMResponse(
            request_id=uuid.uuid4().hex,
            provider_id=self.config.provider_id,
            model_id=model,
            content=content,
            raw_provider_response=data,
        )

    async def invoke_stream(self, request: LLMRequest) -> AsyncIterator[LLMEvent]:
        """Handle invoke stream."""
        model = request.model or self.config.model
        messages = [{"role": m.role, "content": to_provider_text(m.content)} for m in request.messages]
        options = dict(request.params)
        if request.max_tokens is not None and "num_predict" not in options:
            options["num_predict"] = int(request.max_tokens)
        body = {
            "model": model,
            "messages": messages,
            "stream": True,
            "options": options,
        }
        request_id = uuid.uuid4().hex
        yield LLMEvent(
            type=EventType.RESPONSE_STARTED,
            request_id=request_id,
            provider_id=self.config.provider_id,
            model_id=model,
        )
        try:
            async with self._client.stream("POST", f"{self.config.base_url.rstrip('/')}/api/chat", json=body) as resp:
                if resp.status_code >= 400:
                    raise InvalidRequestError(f"Ollama stream failed with {resp.status_code}")
                async for line in resp.aiter_lines():
                    s = line.strip()
                    if not s:
                        continue
                    try:
                        data = json.loads(s)
                    except json.JSONDecodeError:
                        continue
                    msg = data.get("message") or {}
                    text = str(msg.get("content") or "")
                    if text:
                        yield LLMEvent(
                            type=EventType.DELTA_TEXT,
                            request_id=request_id,
                            provider_id=self.config.provider_id,
                            model_id=model,
                            text=text,
                        )
        except httpx.HTTPError as exc:
            raise ProviderUnavailableError(str(exc)) from exc
        yield LLMEvent(
            type=EventType.RESPONSE_COMPLETED,
            request_id=request_id,
            provider_id=self.config.provider_id,
            model_id=model,
        )

    async def embeddings(self, texts: list[str], *, model: str | None = None) -> list[list[float]]:
        """Handle embeddings."""
        out: list[list[float]] = []
        target_model = model or self.config.model
        for text in texts:
            resp = await self._client.post(
                f"{self.config.base_url.rstrip('/')}/api/embeddings",
                json={"model": target_model, "prompt": text},
            )
            if resp.status_code >= 400:
                raise InvalidRequestError(f"Ollama embeddings failed with {resp.status_code}")
            emb = resp.json().get("embedding") or []
            out.append([float(x) for x in emb])
        return out

    async def health(self) -> bool:
        """Handle health."""
        try:
            resp = await self._client.get(f"{self.config.base_url.rstrip('/')}/api/tags")
            return resp.status_code == 200
        except Exception:
            return False

    def capabilities(self) -> CapabilityDescriptor:
        """Handle capabilities."""
        return CapabilityDescriptor(
            provider_id=self.config.provider_id,
            model_id=self.config.model,
            chat=True,
            tool_calling=False,
            json_mode=False,
            embeddings=True,
            supports_streaming=True,
        )
