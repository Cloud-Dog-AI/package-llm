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

import json
from pathlib import Path

import pytest

from cloud_dog_llm.config import select_code_generation_model
from cloud_dog_llm.domain.enums import ExecutionMode
from cloud_dog_llm.prompts import (
    CODE_EMISSION_PROMPT_NAME,
    REFLECTION_PROMPT_NAME,
    PromptRegistry,
    register_agentic_prompt_templates,
    render_code_emission_prompt,
    render_reflection_prompt,
)
from cloud_dog_llm.tools import (
    build_mcp_tools_call,
    mcp_tools_call_jsonrpc_schema,
    parse_mcp_tools_call,
    tool_def_to_mcp_tool,
    validate_mcp_tools_call,
)
from cloud_dog_llm.tools.models import ToolDef


def test_mcp_tools_call_payload_matches_mcp_shape() -> None:
    payload = build_mcp_tools_call("search", {"q": "agentic"}, request_id="req-1")

    assert payload == {
        "id": "req-1",
        "method": "tools/call",
        "params": {"name": "search", "arguments": {"q": "agentic"}},
    }
    json.dumps(payload)
    assert validate_mcp_tools_call(payload) == (True, "ok")

    parsed = parse_mcp_tools_call(payload)
    assert parsed.name == "search"
    assert parsed.arguments == {"q": "agentic"}


def test_mcp_tools_schema_and_tool_descriptor_are_valid_objects() -> None:
    schema = mcp_tools_call_jsonrpc_schema()
    assert schema["properties"]["method"]["const"] == "tools/call"
    assert schema["properties"]["params"]["required"] == ["name"]

    tool = ToolDef(
        tool_id="search",
        name="search",
        description="Search indexed documents",
        input_schema={"properties": {"q": {"type": "string"}}, "required": ["q"]},
        execution_mode=ExecutionMode.MCP,
    )
    descriptor = tool_def_to_mcp_tool(tool)
    assert descriptor["name"] == "search"
    assert descriptor["inputSchema"]["type"] == "object"
    assert descriptor["inputSchema"]["required"] == ["q"]


def test_agentic_prompt_templates_render_deterministically() -> None:
    tools = [{"name": "search", "inputSchema": {"type": "object"}}]
    first = render_code_emission_prompt(
        task="Summarise the latest indexed notes",
        runtime="python",
        available_tools=tools,
        constraints=["no network"],
        observations=["search returned 3 documents"],
    )
    second = render_code_emission_prompt(
        task="Summarise the latest indexed notes",
        runtime="python",
        available_tools=tools,
        constraints=["no network"],
        observations=["search returned 3 documents"],
    )

    assert first.sha256 == second.sha256
    assert "Runtime: python" in first.text
    assert '"name":"search"' in first.text
    assert "Emit code only" in first.text


def test_reflection_prompt_and_registry_templates() -> None:
    registry = PromptRegistry()
    register_agentic_prompt_templates(registry)

    assert registry.get(CODE_EMISSION_PROMPT_NAME, "1.0").name == CODE_EMISSION_PROMPT_NAME
    assert registry.get(REFLECTION_PROMPT_NAME, "1.0").name == REFLECTION_PROMPT_NAME

    rendered = render_reflection_prompt(
        task="Answer the user",
        attempt="The agent returned a partial answer",
        result="Missing citations",
        criteria=["must cite evidence"],
        max_findings=3,
    )
    assert "Missing citations" in rendered.text
    assert '"is_satisfactory":false' in rendered.text
    assert "Limit issues and improvements to 3 items" in rendered.text


def test_code_generation_model_selection_prefers_config_then_caller() -> None:
    config = {
        "models": {
            "code_generation_default": {"model": "deepseek/deepseek-v3.2", "provider": "openrouter"},
            "code_generation_chat_client": {"model": "qwen/qwen3-coder", "provider_id": "openai"},
        }
    }

    service_choice = select_code_generation_model(
        config,
        caller_model="qwen3:14b",
        caller_provider_id="ollama",
        service_name="chat-client",
    )
    assert service_choice.model == "qwen/qwen3-coder"
    assert service_choice.provider_id == "openai"
    assert service_choice.config_key == "models.code_generation_chat_client"

    default_choice = select_code_generation_model(
        config,
        caller_model="qwen3:14b",
        caller_provider_id="ollama",
        service_name="sql-agent",
    )
    assert default_choice.model == "deepseek/deepseek-v3.2"
    assert default_choice.provider_id == "openrouter"

    caller_choice = select_code_generation_model({}, caller_model="qwen3:14b", caller_provider_id="ollama")
    assert caller_choice.model == "qwen3:14b"
    assert caller_choice.provider_id == "ollama"
    assert caller_choice.source == "caller"

    with pytest.raises(ValueError):
        select_code_generation_model({}, caller_model=None)


def test_agentic_extensions_do_not_add_direct_llm_bypass_paths() -> None:
    package_root = Path(__file__).resolve().parents[3] / "cloud_dog_llm"
    targets = [
        package_root / "config" / "code_generation.py",
        package_root / "prompts" / "agentic.py",
        package_root / "tools" / "mcp_calls.py",
    ]
    forbidden = [
        "import httpx",
        "from httpx",
        "import requests",
        "from requests",
        "requests.",
        "os.environ",
        "os.getenv",
        "import hvac",
        "from hvac",
    ]

    for target in targets:
        text = target.read_text(encoding="utf-8")
        hits = [token for token in forbidden if token in text]
        assert hits == [], f"{target} contains bypass tokens: {hits}"
