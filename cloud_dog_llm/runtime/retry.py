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

# cloud_dog_llm — Retry compatibility module
"""Compatibility wrapper with explicit retry policy support."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TypeVar

from cloud_dog_llm.runtime.retries import is_retryable_status, with_retries

T = TypeVar("T")


@dataclass(frozen=True, slots=True)
class RetryPolicy:
    """Policy configuration used by callers that import runtime.retry."""

    retries: int = 2
    base_delay_seconds: float = 0.01


async def run_with_retry(fn, policy: RetryPolicy | None = None) -> T:
    """Run with retry."""
    active = policy or RetryPolicy()
    return await with_retries(
        fn,
        retries=active.retries,
        base_delay_seconds=active.base_delay_seconds,
    )


__all__ = ["RetryPolicy", "is_retryable_status", "run_with_retry"]
