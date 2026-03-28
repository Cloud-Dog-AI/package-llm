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

from cloud_dog_llm.structured.extractor import extract_json
from cloud_dog_llm.structured.schema import StructuredSchema
from cloud_dog_llm.structured.validator import validate_payload


def test_extract_json_from_text() -> None:
    payload = extract_json('text {"answer": 42, "ok": true} trailing')
    assert payload is not None
    assert payload["answer"] == 42


def test_structured_schema_and_validator() -> None:
    schema = StructuredSchema.from_json_schema(
        {
            "type": "object",
            "properties": {"answer": {"type": "number"}, "ok": {"type": "boolean"}},
            "required": ["answer"],
            "additionalProperties": False,
        }
    )
    valid, reason = validate_payload({"answer": 42, "ok": True}, schema)
    assert (valid, reason) == (True, "ok")

    invalid, reason = validate_payload({"ok": True}, schema)
    assert invalid is False
    assert "Missing required keys" in reason
