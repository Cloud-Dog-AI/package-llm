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

# cloud_dog_llm - Agentic prompt templates
"""Prompt templates for PS-96 CodeAct and Reflexion support."""

from __future__ import annotations

import json
from typing import Any

from cloud_dog_llm.prompts.registry import PromptRegistry
from cloud_dog_llm.prompts.render import RenderedPrompt, render_template

CODE_EMISSION_PROMPT_NAME = "agentic.code_emission"
REFLECTION_PROMPT_NAME = "agentic.reflection"
AGENTIC_PROMPT_VERSION = "1.0"

CODE_EMISSION_PROMPT_TEMPLATE = """You are preparing one CodeAct step for a sandboxed code-runner.
Task:
{{ task }}

Runtime: {{ runtime }}

Available MCP tools as JSON descriptors:
{{ available_tools_json }}

Sandbox constraints:
{% if constraints -%}
{% for constraint in constraints %}- {{ constraint }}
{% endfor -%}
{% else -%}
- No additional constraints supplied.
{% endif %}

Prior observations:
{% if observations -%}
{% for observation in observations %}- {{ observation }}
{% endfor -%}
{% else -%}
- No prior observations.
{% endif %}

Return exactly one JSON object. Choose one action only:
{"thought":"why this action is next","runtime":"{{ runtime }}","code":"code to run or null","tool_call":null,"final_answer":null}

Rules:
- Emit code only; do not claim to have executed it.
- Use the configured code-runner for execution.
- If a structured MCP tool is more appropriate, put an MCP tools/call params object in tool_call.
- If the task is complete, set final_answer and leave code and tool_call null.
"""

REFLECTION_PROMPT_TEMPLATE = """Review the prior agent attempt and produce a bounded self-critique.
Original task:
{{ task }}

Attempt:
{{ attempt }}

Observed result:
{{ result }}

Evaluation criteria:
{% if criteria -%}
{% for item in criteria %}- {{ item }}
{% endfor -%}
{% else -%}
- Correctness
- Completeness
- Safety
{% endif %}

Return exactly one JSON object with this shape:
{"is_satisfactory":false,"issues":["issue"],"improvements":["next change"],"revised_instruction":"concise next instruction"}

Limit issues and improvements to {{ max_findings }} items each. Do not re-run tools or code in this reflection.
"""


def _json_for_prompt(value: Any) -> str:
    """Return stable JSON text for prompt insertion."""
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"))


def render_code_emission_prompt(
    *,
    task: str,
    runtime: str = "python",
    available_tools: list[dict[str, Any]] | None = None,
    constraints: list[str] | None = None,
    observations: list[str] | None = None,
) -> RenderedPrompt:
    """Render the PS-96 CodeAct code-emission prompt."""
    return render_template(
        CODE_EMISSION_PROMPT_TEMPLATE,
        {
            "task": task,
            "runtime": runtime,
            "available_tools_json": _json_for_prompt(available_tools or []),
            "constraints": list(constraints or []),
            "observations": list(observations or []),
        },
    )


def render_reflection_prompt(
    *,
    task: str,
    attempt: str,
    result: str,
    criteria: list[str] | None = None,
    max_findings: int = 5,
) -> RenderedPrompt:
    """Render the PS-96 Reflexion self-critique prompt."""
    return render_template(
        REFLECTION_PROMPT_TEMPLATE,
        {
            "task": task,
            "attempt": attempt,
            "result": result,
            "criteria": list(criteria or []),
            "max_findings": max_findings,
        },
    )


def register_agentic_prompt_templates(registry: PromptRegistry) -> None:
    """Register built-in PS-96 agentic prompt templates."""
    registry.register(CODE_EMISSION_PROMPT_NAME, AGENTIC_PROMPT_VERSION, CODE_EMISSION_PROMPT_TEMPLATE)
    registry.register(REFLECTION_PROMPT_NAME, AGENTIC_PROMPT_VERSION, REFLECTION_PROMPT_TEMPLATE)
