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

from cloud_dog_llm.artefacts.memory import MemoryArtefactStore
from cloud_dog_llm.artefacts.s3 import S3ArtefactStore
from cloud_dog_llm.artefacts.store import InMemoryArtefactStore


def test_in_memory_artefact_store_roundtrip() -> None:
    store = InMemoryArtefactStore()
    meta = store.put(b"abc", filename="a.txt", mime_type="text/plain", owner="u1")
    loaded = store.get(meta.artefact_id)
    assert loaded is not None
    loaded_meta, loaded_bytes = loaded
    assert loaded_meta.size == 3
    assert loaded_bytes == b"abc"


def test_memory_artefact_store_helpers() -> None:
    store = MemoryArtefactStore()
    meta = store.put(b"x", filename="b.txt", mime_type="text/plain")
    assert meta.artefact_id in store.list_ids()
    assert store.purge_expired() == 0


def test_s3_artefact_store_local_backing(tmp_path) -> None:
    store = S3ArtefactStore(bucket="b1", prefix="p1", root=str(tmp_path))
    meta = store.put(b"123", filename="c.txt", mime_type="text/plain")
    loaded = store.get(meta.artefact_id)
    assert loaded is not None
    assert loaded[1] == b"123"
