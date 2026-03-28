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

# cloud_dog_llm — Provider adapter interface
"""Abstract base class for pluggable LLM provider adapters."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator

from cloud_dog_llm.domain.models import LLMEvent, LLMRequest, LLMResponse
from cloud_dog_llm.registry.capabilities import CapabilityDescriptor


class ProviderAdapter(ABC):
    """Define the interface implemented by provider adapters."""

    @abstractmethod
    async def invoke(self, request: LLMRequest) -> LLMResponse:
        """Invoke the provider for a single non-streaming request."""
        raise NotImplementedError

    @abstractmethod
    async def invoke_stream(self, request: LLMRequest) -> AsyncIterator[LLMEvent]:
        """Stream provider events for the supplied request."""
        raise NotImplementedError

    @abstractmethod
    async def health(self) -> bool:
        """Return whether the provider is healthy."""
        raise NotImplementedError

    @abstractmethod
    def capabilities(self) -> CapabilityDescriptor:
        """Return the provider capability descriptor."""
        raise NotImplementedError
