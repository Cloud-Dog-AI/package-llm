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

# cloud_dog_llm — Response-shape compatibility adapter
"""Normalise provider-specific payloads into unified ``LLMResponse``."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any

from cloud_dog_llm.domain.enums import FinishReason
from cloud_dog_llm.domain.models import LLMResponse, Usage


class ResponseNormalisationError(ValueError):
    """Raised when a payload cannot be normalised for the selected provider."""


@dataclass(frozen=True, slots=True)
class ProviderMapping:
    """Represent provider mapping."""
    content_path: str
    model_path: str
    request_id_path: str
    finish_reason_path: str | None = None
    usage_prompt_path: str | None = None
    usage_completion_path: str | None = None
    usage_total_path: str | None = None


def _extract_path(payload: Any, path: str | None) -> Any:
    if not path:
        return None
    current: Any = payload
    for part in path.split("."):
        if isinstance(current, list):
            if not part.isdigit():
                return None
            idx = int(part)
            if idx >= len(current):
                return None
            current = current[idx]
            continue
        if isinstance(current, dict):
            current = current.get(part)
            continue
        return None
    return current


def _to_finish_reason(value: Any) -> FinishReason:
    text = str(value or "").lower().strip()
    if text in ("stop", "end_turn"):
        return FinishReason.STOP
    if text in ("length", "max_tokens"):
        return FinishReason.LENGTH
    if text in ("tool_calls", "tool_use"):
        return FinishReason.TOOL_CALLS
    if text in ("error", "failed"):
        return FinishReason.ERROR
    return FinishReason.STOP


class ResponseAdapter:
    """Adapter that translates provider-specific response payloads to ``LLMResponse``."""

    def __init__(self, mappings: dict[str, ProviderMapping] | None = None) -> None:
        base = {
            "ollama": ProviderMapping(
                content_path="message.content",
                model_path="model",
                request_id_path="id",
                finish_reason_path="done_reason",
                usage_prompt_path="prompt_eval_count",
                usage_completion_path="eval_count",
            ),
            "openrouter": ProviderMapping(
                content_path="choices.0.message.content",
                model_path="model",
                request_id_path="id",
                finish_reason_path="choices.0.finish_reason",
                usage_prompt_path="usage.prompt_tokens",
                usage_completion_path="usage.completion_tokens",
                usage_total_path="usage.total_tokens",
            ),
            "openai": ProviderMapping(
                content_path="choices.0.message.content",
                model_path="model",
                request_id_path="id",
                finish_reason_path="choices.0.finish_reason",
                usage_prompt_path="usage.prompt_tokens",
                usage_completion_path="usage.completion_tokens",
                usage_total_path="usage.total_tokens",
            ),
            "openai_compat": ProviderMapping(
                content_path="choices.0.message.content",
                model_path="model",
                request_id_path="id",
                finish_reason_path="choices.0.finish_reason",
                usage_prompt_path="usage.prompt_tokens",
                usage_completion_path="usage.completion_tokens",
                usage_total_path="usage.total_tokens",
            ),
            "anthropic": ProviderMapping(
                content_path="content.0.text",
                model_path="model",
                request_id_path="id",
                finish_reason_path="stop_reason",
                usage_prompt_path="usage.input_tokens",
                usage_completion_path="usage.output_tokens",
            ),
        }
        if mappings:
            base.update(mappings)
        self._mappings = base

    def normalise(
        self, provider_id: str, payload: dict[str, Any], *, fallback_model_id: str = "unknown"
    ) -> LLMResponse:
        """Handle normalise."""
        if provider_id not in self._mappings:
            raise ResponseNormalisationError(f"Unsupported provider response shape: {provider_id}")

        mapping = self._mappings[provider_id]
        content = _extract_path(payload, mapping.content_path)
        if provider_id == "anthropic" and not content:
            # Anthropic can return an array of content blocks.
            blocks = payload.get("content") if isinstance(payload, dict) else None
            if isinstance(blocks, list):
                content = "".join(str((b or {}).get("text") or "") for b in blocks if isinstance(b, dict))
        if content is None:
            raise ResponseNormalisationError(f"Missing content in provider response: {provider_id}")

        model_id = str(_extract_path(payload, mapping.model_path) or fallback_model_id)
        request_id = str(_extract_path(payload, mapping.request_id_path) or uuid.uuid4().hex)

        prompt_tokens = int(_extract_path(payload, mapping.usage_prompt_path) or 0)
        completion_tokens = int(_extract_path(payload, mapping.usage_completion_path) or 0)
        total_tokens_raw = _extract_path(payload, mapping.usage_total_path)
        total_tokens = int(total_tokens_raw) if total_tokens_raw is not None else prompt_tokens + completion_tokens

        return LLMResponse(
            request_id=request_id,
            provider_id=provider_id,
            model_id=model_id,
            content=str(content),
            finish_reason=_to_finish_reason(_extract_path(payload, mapping.finish_reason_path)),
            usage=Usage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=total_tokens,
            ),
            raw_provider_response=payload,
        )
