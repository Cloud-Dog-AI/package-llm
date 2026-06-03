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

# cloud_dog_llm — Runtime response helpers
"""Helpers for constructing unified LLMResponse objects."""

from __future__ import annotations

import uuid
from typing import Any

from cloud_dog_llm.domain.enums import FinishReason
from cloud_dog_llm.domain.models import LLMResponse, Usage


def build_response(
    *,
    provider_id: str,
    model_id: str,
    content: str,
    request_id: str | None = None,
    usage: Usage | None = None,
    finish_reason: FinishReason = FinishReason.STOP,
    raw_provider_response: dict[str, Any] | None = None,
) -> LLMResponse:
    """Build response."""
    return LLMResponse(
        request_id=request_id or uuid.uuid4().hex,
        provider_id=provider_id,
        model_id=model_id,
        content=content,
        usage=usage or Usage(),
        finish_reason=finish_reason,
        raw_provider_response=raw_provider_response,
    )
