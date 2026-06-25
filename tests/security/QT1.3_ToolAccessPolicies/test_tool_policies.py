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

from cloud_dog_llm.security.policies import GovernancePolicy
from cloud_dog_llm.tools.models import ToolCall, ToolDef
from cloud_dog_llm.tools.router import ToolRouter


@pytest.mark.asyncio
async def test_tool_access_policy_denies_restricted_tool() -> None:
    async def noop(_: dict[str, int]) -> dict[str, int]:
        return {"ok": 1}

    router = ToolRouter(policy=GovernancePolicy(denied_tools={"danger"}))
    router.register(ToolDef("danger", "danger", "danger", {"type": "object"}), noop)
    result = await router.route(ToolCall("danger", "danger", {}))
    assert result.success is False
    assert "policy" in result.error.lower()
