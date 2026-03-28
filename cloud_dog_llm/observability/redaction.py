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

from __future__ import annotations

from cloud_dog_llm.security.redaction import redact_secrets


def redact_payload(payload: dict) -> dict:
    """Handle redact payload."""
    out: dict = {}
    for key, value in payload.items():
        if isinstance(value, str):
            out[key] = redact_secrets(value)
        elif isinstance(value, dict):
            out[key] = redact_payload(value)
        elif isinstance(value, list):
            out[key] = [
                redact_payload(v) if isinstance(v, dict) else redact_secrets(v) if isinstance(v, str) else v
                for v in value
            ]
        else:
            out[key] = value
    return out


__all__ = ["redact_secrets", "redact_payload"]
