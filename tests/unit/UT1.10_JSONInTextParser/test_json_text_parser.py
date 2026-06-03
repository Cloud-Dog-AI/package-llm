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

from cloud_dog_llm.tools.calling import parse_json_tool_call
from cloud_dog_llm.tools.parser import ToolCallParser


def test_parse_json_tool_from_text() -> None:
    call = parse_json_tool_call('please run {"tool":"lookup","arguments":{"id":7}} now')
    assert call is not None
    assert call.name == "lookup"
    assert call.arguments["id"] == 7


def test_parser_wrapper_openai_message() -> None:
    wrapped = ToolCallParser.from_openai_message(
        {"tool_calls": [{"id": "t1", "function": {"name": "sum", "arguments": '{"a":1}'}}]}
    )
    assert len(wrapped) == 1
    assert wrapped[0].name == "sum"
    assert wrapped[0].arguments["a"] == 1
