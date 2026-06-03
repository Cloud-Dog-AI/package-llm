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

# cloud_dog_llm — Retry helpers
"""Bounded retries with exponential backoff and retryable code helpers."""

from __future__ import annotations

import asyncio
import random
from collections.abc import Awaitable, Callable
from typing import TypeVar

T = TypeVar("T")

RETRYABLE_STATUS_CODES = {502, 503, 504}


def is_retryable_status(status_code: int) -> bool:
    """Return whether retryable status."""
    return status_code in RETRYABLE_STATUS_CODES


async def with_retries(
    fn: Callable[[], Awaitable[T]],
    *,
    retries: int = 2,
    base_delay_seconds: float = 0.01,
) -> T:
    """Handle with retries."""
    attempt = 0
    while True:
        try:
            return await fn()
        except Exception:
            if attempt >= retries:
                raise
            delay = base_delay_seconds * (2**attempt) + random.uniform(0.0, base_delay_seconds)
            await asyncio.sleep(delay)
            attempt += 1
