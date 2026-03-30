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

from cloud_dog_llm.tools.calling import parse_json_tool_call, parse_openai_tool_calls


class ToolCallParser:
    """Unified parser wrapper for provider tool-call formats."""

    @staticmethod
    def from_openai_message(choice_message: dict) -> list:
        """Handle from openai message."""
        return parse_openai_tool_calls(choice_message)

    @staticmethod
    def from_text(text: str):
        """Handle from text."""
        return parse_json_tool_call(text)


__all__ = ["parse_json_tool_call", "parse_openai_tool_calls", "ToolCallParser"]
