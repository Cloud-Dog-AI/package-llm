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

# cloud_dog_llm — Domain enums
"""Core enums for the PS-50 domain model."""

from __future__ import annotations

from enum import Enum


class EventType(str, Enum):
    """Represent event type."""
    RESPONSE_STARTED = "response_started"
    DELTA_TEXT = "delta_text"
    DELTA_TOOL_CALL = "delta_tool_call"
    TOOL_CALL_STARTED = "tool_call_started"
    TOOL_CALL_RESULT = "tool_call_result"
    RESPONSE_COMPLETED = "response_completed"
    RESPONSE_ERROR = "response_error"


class FinishReason(str, Enum):
    """Represent finish reason."""
    STOP = "stop"
    LENGTH = "length"
    TOOL_CALLS = "tool_calls"
    ERROR = "error"


class ExecutionMode(str, Enum):
    """Represent execution mode."""
    LOCAL = "local"
    REMOTE = "remote"
    MCP = "mcp"
    A2A = "a2a"
