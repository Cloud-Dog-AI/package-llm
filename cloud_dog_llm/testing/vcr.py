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

# cloud_dog_llm — Lightweight VCR recorder
"""Minimal cassette recorder/replayer for HTTP tests."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

import httpx


@dataclass(frozen=True, slots=True)
class RecordedExchange:
    """Represent recorded exchange."""
    method: str
    url: str
    request_body: str
    status_code: int
    response_body: str
    headers: dict[str, str]


class SimpleVCR:
    """Represent simple v c r."""
    def __init__(self, cassette_path: str) -> None:
        self.path = Path(cassette_path)
        self._records: list[RecordedExchange] = []
        if self.path.is_file():
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            self._records = [RecordedExchange(**item) for item in raw]

    def save(self) -> None:
        """Handle save."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        serialised = [asdict(r) for r in self._records]
        self.path.write_text(json.dumps(serialised, indent=2, sort_keys=True), encoding="utf-8")

    def replay(self, request: httpx.Request) -> httpx.Response | None:
        """Handle replay."""
        req_body = (request.content or b"").decode("utf-8", errors="replace")
        for item in self._records:
            if item.method == request.method and item.url == str(request.url) and item.request_body == req_body:
                return httpx.Response(
                    status_code=item.status_code,
                    headers=item.headers,
                    content=item.response_body.encode("utf-8"),
                    request=request,
                )
        return None

    def record(self, request: httpx.Request, response: httpx.Response) -> None:
        """Handle record."""
        req_body = (request.content or b"").decode("utf-8", errors="replace")
        resp_body = response.text
        self._records.append(
            RecordedExchange(
                method=request.method,
                url=str(request.url),
                request_body=req_body,
                status_code=response.status_code,
                response_body=resp_body,
                headers={k: v for k, v in response.headers.items()},
            )
        )
