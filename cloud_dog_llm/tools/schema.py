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

# cloud_dog_llm — Tool schema helpers
"""Compatibility module for tool schema handling."""

from __future__ import annotations

from typing import Any

from cloud_dog_llm.tools.schemas import normalize_json_schema


def validate_arguments(schema: dict[str, Any], args: dict[str, Any]) -> tuple[bool, str]:
    """Validate arguments."""
    norm = normalize_json_schema(schema)
    required = norm.get("required", [])
    if isinstance(required, list):
        for key in required:
            if key not in args:
                return False, f"Missing required argument: {key}"
    properties = norm.get("properties", {})
    if isinstance(properties, dict):
        for key in args:
            if properties and key not in properties:
                return False, f"Unknown argument: {key}"
    return True, "ok"
