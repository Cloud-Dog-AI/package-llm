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

from cloud_dog_llm.registry.capabilities import CapabilityDescriptor
from cloud_dog_llm.registry.registry import ModelRegistry


def test_get_capabilities_returns_descriptor_with_expected_fields() -> None:
    registry = ModelRegistry()
    registry.register(
        "qwen3",
        CapabilityDescriptor(
            provider_id="ollama",
            model_id="qwen3",
            streaming=True,
            tool_calling=True,
            structured_output=True,
            vision=False,
            embeddings=False,
            max_tokens=8192,
            context_window=32768,
        ),
    )

    caps = registry.get_capabilities("qwen3")
    assert caps.streaming is True
    assert caps.tool_calling is True
    assert caps.structured_output is True
    assert caps.max_tokens == 8192
    assert caps.context_window == 32768


def test_unknown_model_returns_safe_default() -> None:
    caps = ModelRegistry().get_capabilities("unknown-model")
    assert caps.model_id == "unknown-model"
    assert caps.chat is False
    assert caps.streaming is False


def test_capabilities_are_used_for_param_validation() -> None:
    registry = ModelRegistry()
    registry.register(
        "base",
        CapabilityDescriptor(provider_id="ollama", model_id="base", tool_calling=False, structured_output=False),
    )

    errors = registry.validate_params("base", {"response_format": {"type": "json_object"}, "tools": [{"x": 1}]})
    assert errors == ["response_format not supported by model", "tool calling not supported by model"]
