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

from cloud_dog_llm.runtime.cancel import is_cancelled
from cloud_dog_llm.runtime.cancellation import CancellationToken


@pytest.mark.asyncio
async def test_cancellation_token_transitions() -> None:
    tok = CancellationToken()
    assert tok.cancelled is False
    assert is_cancelled(tok) is False
    tok.cancel()
    await tok.wait_cancelled()
    assert tok.cancelled is True
    assert is_cancelled(tok) is True
