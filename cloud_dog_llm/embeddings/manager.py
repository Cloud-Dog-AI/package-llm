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

# cloud_dog_llm — Embedding manager
"""Unified embedding manager over a provider adapter."""

from __future__ import annotations

from cloud_dog_llm.embeddings.base import EmbeddingProvider


class EmbeddingManager:
    """Represent embedding manager."""
    def __init__(self, provider: EmbeddingProvider, model: str | None = None) -> None:
        self._provider = provider
        self._model = model

    async def generate_embedding(self, text: str) -> list[float]:
        """Handle generate embedding."""
        return (await self._provider.embeddings([text], model=self._model))[0]

    async def generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        """Handle generate embeddings."""
        return await self._provider.embeddings(texts, model=self._model)
