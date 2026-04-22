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

from collections.abc import AsyncIterator

from cloud_dog_llm.domain.enums import EventType
from cloud_dog_llm.domain.models import LLMEvent, LLMRequest, LLMResponse
from cloud_dog_llm.providers.base import ProviderAdapter
from cloud_dog_llm.registry.capabilities import CapabilityDescriptor


class MockProvider(ProviderAdapter):
    """Represent mock provider."""
    async def invoke(self, request: LLMRequest) -> LLMResponse:
        """Handle invoke."""
        return LLMResponse(request_id="r1", provider_id="mock", model_id=request.model or "mock", content="ok")

    async def invoke_stream(self, request: LLMRequest) -> AsyncIterator[LLMEvent]:
        """Handle invoke stream."""
        yield LLMEvent(EventType.RESPONSE_STARTED, "r1", "mock", request.model or "mock")
        yield LLMEvent(EventType.DELTA_TEXT, "r1", "mock", request.model or "mock", text="ok")
        yield LLMEvent(EventType.RESPONSE_COMPLETED, "r1", "mock", request.model or "mock")

    async def health(self) -> bool:
        """Handle health."""
        return True

    def capabilities(self) -> CapabilityDescriptor:
        """Handle capabilities."""
        return CapabilityDescriptor(provider_id="mock", model_id="mock")
