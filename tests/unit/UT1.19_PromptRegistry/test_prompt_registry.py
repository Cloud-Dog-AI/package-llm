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

from cloud_dog_llm.prompts.registry import PromptRegistry


def test_prompt_registry_register_and_get() -> None:
    reg = PromptRegistry()
    reg.register("sys", "1", "hello")
    tpl = reg.get("sys", "1")
    assert tpl.template == "hello"


def test_prompt_registry_missing() -> None:
    reg = PromptRegistry()
    with pytest.raises(KeyError):
        reg.get("x", "1")
