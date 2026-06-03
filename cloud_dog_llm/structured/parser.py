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

# cloud_dog_llm — Structured parser
"""Structured payload parser with strict/lenient modes."""

from __future__ import annotations

from typing import Any

from cloud_dog_llm.structured.extractor import extract_json


def parse_structured_payload(text: str, *, strict: bool = False) -> dict[str, Any] | None:
    """Parse structured payload."""
    payload = extract_json(text)
    if payload is not None:
        return payload
    if strict:
        raise ValueError("No structured JSON payload found")
    return None
