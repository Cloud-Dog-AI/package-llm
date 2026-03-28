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

import time
from typing import Any

from cloud_dog_llm.observability.redaction import redact_payload


def build_audit_event(event_type: str, correlation_id: str, payload: dict[str, Any]) -> dict[str, Any]:
    """Build audit event."""
    return {
        "event_type": event_type,
        "correlation_id": correlation_id,
        "timestamp": time.time(),
        "payload": redact_payload(payload),
    }
