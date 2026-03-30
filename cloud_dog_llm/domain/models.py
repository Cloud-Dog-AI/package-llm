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

# cloud_dog_llm — Domain models
"""Portable request/response/session/tool models for PS-50."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from cloud_dog_llm.domain.enums import EventType, FinishReason


@dataclass(frozen=True, slots=True)
class SessionContext:
    """Represent session context."""
    session_id: str
    correlation_id: str
    conversation_id: str | None = None
    user_id: str | None = None
    tenant_id: str | None = None


@dataclass(frozen=True, slots=True)
class Message:
    """Represent message."""
    role: str
    content: str | list[dict[str, Any]]


@dataclass(frozen=True, slots=True)
class LLMRequest:
    """Represent l l m request."""
    messages: list[Message]
    model: str | None = None
    provider_id: str | None = None
    temperature: float | None = None
    max_tokens: int | None = None
    stream: bool = False
    params: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class Usage:
    """Represent usage."""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


@dataclass(frozen=True, slots=True)
class LLMResponse:
    """Represent l l m response."""
    request_id: str
    provider_id: str
    model_id: str
    content: str
    tool_calls: list[dict[str, Any]] = field(default_factory=list)
    finish_reason: FinishReason = FinishReason.STOP
    usage: Usage = field(default_factory=Usage)
    timing: dict[str, float] = field(default_factory=dict)
    raw_provider_response: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class LLMEvent:
    """Represent l l m event."""
    type: EventType
    request_id: str
    provider_id: str
    model_id: str
    text: str = ""
    error: str = ""
