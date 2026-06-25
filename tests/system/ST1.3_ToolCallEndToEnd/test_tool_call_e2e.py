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
from cloud_dog_llm.tools.models import ToolDef
from cloud_dog_llm.tools.router import ToolRouter


@pytest.mark.asyncio
async def test_tool_call_end_to_end_json_text_to_router() -> None:
    async def add(args: dict[str, int]) -> dict[str, int]:
        return {"sum": args["a"] + args["b"]}

    router = ToolRouter()
    router.register(ToolDef("add", "add", "add", {"type": "object"}), add)
    call = parse_json_tool_call('{"tool":"add","arguments":{"a":2,"b":3}}')
    assert call is not None
    result = await router.route(call)
    assert result.success is True
    assert result.output["sum"] == 5
