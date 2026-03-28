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

# cloud_dog_llm — OpenAI-compatible provider adapter
"""Adapter for OpenAI-compatible chat/completions and embeddings APIs."""

from __future__ import annotations

import time
import uuid
import json
from collections.abc import AsyncIterator
from typing import Any

import httpx

from cloud_dog_llm.config.models import ProviderConfig
from cloud_dog_llm.domain.enums import EventType
from cloud_dog_llm.domain.errors import AuthError, InvalidRequestError, ProviderUnavailableError, RateLimitError
from cloud_dog_llm.domain.models import LLMEvent, LLMRequest, LLMResponse, Usage
from cloud_dog_llm.multimodal.handler import to_provider_text
from cloud_dog_llm.providers.base import ProviderAdapter
from cloud_dog_llm.registry.capabilities import CapabilityDescriptor


class OpenAICompatAdapter(ProviderAdapter):
    """Represent open a i compat adapter."""
    def __init__(self, config: ProviderConfig, client: httpx.AsyncClient | None = None) -> None:
        self.config = config
        self._client = client or httpx.AsyncClient(timeout=config.timeout_seconds)

    def _headers(self) -> dict[str, str]:
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"
        if self.config.extra_headers:
            headers.update(self.config.extra_headers)
        return headers

    async def invoke(self, request: LLMRequest) -> LLMResponse:
        """Handle invoke."""
        body = {
            "model": request.model or self.config.model,
            "messages": [{"role": m.role, "content": to_provider_text(m.content)} for m in request.messages],
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
            **request.params,
        }
        # Remove None values for provider compatibility.
        body = {k: v for k, v in body.items() if v is not None}

        t0 = time.perf_counter()
        try:
            resp = await self._client.post(
                f"{self.config.base_url.rstrip('/')}/chat/completions",
                headers=self._headers(),
                json=body,
            )
        except httpx.HTTPError as exc:
            raise ProviderUnavailableError(str(exc)) from exc

        if resp.status_code == 401:
            raise AuthError("Provider authentication failed")
        if resp.status_code == 429:
            raise RateLimitError("Provider rate limit exceeded")
        if resp.status_code >= 400:
            raise InvalidRequestError(f"Provider request failed with {resp.status_code}")

        data = resp.json()
        choice = (data.get("choices") or [{}])[0]
        msg = choice.get("message") or {}
        usage = data.get("usage") or {}
        content = str(msg.get("content") or "")
        if not content:
            content = str(msg.get("reasoning") or "")

        _elapsed_ms = (time.perf_counter() - t0) * 1000
        return LLMResponse(
            request_id=data.get("id") or uuid.uuid4().hex,
            provider_id=self.config.provider_id,
            model_id=str(data.get("model") or body["model"]),
            content=content,
            usage=Usage(
                prompt_tokens=int(usage.get("prompt_tokens") or 0),
                completion_tokens=int(usage.get("completion_tokens") or 0),
                total_tokens=int(usage.get("total_tokens") or 0),
            ),
            raw_provider_response=data,
        )

    async def invoke_stream(self, request: LLMRequest) -> AsyncIterator[LLMEvent]:
        """Handle invoke stream."""
        body = {
            "model": request.model or self.config.model,
            "messages": [{"role": m.role, "content": to_provider_text(m.content)} for m in request.messages],
            "temperature": request.temperature,
            "max_tokens": request.max_tokens,
            "stream": True,
            **request.params,
        }
        body = {k: v for k, v in body.items() if v is not None}
        request_id = uuid.uuid4().hex
        yield LLMEvent(
            type=EventType.RESPONSE_STARTED,
            request_id=request_id,
            provider_id=self.config.provider_id,
            model_id=str(body["model"]),
        )
        async with self._client.stream(
            "POST",
            f"{self.config.base_url.rstrip('/')}/chat/completions",
            headers=self._headers(),
            json=body,
        ) as resp:
            if resp.status_code >= 400:
                raise InvalidRequestError(f"Provider stream request failed with {resp.status_code}")
            async for line in resp.aiter_lines():
                s = line.strip()
                if not s.startswith("data:"):
                    continue
                payload = s[5:].strip()
                if payload == "[DONE]":
                    break
                try:
                    data = json.loads(payload)
                except json.JSONDecodeError:
                    continue
                choice = (data.get("choices") or [{}])[0]
                delta = choice.get("delta") or {}
                text = str(delta.get("content") or "")
                if text:
                    yield LLMEvent(
                        type=EventType.DELTA_TEXT,
                        request_id=request_id,
                        provider_id=self.config.provider_id,
                        model_id=str(body["model"]),
                        text=text,
                    )
        yield LLMEvent(
            type=EventType.RESPONSE_COMPLETED,
            request_id=request_id,
            provider_id=self.config.provider_id,
            model_id=str(body["model"]),
        )

    async def embeddings(self, texts: list[str], *, model: str | None = None) -> list[list[float]]:
        """Handle embeddings."""
        body: dict[str, Any] = {
            "model": model or self.config.model,
            "input": texts,
        }
        resp = await self._client.post(
            f"{self.config.base_url.rstrip('/')}/embeddings",
            headers=self._headers(),
            json=body,
        )
        if resp.status_code >= 400:
            raise InvalidRequestError(f"Embedding request failed with {resp.status_code}")
        data = resp.json()
        out: list[list[float]] = []
        for item in data.get("data", []):
            emb = item.get("embedding") or []
            out.append([float(x) for x in emb])
        return out

    async def health(self) -> bool:
        """Handle health."""
        try:
            resp = await self._client.get(f"{self.config.base_url.rstrip('/')}/models", headers=self._headers())
            return resp.status_code < 500
        except Exception:
            return False

    def capabilities(self) -> CapabilityDescriptor:
        """Handle capabilities."""
        return CapabilityDescriptor(
            provider_id=self.config.provider_id,
            model_id=self.config.model,
            chat=True,
            tool_calling=True,
            json_mode=True,
            embeddings=True,
            supports_streaming=True,
        )
