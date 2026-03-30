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

# cloud_dog_llm — Tool models
"""Tool definition and call/result models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from cloud_dog_llm.domain.enums import ExecutionMode


@dataclass(frozen=True, slots=True)
class ToolDef:
    """Represent tool def."""
    tool_id: str
    name: str
    description: str
    input_schema: dict[str, Any]
    output_schema: dict[str, Any] = field(default_factory=dict)
    execution_mode: ExecutionMode = ExecutionMode.LOCAL


@dataclass(frozen=True, slots=True)
class ToolCall:
    """Represent tool call."""
    tool_id: str
    name: str
    arguments: dict[str, Any]


@dataclass(frozen=True, slots=True)
class ToolResult:
    """Represent tool result."""
    tool_id: str
    success: bool
    output: dict[str, Any]
    error: str = ""
