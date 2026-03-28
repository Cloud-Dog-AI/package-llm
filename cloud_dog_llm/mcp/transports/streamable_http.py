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

from typing import Any

import httpx


class StreamableHTTPTransport:
    """Represent streamable h t t p transport."""
    def __init__(self, base_url: str, client: httpx.AsyncClient, headers: dict[str, str]) -> None:
        self.base_url = base_url.rstrip("/")
        self._client = client
        self._headers = headers

    async def send(self, payload: dict[str, Any]) -> dict[str, Any]:
        """Handle send."""
        resp = await self._client.post(f"{self.base_url}/messages", headers=self._headers, json=payload)
        resp.raise_for_status()
        return resp.json()
