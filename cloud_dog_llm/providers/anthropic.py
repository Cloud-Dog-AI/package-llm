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

# cloud_dog_llm — Anthropic provider adapter
"""Adapter for Anthropic Messages API with streaming support."""

from __future__ import annotations

import json
import uuid
from collections.abc import AsyncIterator

import httpx

from cloud_dog_llm.config.models import ProviderConfig
from cloud_dog_llm.domain.enums import EventType
from cloud_dog_llm.domain.errors import AuthError, InvalidRequestError, ProviderUnavailableError, RateLimitError
from cloud_dog_llm.domain.models import LLMEvent, LLMRequest, LLMResponse, Usage
from cloud_dog_llm.providers.base import ProviderAdapter
from cloud_dog_llm.registry.capabilities import CapabilityDescriptor


class AnthropicAdapter(ProviderAdapter):
    """Anthropic Messages API adapter.

    The adapter targets `/v1/messages` and maps the platform request model to
    Anthropic's expected payload. Streaming supports `content_block_delta`
    events that carry text deltas.
    """

    def __init__(self, config: ProviderConfig, client: httpx.AsyncClient | None = None) -> None:
        self.config = config
        self._client = client or httpx.AsyncClient(timeout=config.timeout_seconds)

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json", "anthropic-version": "2023-06-01"}
        if self.config.api_key:
            headers["x-api-key"] = self.config.api_key
        if self.config.extra_headers:
            headers.update(self.config.extra_headers)
        return headers

    def _messages_payload(self, request: LLMRequest) -> list[dict[str, str]]:
        return [{"role": m.role, "content": m.content} for m in request.messages]

    async def invoke(self, request: LLMRequest) -> LLMResponse:
        """Handle invoke."""
        model = request.model or self.config.model
        body: dict[str, object] = {
            "model": model,
            "messages": self._messages_payload(request),
            "max_tokens": int(request.max_tokens or 1024),
            **request.params,
        }
        if request.temperature is not None:
            body["temperature"] = request.temperature

        try:
            resp = await self._client.post(
                f"{self.config.base_url.rstrip('/')}/v1/messages", headers=self._headers(), json=body
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
        parts = data.get("content") or []
        text_chunks = [str(p.get("text") or "") for p in parts if isinstance(p, dict)]
        usage = data.get("usage") or {}

        return LLMResponse(
            request_id=str(data.get("id") or uuid.uuid4().hex),
            provider_id=self.config.provider_id,
            model_id=str(data.get("model") or model),
            content="".join(text_chunks),
            usage=Usage(
                prompt_tokens=int(usage.get("input_tokens") or 0),
                completion_tokens=int(usage.get("output_tokens") or 0),
                total_tokens=int((usage.get("input_tokens") or 0) + (usage.get("output_tokens") or 0)),
            ),
            raw_provider_response=data,
        )

    async def invoke_stream(self, request: LLMRequest) -> AsyncIterator[LLMEvent]:
        """Handle invoke stream."""
        model = request.model or self.config.model
        body: dict[str, object] = {
            "model": model,
            "messages": self._messages_payload(request),
            "max_tokens": int(request.max_tokens or 1024),
            "stream": True,
            **request.params,
        }
        if request.temperature is not None:
            body["temperature"] = request.temperature

        request_id = uuid.uuid4().hex
        yield LLMEvent(
            type=EventType.RESPONSE_STARTED,
            request_id=request_id,
            provider_id=self.config.provider_id,
            model_id=model,
        )

        try:
            async with self._client.stream(
                "POST",
                f"{self.config.base_url.rstrip('/')}/v1/messages",
                headers=self._headers(),
                json=body,
            ) as resp:
                if resp.status_code >= 400:
                    raise InvalidRequestError(f"Provider stream request failed with {resp.status_code}")
                async for line in resp.aiter_lines():
                    text = line.strip()
                    if not text.startswith("data:"):
                        continue
                    payload = text[5:].strip()
                    if payload in ("", "[DONE]"):
                        continue
                    try:
                        event = json.loads(payload)
                    except json.JSONDecodeError:
                        continue
                    if event.get("type") == "content_block_delta":
                        delta = (event.get("delta") or {}).get("text") or ""
                        if delta:
                            yield LLMEvent(
                                type=EventType.DELTA_TEXT,
                                request_id=request_id,
                                provider_id=self.config.provider_id,
                                model_id=model,
                                text=str(delta),
                            )
        except httpx.HTTPError as exc:
            raise ProviderUnavailableError(str(exc)) from exc

        yield LLMEvent(
            type=EventType.RESPONSE_COMPLETED,
            request_id=request_id,
            provider_id=self.config.provider_id,
            model_id=model,
        )

    async def health(self) -> bool:
        """Handle health."""
        try:
            resp = await self._client.get(f"{self.config.base_url.rstrip('/')}/v1/models", headers=self._headers())
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
            embeddings=False,
            supports_streaming=True,
        )
