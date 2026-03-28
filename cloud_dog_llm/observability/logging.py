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

# cloud_dog_llm — Observability logging helpers
"""Structured logging helpers for request/response lifecycle events."""

from __future__ import annotations

from typing import Any

from cloud_dog_llm.security.redaction import redact_secrets


def build_log_payload(event: str, *, correlation_id: str, fields: dict[str, Any] | None = None) -> dict[str, Any]:
    """Build log payload."""
    payload = {
        "event": event,
        "correlation_id": correlation_id,
    }
    if fields:
        redacted = {k: redact_secrets(str(v)) if isinstance(v, str) else v for k, v in fields.items()}
        payload.update(redacted)
    return payload
