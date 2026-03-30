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

# cloud_dog_llm — In-memory artefact store
"""Minimal provider-agnostic artefact store for tests and local use."""

from __future__ import annotations

import hashlib
import time
import uuid
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Artefact:
    """Represent artefact."""
    artefact_id: str
    filename: str
    mime_type: str
    size: int
    sha256: str
    created_at: float
    expires_at: float | None
    owner: str | None


class InMemoryArtefactStore:
    """Represent in memory artefact store."""
    def __init__(self) -> None:
        self._meta: dict[str, Artefact] = {}
        self._data: dict[str, bytes] = {}

    def put(
        self, content: bytes, *, filename: str, mime_type: str, owner: str | None = None, ttl_seconds: int | None = None
    ) -> Artefact:
        """Handle put."""
        artefact_id = uuid.uuid4().hex
        now = time.time()
        expires_at = now + ttl_seconds if ttl_seconds else None
        sha = hashlib.sha256(content).hexdigest()
        artefact = Artefact(
            artefact_id=artefact_id,
            filename=filename,
            mime_type=mime_type,
            size=len(content),
            sha256=sha,
            created_at=now,
            expires_at=expires_at,
            owner=owner,
        )
        self._meta[artefact_id] = artefact
        self._data[artefact_id] = content
        return artefact

    def get(self, artefact_id: str) -> tuple[Artefact, bytes] | None:
        """Handle get."""
        artefact = self._meta.get(artefact_id)
        data = self._data.get(artefact_id)
        if artefact is None or data is None:
            return None
        if artefact.expires_at and artefact.expires_at < time.time():
            return None
        return artefact, data
