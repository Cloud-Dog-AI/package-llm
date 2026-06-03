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

# cloud_dog_llm — Secret detection helpers
"""Secret detection and payload redaction utilities."""

from __future__ import annotations

from typing import Any

from cloud_dog_llm.security.redaction import redact_secrets


def contains_secret(value: str) -> bool:
    """Handle contains secret."""
    return redact_secrets(value) != value


def redact_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Handle redact payload."""
    redacted: dict[str, Any] = {}
    for key, value in payload.items():
        if isinstance(value, str):
            redacted[key] = redact_secrets(value)
        else:
            redacted[key] = value
    return redacted
