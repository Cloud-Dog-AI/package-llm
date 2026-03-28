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

# cloud_dog_llm — Tool execution pipeline
"""Sequential/parallel tool execution with lifecycle events."""

from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field
from typing import Any

from cloud_dog_llm.tools.models import ToolCall, ToolResult

ToolHandler = Callable[[dict[str, Any]], Awaitable[dict[str, Any]]]


@dataclass(slots=True)
class ToolLifecycleEvent:
    """Represent tool lifecycle event."""
    event: str
    tool_id: str
    error: str = ""


@dataclass(slots=True)
class PipelineResult:
    """Represent pipeline result."""
    results: list[ToolResult] = field(default_factory=list)
    events: list[ToolLifecycleEvent] = field(default_factory=list)


class ToolPipeline:
    """Represent tool pipeline."""
    def __init__(self, handlers: dict[str, ToolHandler], max_concurrency: int = 4) -> None:
        self._handlers = handlers
        self._sem = asyncio.Semaphore(max_concurrency)

    async def _run_one(self, call: ToolCall, out: PipelineResult) -> None:
        out.events.append(ToolLifecycleEvent(event="tool_call_started", tool_id=call.tool_id))
        if call.tool_id not in self._handlers:
            out.events.append(
                ToolLifecycleEvent(event="tool_call_failed", tool_id=call.tool_id, error="Tool not registered")
            )
            out.results.append(ToolResult(tool_id=call.tool_id, success=False, output={}, error="Tool not registered"))
            return
        try:
            async with self._sem:
                payload = await self._handlers[call.tool_id](call.arguments)
            out.events.append(ToolLifecycleEvent(event="tool_call_succeeded", tool_id=call.tool_id))
            out.results.append(ToolResult(tool_id=call.tool_id, success=True, output=payload))
        except asyncio.CancelledError:
            out.events.append(ToolLifecycleEvent(event="tool_call_cancelled", tool_id=call.tool_id))
            out.results.append(ToolResult(tool_id=call.tool_id, success=False, output={}, error="cancelled"))
            raise
        except Exception as exc:  # noqa: BLE001
            out.events.append(ToolLifecycleEvent(event="tool_call_failed", tool_id=call.tool_id, error=str(exc)))
            out.results.append(ToolResult(tool_id=call.tool_id, success=False, output={}, error=str(exc)))

    async def run_sequential(self, calls: list[ToolCall]) -> PipelineResult:
        """Run sequential."""
        out = PipelineResult()
        for call in calls:
            await self._run_one(call, out)
        return out

    async def run_parallel(self, calls: list[ToolCall]) -> PipelineResult:
        """Run parallel."""
        out = PipelineResult()
        await asyncio.gather(*(self._run_one(call, out) for call in calls))
        return out
