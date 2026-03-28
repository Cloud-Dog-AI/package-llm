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

from cloud_dog_llm.security.policies import GovernancePolicy


def enforce_request(policy: GovernancePolicy, *, provider_id: str, prompt: str, max_tokens: int | None) -> None:
    """Handle enforce request."""
    if not policy.provider_allowed(provider_id):
        raise ValueError(f"Provider not allowed: {provider_id}")
    if not policy.validate_prompt(prompt):
        raise ValueError("Prompt exceeds governance max_prompt_chars")
    if max_tokens is not None and max_tokens > policy.max_output_tokens:
        raise ValueError("Requested max_tokens exceeds governance max_output_tokens")


__all__ = ["GovernancePolicy", "enforce_request"]
