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

# cloud_dog_llm — Model registry
"""Simple registry for model capability descriptors."""

from __future__ import annotations

from cloud_dog_llm.registry.capabilities import CapabilityDescriptor


class ModelRegistry:
    """Represent model registry."""
    def __init__(self) -> None:
        self._models: dict[str, CapabilityDescriptor] = {}

    def register(self, model_id: str, descriptor: CapabilityDescriptor) -> None:
        """Handle register."""
        self._models[model_id] = descriptor

    def get(self, model_id: str) -> CapabilityDescriptor | None:
        """Handle get."""
        return self._models.get(model_id)

    def get_capabilities(self, model_id: str) -> CapabilityDescriptor:
        """Return capabilities."""
        found = self._models.get(model_id)
        if found is not None:
            return found
        return CapabilityDescriptor(
            provider_id="unknown",
            model_id=model_id,
            chat=False,
            streaming=False,
            tool_calling=False,
            structured_output=False,
            vision=False,
            json_mode=False,
            embeddings=False,
            max_tokens=None,
            context_window=0,
        )

    def validate_params(self, model_id: str, params: dict[str, object]) -> list[str]:
        """Validate params."""
        caps = self.get_capabilities(model_id)
        errors: list[str] = []
        if "response_format" in params and not (caps.structured_output or caps.json_mode):
            errors.append("response_format not supported by model")
        if "tools" in params and not caps.tool_calling:
            errors.append("tool calling not supported by model")
        return errors

    def all(self) -> list[CapabilityDescriptor]:
        """Handle all."""
        return list(self._models.values())
