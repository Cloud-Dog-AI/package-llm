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

import pytest

from cloud_dog_llm.runtime.retry import RetryPolicy, run_with_retry
from cloud_dog_llm.runtime.retries import is_retryable_status, with_retries


@pytest.mark.asyncio
async def test_with_retries_eventually_succeeds() -> None:
    attempts = {"n": 0}

    async def flaky() -> str:
        attempts["n"] += 1
        if attempts["n"] < 3:
            raise RuntimeError("retry")
        return "ok"

    out = await with_retries(flaky, retries=3, base_delay_seconds=0.0)
    assert out == "ok"
    assert is_retryable_status(503) is True


@pytest.mark.asyncio
async def test_retry_compatibility_policy_wrapper() -> None:
    attempts = {"n": 0}

    async def flaky() -> str:
        attempts["n"] += 1
        if attempts["n"] < 2:
            raise RuntimeError("retry")
        return "ok"

    policy = RetryPolicy(retries=1, base_delay_seconds=0.0)
    out = await run_with_retry(flaky, policy)
    assert out == "ok"
