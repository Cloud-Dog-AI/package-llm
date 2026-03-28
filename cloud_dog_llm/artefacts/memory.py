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

from cloud_dog_llm.artefacts.store import InMemoryArtefactStore


class MemoryArtefactStore(InMemoryArtefactStore):
    """In-memory store with convenience maintenance helpers."""

    def list_ids(self) -> list[str]:
        """List ids."""
        return sorted(self._meta.keys())  # type: ignore[attr-defined]

    def purge_expired(self) -> int:
        """Handle purge expired."""
        now_ids = list(self.list_ids())
        removed = 0
        for artefact_id in now_ids:
            loaded = self.get(artefact_id)
            if loaded is None:
                self._meta.pop(artefact_id, None)  # type: ignore[attr-defined]
                self._data.pop(artefact_id, None)  # type: ignore[attr-defined]
                removed += 1
        return removed
