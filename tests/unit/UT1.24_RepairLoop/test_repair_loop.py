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

from cloud_dog_llm.structured.repair import repair_json


def test_repair_loop_bounded_retries() -> None:
    attempts = {"n": 0}

    def repair(_: str) -> str:
        attempts["n"] += 1
        return '{"status":"ok"}' if attempts["n"] == 2 else "still bad"

    out = repair_json("bad", repair, max_retries=3)
    assert out is not None
    assert out["status"] == "ok"
