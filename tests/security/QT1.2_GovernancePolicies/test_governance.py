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

import pytest

from cloud_dog_llm.security.governance import enforce_request
from cloud_dog_llm.security.policies import GovernancePolicy
from cloud_dog_llm.security.rbac import RBACPolicy


def test_governance_provider_and_prompt_limits() -> None:
    policy = GovernancePolicy(allowed_providers={"ollama"}, max_prompt_chars=8)
    assert policy.provider_allowed("ollama") is True
    assert policy.provider_allowed("openai") is False
    assert policy.validate_prompt("12345678") is True
    assert policy.validate_prompt("123456789") is False


def test_governance_enforcement_raises_on_invalid_request() -> None:
    policy = GovernancePolicy(allowed_providers={"ollama"}, max_prompt_chars=4, max_output_tokens=8)
    enforce_request(policy, provider_id="ollama", prompt="ok", max_tokens=4)
    with pytest.raises(ValueError):
        enforce_request(policy, provider_id="openrouter", prompt="ok", max_tokens=4)
    with pytest.raises(ValueError):
        enforce_request(policy, provider_id="ollama", prompt="12345", max_tokens=4)
    with pytest.raises(ValueError):
        enforce_request(policy, provider_id="ollama", prompt="ok", max_tokens=9)


def test_rbac_policy_allows_expected_entities() -> None:
    policy = RBACPolicy(
        role_tools={"admin": {"tool.search"}},
        role_providers={"admin": {"ollama"}},
    )
    assert policy.can_use_tool("admin", "tool.search") is True
    assert policy.can_use_tool("admin", "tool.write") is False
    assert policy.can_use_provider("admin", "ollama") is True
    assert policy.can_use_provider("admin", "openrouter") is False
