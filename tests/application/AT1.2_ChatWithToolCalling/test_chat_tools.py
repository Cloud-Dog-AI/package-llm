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

import pytest

from cloud_dog_llm.tools.calling import parse_json_tool_call
from cloud_dog_llm.tools.models import ToolCall, ToolDef
from cloud_dog_llm.tools.router import ToolRouter


@pytest.mark.asyncio
async def test_application_chat_with_tool_calling_pattern() -> None:
    async def echo(args: dict[str, str]) -> dict[str, str]:
        return {"value": str(args.get("value", ""))}

    router = ToolRouter()
    router.register(ToolDef("echo", "echo", "echo", {"type": "object"}), echo)

    parsed = parse_json_tool_call('{"tool":"echo","arguments":{"value":"ok"}}')
    assert parsed is not None
    result = await router.route(ToolCall(parsed.tool_id, parsed.name, parsed.arguments))
    assert result.success is True
    assert result.output["value"] == "ok"
