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

from cloud_dog_llm.tools.models import ToolCall
from cloud_dog_llm.tools.pipeline import ToolPipeline


@pytest.mark.asyncio
async def test_tool_pipeline_parallel_lifecycle() -> None:
    async def add(args: dict[str, int]) -> dict[str, int]:
        return {"value": args["a"] + args["b"]}

    pipe = ToolPipeline({"add": add}, max_concurrency=2)
    result = await pipe.run_parallel([ToolCall("add", "add", {"a": 1, "b": 2})])
    assert result.results[0].success is True
    assert result.results[0].output["value"] == 3
    assert result.events[0].event == "tool_call_started"
