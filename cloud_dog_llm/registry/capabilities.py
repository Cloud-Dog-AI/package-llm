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

# cloud_dog_llm — Capability descriptor
"""Model capability descriptors used by registry and adapters."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CapabilityDescriptor:
    """Represent capability descriptor."""
    provider_id: str
    model_id: str
    chat: bool = True
    streaming: bool = True
    tool_calling: bool = False
    structured_output: bool = False
    vision: bool = False
    json_mode: bool = False
    embeddings: bool = False
    max_tokens: int | None = None
    context_window: int = 0
    supports_streaming: bool | None = None

    def __post_init__(self) -> None:
        if self.supports_streaming is None:
            object.__setattr__(self, "supports_streaming", self.streaming)
        else:
            object.__setattr__(self, "streaming", bool(self.supports_streaming))
