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

# cloud_dog_llm — Domain formatter compatibility adapter
"""Wrap domain formatter callables as PromptTemplate-compatible objects."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from cloud_dog_llm.prompts.registry import PromptTemplate
from cloud_dog_llm.prompts.render import render_template


@dataclass(frozen=True, slots=True)
class _CompatRef:
    key: str


class FormatterCompatibilityAdapter:
    """Bridges function-based formatters with PromptTemplate flows."""

    def __init__(self) -> None:
        self._formatters: dict[str, Callable[[dict[str, Any]], str]] = {}

    def wrap(
        self,
        *,
        name: str,
        version: str,
        formatter: Callable[[dict[str, Any]], str],
    ) -> PromptTemplate:
        """Handle wrap."""
        key = f"{name}@{version}"
        self._formatters[key] = formatter
        return PromptTemplate(name=name, version=version, template=f"{{{{compat:{key}}}}}")

    def render(self, template: PromptTemplate, variables: dict[str, Any]) -> str:
        """Handle render."""
        marker = "{{compat:"
        if template.template.startswith(marker) and template.template.endswith("}}"):
            key = template.template[len(marker) : -2]
            formatter = self._formatters.get(key)
            if formatter is None:
                raise KeyError(f"Formatter not registered: {key}")
            return formatter(variables)
        return render_template(template.template, variables).text

    def render_chain(self, templates: list[PromptTemplate], variables: dict[str, Any]) -> list[str]:
        """Handle render chain."""
        return [self.render(template, variables) for template in templates]
