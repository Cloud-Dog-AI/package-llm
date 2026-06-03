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

# cloud_dog_llm — Secret/content redaction
"""Redaction hooks for logs and diagnostics."""

from __future__ import annotations

import re

_SECRET_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9_-]{8,}"),
    re.compile(r"Bearer\s+[A-Za-z0-9._-]{8,}", flags=re.IGNORECASE),
    re.compile(r"(api[_-]?key\s*[=:]\s*)[^\s,;]+", flags=re.IGNORECASE),
]


def redact_secrets(text: str) -> str:
    """Handle redact secrets."""
    out = text
    for pattern in _SECRET_PATTERNS:
        out = pattern.sub(lambda m: f"{m.group(1)}***" if m.lastindex else "***", out)
    return out
