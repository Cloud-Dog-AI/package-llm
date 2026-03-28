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

# cloud_dog_llm — Tool executor
"""Single-call and batch tool execution helpers."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from cloud_dog_llm.tools.models import ToolCall, ToolResult
from cloud_dog_llm.tools.pipeline import ToolPipeline

ToolHandler = Callable[[dict[str, Any]], Awaitable[dict[str, Any]]]


class ToolExecutor:
    """Executes tool calls using the shared ToolPipeline implementation."""

    def __init__(self, handlers: dict[str, ToolHandler], max_concurrency: int = 4) -> None:
        self._pipeline = ToolPipeline(handlers=handlers, max_concurrency=max_concurrency)

    async def execute(self, call: ToolCall) -> ToolResult:
        """Handle execute."""
        result = await self._pipeline.run_sequential([call])
        return result.results[0]

    async def execute_many(self, calls: list[ToolCall], *, parallel: bool = True) -> list[ToolResult]:
        """Handle execute many."""
        result = await (self._pipeline.run_parallel(calls) if parallel else self._pipeline.run_sequential(calls))
        return result.results
