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

from cloud_dog_llm.tools.calling import parse_openai_tool_calls


def test_parse_openai_style_tool_call() -> None:
    message = {
        "tool_calls": [
            {"id": "c1", "function": {"name": "search", "arguments": '{"q":"abc"}'}},
        ]
    }
    calls = parse_openai_tool_calls(message)
    assert len(calls) == 1
    assert calls[0].name == "search"
    assert calls[0].arguments["q"] == "abc"
