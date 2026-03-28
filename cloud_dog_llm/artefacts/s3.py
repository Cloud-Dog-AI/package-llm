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

from pathlib import Path

from cloud_dog_llm.artefacts.local import LocalArtefactStore


class S3ArtefactStore(LocalArtefactStore):
    """S3-compatible store surface backed by local filesystem in tests.

    The public API mirrors a bucket/key style without introducing a hard
    runtime dependency on boto3 for local and unit-test execution.
    """

    def __init__(self, bucket: str, prefix: str = "", root: str = ".artefacts_s3") -> None:
        self.bucket = bucket
        self.prefix = prefix.strip("/")
        path = Path(root) / bucket
        if self.prefix:
            path = path / self.prefix
        super().__init__(str(path))
