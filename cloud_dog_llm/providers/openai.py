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

# cloud_dog_llm — OpenAI provider adapter
"""First-party OpenAI adapter built on the OpenAI-compatible base adapter."""

from __future__ import annotations

from cloud_dog_llm.config.models import ProviderConfig
from cloud_dog_llm.providers.openai_compat import OpenAICompatAdapter


class OpenAIAdapter(OpenAICompatAdapter):
    """OpenAI adapter.

    This adapter keeps a dedicated module path for OpenAI while reusing the
    OpenAI-compatible transport implementation.
    """

    def __init__(self, config: ProviderConfig) -> None:
        super().__init__(config)
