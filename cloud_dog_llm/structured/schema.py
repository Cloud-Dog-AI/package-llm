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

# cloud_dog_llm — Structured schema model
"""Schema helpers for structured-output validation."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class StructuredSchema:
    """Minimal schema model used by structured validator helpers."""

    required: set[str] = field(default_factory=set)
    optional: set[str] = field(default_factory=set)
    allow_extra_keys: bool = False

    @classmethod
    def from_json_schema(cls, schema: dict) -> "StructuredSchema":
        """Handle from json schema."""
        properties = schema.get("properties", {}) if isinstance(schema, dict) else {}
        required_raw = schema.get("required", []) if isinstance(schema, dict) else []
        keys = set(properties.keys()) if isinstance(properties, dict) else set()
        required = {k for k in required_raw if isinstance(k, str)}
        optional = keys - required
        allow_extra = bool(schema.get("additionalProperties", False)) if isinstance(schema, dict) else False
        return cls(required=required, optional=optional, allow_extra_keys=allow_extra)


__all__ = ["StructuredSchema"]
