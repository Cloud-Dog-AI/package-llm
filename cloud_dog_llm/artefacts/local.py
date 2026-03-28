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

import hashlib
import time
import uuid
from pathlib import Path

from cloud_dog_llm.artefacts.store import Artefact


class LocalArtefactStore:
    """Represent local artefact store."""
    def __init__(self, root: str) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def put(self, content: bytes, *, filename: str, mime_type: str) -> Artefact:
        """Handle put."""
        artefact_id = uuid.uuid4().hex
        path = self.root / f"{artefact_id}_{filename}"
        path.write_bytes(content)
        return Artefact(
            artefact_id=artefact_id,
            filename=filename,
            mime_type=mime_type,
            size=len(content),
            sha256=hashlib.sha256(content).hexdigest(),
            created_at=time.time(),
            expires_at=None,
            owner=None,
        )

    def get(self, artefact_id: str) -> tuple[Artefact, bytes] | None:
        """Handle get."""
        for f in self.root.glob(f"{artefact_id}_*"):
            b = f.read_bytes()
            meta = Artefact(
                artefact_id=artefact_id,
                filename=f.name.split("_", 1)[1],
                mime_type="application/octet-stream",
                size=len(b),
                sha256=hashlib.sha256(b).hexdigest(),
                created_at=f.stat().st_mtime,
                expires_at=None,
                owner=None,
            )
            return meta, b
        return None
