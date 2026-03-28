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

# cloud_dog_llm — tools package

from cloud_dog_llm.tools.calling import parse_json_tool_call, parse_openai_tool_calls
from cloud_dog_llm.tools.executor import ToolExecutor
from cloud_dog_llm.tools.local import LocalToolRegistry
from cloud_dog_llm.tools.models import ToolCall, ToolDef, ToolResult
from cloud_dog_llm.tools.pipeline import ToolPipeline
from cloud_dog_llm.tools.schemas import normalize_json_schema
from cloud_dog_llm.tools.reducer import reduce_output
from cloud_dog_llm.tools.router import ToolRouter

__all__ = [
    "ToolCall",
    "ToolDef",
    "ToolResult",
    "ToolPipeline",
    "ToolExecutor",
    "ToolRouter",
    "LocalToolRegistry",
    "parse_json_tool_call",
    "parse_openai_tool_calls",
    "normalize_json_schema",
    "reduce_output",
]
