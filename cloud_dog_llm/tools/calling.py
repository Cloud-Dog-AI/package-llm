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

# cloud_dog_llm — Tool calling parsers
"""Helpers for OpenAI-style and JSON-in-text tool-call extraction."""

from __future__ import annotations

import json
from typing import Any

from cloud_dog_llm.tools.models import ToolCall


def parse_openai_tool_calls(choice_message: dict[str, Any]) -> list[ToolCall]:
    """Parse openai tool calls."""
    out: list[ToolCall] = []
    for item in choice_message.get("tool_calls", []) or []:
        fn = item.get("function") or {}
        args_raw = fn.get("arguments") or "{}"
        try:
            args = json.loads(args_raw)
        except Exception:  # noqa: BLE001
            args = {}
        out.append(
            ToolCall(
                tool_id=str(item.get("id") or fn.get("name") or ""),
                name=str(fn.get("name") or ""),
                arguments=args if isinstance(args, dict) else {},
            )
        )
    return out


def parse_json_tool_call(text: str) -> ToolCall | None:
    """Parse json tool call."""
    decoder = json.JSONDecoder()

    def to_call(payload: dict[str, Any]) -> ToolCall | None:
        """Handle to call."""
        name = payload.get("tool") or payload.get("name")
        args = payload.get("arguments") or payload.get("args") or {}
        if name and isinstance(args, dict):
            return ToolCall(tool_id=str(name), name=str(name), arguments=args)
        return None

    def recursive_extract(payload: dict[str, Any]) -> ToolCall | None:
        """Handle recursive extract."""
        direct = to_call(payload)
        if direct is not None:
            return direct
        for value in payload.values():
            if isinstance(value, dict):
                nested = recursive_extract(value)
                if nested is not None:
                    return nested
            elif isinstance(value, str):
                nested = parse_json_tool_call(value)
                if nested is not None:
                    return nested
        return None

    idx = 0
    while idx < len(text):
        if text[idx] != "{":
            idx += 1
            continue
        try:
            obj, end = decoder.raw_decode(text[idx:])
        except json.JSONDecodeError:
            idx += 1
            continue
        if isinstance(obj, dict):
            call = recursive_extract(obj)
            if call is not None:
                return call
        idx += max(end, 1)
    return None
