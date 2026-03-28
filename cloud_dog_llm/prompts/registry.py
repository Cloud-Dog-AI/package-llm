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

# cloud_dog_llm — Prompt registry
"""In-memory prompt template registry with versioned keys."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class PromptTemplate:
    """Represent prompt template."""
    name: str
    version: str
    template: str


class PromptRegistry:
    """Represent prompt registry."""
    def __init__(self) -> None:
        self._templates: dict[tuple[str, str], PromptTemplate] = {}

    def register(self, name: str, version: str, template: str) -> None:
        """Handle register."""
        self._templates[(name, version)] = PromptTemplate(name=name, version=version, template=template)

    def get(self, name: str, version: str) -> PromptTemplate:
        """Handle get."""
        key = (name, version)
        if key not in self._templates:
            raise KeyError(f"Prompt not found: {name}@{version}")
        return self._templates[key]
