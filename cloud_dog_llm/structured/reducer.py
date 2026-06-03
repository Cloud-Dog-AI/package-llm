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

from typing import Any


def reduce_structured_payload(payload: dict[str, Any], *, max_chars: int = 4096) -> dict[str, Any]:
    """Handle reduce structured payload."""
    out: dict[str, Any] = {}
    for key, value in payload.items():
        if isinstance(value, str) and len(value) > max_chars:
            out[key] = value[:max_chars]
        else:
            out[key] = value
    return out
