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

from cloud_dog_llm.providers.base import ProviderAdapter
from cloud_dog_llm.providers.registry import ProviderRegistry
from cloud_dog_llm.registry.capabilities import CapabilityDescriptor


class _Dummy(ProviderAdapter):
    async def invoke(self, request):
        return None

    async def invoke_stream(self, request):
        if False:
            yield None

    async def health(self) -> bool:
        return True

    def capabilities(self) -> CapabilityDescriptor:
        return CapabilityDescriptor(provider_id="dummy", model_id="m")


def test_registry_register_get_list() -> None:
    r = ProviderRegistry()
    r.register("x", _Dummy())
    assert r.has("x")
    assert r.list_ids() == ["x"]


def test_registry_missing_raises() -> None:
    r = ProviderRegistry()
    with pytest.raises(KeyError):
        r.get("missing")
