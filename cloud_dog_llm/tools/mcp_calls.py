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

# cloud_dog_llm - MCP tool-call helpers
"""Structured helpers for MCP ``tools/call`` payloads."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from cloud_dog_llm.tools.models import ToolCall, ToolDef
from cloud_dog_llm.tools.schemas import normalize_json_schema

MCP_TOOLS_CALL_METHOD = "tools/call"


@dataclass(frozen=True, slots=True)
class MCPToolsCall:
    """Represent an MCP ``tools/call`` request."""

    name: str
    arguments: dict[str, Any] = field(default_factory=dict)
    request_id: str | int | None = None
    meta: dict[str, Any] = field(default_factory=dict)

    def to_json_rpc(self) -> dict[str, Any]:
        """Return a JSON-RPC request matching MCP ``tools/call``."""
        payload: dict[str, Any] = {
            "method": MCP_TOOLS_CALL_METHOD,
            "params": {
                "name": self.name,
                "arguments": dict(self.arguments),
            },
        }
        if self.request_id is not None:
            payload["id"] = self.request_id
        if self.meta:
            payload["params"]["_meta"] = dict(self.meta)
        return payload

    def to_tool_call(self) -> ToolCall:
        """Convert to the package-neutral ``ToolCall`` model."""
        return ToolCall(tool_id=self.name, name=self.name, arguments=dict(self.arguments))


def build_mcp_tools_call(
    name: str,
    arguments: dict[str, Any] | None = None,
    *,
    request_id: str | int | None = None,
    meta: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a JSON-RPC MCP ``tools/call`` request."""
    return MCPToolsCall(
        name=name,
        arguments=dict(arguments or {}),
        request_id=request_id,
        meta=dict(meta or {}),
    ).to_json_rpc()


def parse_mcp_tools_call(payload: dict[str, Any]) -> ToolCall:
    """Parse an MCP ``tools/call`` JSON-RPC request or params object."""
    if not isinstance(payload, dict):
        raise ValueError("MCP tools/call payload must be an object")

    if "params" in payload:
        method = payload.get("method")
        if method != MCP_TOOLS_CALL_METHOD:
            raise ValueError(f"Expected MCP method {MCP_TOOLS_CALL_METHOD!r}")
        params = payload.get("params")
    else:
        params = payload

    if not isinstance(params, dict):
        raise ValueError("MCP tools/call params must be an object")

    name = params.get("name")
    if not isinstance(name, str) or not name.strip():
        raise ValueError("MCP tools/call params.name must be a non-empty string")

    arguments = params.get("arguments", {})
    if arguments is None:
        arguments = {}
    if not isinstance(arguments, dict):
        raise ValueError("MCP tools/call params.arguments must be an object")

    return ToolCall(tool_id=name, name=name, arguments=dict(arguments))


def validate_mcp_tools_call(payload: dict[str, Any]) -> tuple[bool, str]:
    """Validate an MCP ``tools/call`` payload without raising."""
    try:
        parse_mcp_tools_call(payload)
    except ValueError as exc:
        return False, str(exc)
    return True, "ok"


def mcp_tools_call_params_schema() -> dict[str, Any]:
    """Return the JSON Schema for MCP ``tools/call`` params."""
    return {
        "type": "object",
        "additionalProperties": False,
        "required": ["name"],
        "properties": {
            "name": {"type": "string", "minLength": 1},
            "arguments": {"type": "object", "additionalProperties": True},
            "_meta": {"type": "object", "additionalProperties": True},
        },
    }


def mcp_tools_call_jsonrpc_schema() -> dict[str, Any]:
    """Return the JSON Schema for a JSON-RPC MCP ``tools/call`` request."""
    return {
        "type": "object",
        "additionalProperties": False,
        "required": ["method", "params"],
        "properties": {
            "jsonrpc": {"type": "string"},
            "id": {"type": ["string", "integer", "null"]},
            "method": {"const": MCP_TOOLS_CALL_METHOD},
            "params": mcp_tools_call_params_schema(),
        },
    }


def tool_def_to_mcp_tool(tool: ToolDef) -> dict[str, Any]:
    """Convert a ``ToolDef`` to an MCP ``tools/list`` descriptor."""
    return {
        "name": tool.name,
        "description": tool.description,
        "inputSchema": normalize_json_schema(tool.input_schema),
    }


def tool_defs_to_mcp_tools(tools: list[ToolDef]) -> list[dict[str, Any]]:
    """Convert ``ToolDef`` values to MCP ``tools/list`` descriptors."""
    return [tool_def_to_mcp_tool(tool) for tool in tools]
