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

# cloud_dog_llm — Cancellation helpers
"""Small cancellation primitives for tests and integrations."""

from __future__ import annotations

import asyncio


class CancellationToken:
    """Represent cancellation token."""
    def __init__(self) -> None:
        self._event = asyncio.Event()

    def cancel(self) -> None:
        """Handle cancel."""
        self._event.set()

    async def wait_cancelled(self) -> None:
        """Handle wait cancelled."""
        await self._event.wait()

    @property
    def cancelled(self) -> bool:
        """Handle cancelled."""
        return self._event.is_set()
