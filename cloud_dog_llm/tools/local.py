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

from collections.abc import Awaitable, Callable
from typing import Any

LocalToolHandler = Callable[[dict[str, Any]], Awaitable[dict[str, Any]]]


class LocalToolRegistry:
    """Represent local tool registry."""
    def __init__(self) -> None:
        self._handlers: dict[str, LocalToolHandler] = {}

    def register(self, tool_id: str, handler: LocalToolHandler) -> None:
        """Handle register."""
        self._handlers[tool_id] = handler

    async def execute(self, tool_id: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """Handle execute."""
        if tool_id not in self._handlers:
            raise KeyError(f"Local tool not found: {tool_id}")
        return await self._handlers[tool_id](arguments)
