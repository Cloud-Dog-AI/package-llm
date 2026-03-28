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

# cloud_dog_llm — Streaming serialisation
"""Helpers for serialising stream events to SSE/JSONL."""

from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncIterator

from cloud_dog_llm.domain.models import LLMEvent


def to_jsonl(event: LLMEvent) -> str:
    """Handle to jsonl."""
    return json.dumps(
        {
            "type": event.type.value,
            "request_id": event.request_id,
            "provider_id": event.provider_id,
            "model_id": event.model_id,
            "text": event.text,
            "error": event.error,
        }
    )


def to_sse(event: LLMEvent) -> str:
    """Handle to sse."""
    return f"event: {event.type.value}\ndata: {to_jsonl(event)}\n\n"


class StreamBuffer:
    """Bounded async stream buffer with cancellation support."""

    def __init__(self, max_events: int = 128) -> None:
        self._queue: asyncio.Queue[LLMEvent | None] = asyncio.Queue(maxsize=max_events)
        self._cancelled = False

    async def push(self, event: LLMEvent) -> None:
        """Handle push."""
        if self._cancelled:
            return
        await self._queue.put(event)

    async def close(self) -> None:
        """Handle close."""
        if self._queue.full():
            try:
                self._queue.get_nowait()
            except asyncio.QueueEmpty:
                pass
        await self._queue.put(None)

    def cancel(self) -> None:
        """Handle cancel."""
        self._cancelled = True

    async def events(self) -> AsyncIterator[LLMEvent]:
        """Handle events."""
        while True:
            item = await self._queue.get()
            if item is None:
                return
            yield item
