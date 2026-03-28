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

import pytest

from cloud_dog_llm.embeddings.manager import EmbeddingManager


class FakeEmbeddingProvider:
    async def embeddings(self, texts: list[str], *, model: str | None = None) -> list[list[float]]:
        _ = model
        return [[float(len(t))] for t in texts]


@pytest.mark.asyncio
async def test_embedding_manager_batch() -> None:
    manager = EmbeddingManager(FakeEmbeddingProvider(), model="embed")
    out = await manager.generate_embeddings(["a", "abcd"])
    assert out == [[1.0], [4.0]]
