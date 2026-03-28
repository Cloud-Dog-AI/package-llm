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

# cloud_dog_llm — Prompt rendering
"""Deterministic Jinja2 prompt rendering helpers."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any

from jinja2 import Environment, StrictUndefined


@dataclass(frozen=True, slots=True)
class RenderedPrompt:
    """Represent rendered prompt."""
    text: str
    sha256: str


def render_template(template: str, variables: dict[str, Any]) -> RenderedPrompt:
    """Handle render template."""
    env = Environment(undefined=StrictUndefined, autoescape=False, trim_blocks=True, lstrip_blocks=True)
    text = env.from_string(template).render(**variables)
    digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return RenderedPrompt(text=text, sha256=digest)
