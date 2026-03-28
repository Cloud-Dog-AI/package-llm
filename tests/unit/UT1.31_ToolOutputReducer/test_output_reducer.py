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

from cloud_dog_llm.tools.reducer import reduce_output


def test_reduce_output_limits_fields_and_chars() -> None:
    payload = {"a": "x" * 20, "b": 2, "c": 3}
    out = reduce_output(payload, max_items=2, max_chars=5, fields=["a", "b", "c"])
    assert out["a"] == "xxxxx"
    assert "c" not in out
