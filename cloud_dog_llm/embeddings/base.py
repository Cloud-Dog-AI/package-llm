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

# cloud_dog_llm — Embedding provider interface
"""Embedding provider protocol."""

from __future__ import annotations

from typing import Protocol


class EmbeddingProvider(Protocol):
    """Represent embedding provider."""

    async def embeddings(self, texts: list[str], *, model: str | None = None) -> list[list[float]]:
        """Generate embeddings for the supplied texts."""
        ...

    async def dimensions(self, *, model: str | None = None) -> int | None:
        """Return the embedding dimensionality for the model when known."""
        _ = model
        return None
